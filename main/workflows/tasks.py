# ctx is imported and used in operations
from cloudify import ctx

# put the operation decorator on any function that is a task
from cloudify.decorators import operation
import requests
import json
import time
import ConfigParser
import StringIO

@operation
def startwf(**kwargs):
	config = ConfigParser.ConfigParser()
	buf = StringIO.StringIO(ctx.get_resource('orchestration.cfg'))
	config.readfp(buf)
	ctx.send_event(' -----node name-----> ' + ctx.node.name)
	VDC_NAME = ctx.node.properties[ctx.node.name]
	
	host = ctx.node.properties['host']
	definitionName = config.get(ctx.node.name,'definitionName')
	payload = config.get(ctx.node.name,'payload')
	payload = payload.replace("$VDC_NAME",VDC_NAME)

	ctx.send_event('running commissioning workflow -- host: ' + host + '   definition: ' + definitionName + '   vDC name: ' + VDC_NAME)
	# runwf(host, definitionName, payload)

@operation
def stopwf(**kwargs):
	config = ConfigParser.ConfigParser()
	buf = StringIO.StringIO(ctx.get_resource('orchestration.cfg'))
	config.readfp(buf)
	ctx.send_event(' -----node name-----> ' + ctx.node.name)
	VDC_NAME = ctx.node.properties[ctx.node.name]
	
	host = ctx.node.properties['host']
	definitionName = config.get('DECOMMISSION','definitionName')
	payload = config.get('DECOMMISSION','payload')
	payload = payload.replace("$VDC_NAME",VDC_NAME)

	ctx.send_event('running commissioning workflow -- host: ' + host + '   definition: ' + definitionName + '   vDC name: ' + VDC_NAME)
	# runwf(host, definitionName, payload)

def runwf(host, definitionName, payload):
	try:
		definitionsURL = host+'/workflowservice-ext/rest/nfv_resource/process-definition-ext?latest=true&sortBy=name&sortOrder=asc'

		response = requests.get(definitionsURL)

		resValue = json.loads(response.text)

		definitionId = ''

		for x in resValue:
			if x.get('name').strip() == definitionName:
				definitionId=x.get('id')
				ctx.logger.info('found the id: '+ definitionId +' for requested definition: '+ definitionName)

		#### start
		startURL = host+'/engine-rest/engine/default/process-definition/'+definitionId+'/start'

		headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

		response = requests.post(startURL, headers=headers, data=payload)
		ctx.logger.info('RESPONSE for start: '+ response.text)

		resValue = json.loads(response.text)

		instanceID = resValue.get('id')

		ctx.logger.info('instance id obtained for triggered instance: '+ instanceID)

		#### progress
		progressURL = host+'/workflowservice-ext/rest/progress-service/process-instance/status/'+instanceID
		
		historyURL = host+'/engine-rest/engine/default/history/process-instance?processDefinitionId='+definitionId

		progress = 0
		
		while True:
			
			response = requests.get(progressURL, headers=headers)

			resValue = json.loads(response.text)

			progress = resValue.get('progressPercentage')

			if progress is not None:
				ctx.logger.info('----- progress ----- ' + progress + '%')
			else:
				response = requests.get(historyURL, headers=headers)
				resValue = json.loads(response.text)
				for x in resValue:
					if x.get('id') == instanceID:
						ctx.logger.info('----- progress ----- 100% End Time: '+ x.get('endTime'))					
				break

			time.sleep(30)
	except Exception as e:
		ctx.logger.info('Something went wrong! Exiting script... Error-' + e)

	return

def generatePayload():
	i=config.items('VARS-EPG')
    d=dict(i)
#     print(d)
    y={}
    z={}
    for i in d.keys():
        x={}
        x['value']=d.get(i)
        y[i]=x
    
#     print(y)
    z['variables']=y
#     print(z)
    payload = json.dumps(z)
    print(payload)