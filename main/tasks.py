# ctx is imported and used in operations
from cloudify import ctx

# put the operation decorator on any function that is a task
from cloudify.decorators import operation


@operation
def my_task(**kwargs):
    ctx.logger.info('----------------invoking my_task in vnfmplugin-----------------------')
    
