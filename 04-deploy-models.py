import argparse

from azureml.core import Workspace
from azureml.core.environment import Environment
from azureml.core.model import InferenceConfig, Model
from azureml.core.webservice import AciWebservice

if __name__ == "__main__":
    parser = argparse.ArgumentParser("deployment")
    parser.add_argument("--entry_script", type=str, help="Inference script path")
    parser.add_argument("--model_name", type=str, help="Registered model name")
    parser.add_argument("--pub_service_name", type=str, help="Service name to publish")
    args = parser.parse_args()

    ws = Workspace.from_config()

    env = Environment.from_conda_specification(name='rappi-ml-challenge', file_path='.azureml/deploy_env.yml')

    inference_config = InferenceConfig(entry_script=args.entry_script, environment=env)

    # deployment_config = LocalWebservice.deploy_configuration(port=8890)
    deployment_config = AciWebservice.deploy_configuration(cpu_cores=1,
                                                           memory_gb=1,
                                                           description=f"{args.model_name} wrapper service",
                                                           enable_app_insights=True)

    model = Model(ws, args.model_name)
    service = Model.deploy(ws, args.pub_service_name, [model], inference_config, deployment_config)
    service.wait_for_deployment(show_output=True)
    print(service.state)
