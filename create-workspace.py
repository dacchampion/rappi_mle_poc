# rappi_prj/create-workspace.py
from azureml.core import Workspace

ws = Workspace.create(name='rappi_ws',
                      subscription_id='ed50c052-d031-4623-9383-148aa05a57ef',
                      resource_group='rappi_rg',
                      create_resource_group=True,
                      location='eastus2')

# write out the workspace details to a configuration file: .azureml/config.json
ws.write_config(path='.azureml')