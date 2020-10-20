import argparse

from azureml.core import Workspace
from azureml.core.environment import Environment
from azureml.core.model import InferenceConfig, Model

if __name__ == "__main__":
    parser = argparse.ArgumentParser("deployment")
    parser.add_argument("--model_id", type=str, help="Model identifier in Azure ML")
    parser.add_argument("--entry_script", type=str, help="Inference script path")
    args = parser.parse_args()

    ws = Workspace.from_config()
    model = Model(ws, id=args.model_id)
    env = Environment.from_conda_specification(name='rappi-ml-challenge', file_path='.azureml/deploy_env.yml')
    inference_config = InferenceConfig(entry_script=args.entry_script, environment=env)

    package = Model.package(ws, [model], inference_config, generate_dockerfile=True)
    package.wait_for_creation(show_output=True)
    # Download the package.
    package.save("./titanic_container")
    # Get the Azure container registry that the model/Dockerfile uses.
    acr = package.get_container_registry()
    print("Address:", acr.address)
    print("Username:", acr.username)
    print("Password:", acr.password)
