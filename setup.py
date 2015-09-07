from setuptools import setup

# Replace the place holders with values for your project

setup(

    # Do not use underscores in the plugin name.
    name='vnfmplugin',

    version='0.1',
    author='esumdaw',
    author_email='esumdaw@ericsson.com',
    description='vnfm workflow Plugin',
    packages=['main','main.workflows'], 
    install_requires=['cloudify-plugins-common==3.1']    
)