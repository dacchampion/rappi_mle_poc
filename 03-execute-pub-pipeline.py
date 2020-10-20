import requests

from azureml.core import Workspace
from azureml.core.authentication import InteractiveLoginAuthentication
from azureml.pipeline.core import PublishedPipeline

interactive_auth = InteractiveLoginAuthentication()
auth_header = interactive_auth.get_authentication_header()

ws = Workspace.from_config()
pub_titanic_models = PublishedPipeline.get(ws, id="3cc312db-fa33-4e05-bdc8-de7fa471b7d8")

rest_endpoint = pub_titanic_models.endpoint
response = requests.post(rest_endpoint,
                         headers=auth_header,
                         json={"ExperimentName": "Titanic_models_exp",
                               "ParameterAssignments": {}})
print(response)
