import argparse
import json

from azureml.core import Datastore, Workspace
from azureml.data import dataset_type_definitions
from azureml.core.dataset import Dataset
from azureml.core.environment import Environment
from azureml.core.model import InferenceConfig, Model

PROFILING_DATA = "sample_request_data"

if __name__ == "__main__":
    parser = argparse.ArgumentParser("deployment")
    parser.add_argument("--model_id", type=str, help="Model identifier in Azure ML")
    parser.add_argument("--entry_script", type=str, help="Inference script path")
    parser.add_argument("--profile_name", type=str, help="Profile name for the model")
    args = parser.parse_args()

    input_json = {'data': [
        [17, 0, 1, 53.1000, 0, 0, 1, 1, 0, 1, 0, 0],
        [23, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1]]}

    # create a string that can be utf-8 encoded and
    # put in the body of the request
    serialized_input_json = json.dumps(input_json)
    dataset_content = []
    for i in range(100):
        dataset_content.append(serialized_input_json)
    dataset_content = '\n'.join(dataset_content)

    file_name = f'{PROFILING_DATA}.txt'
    with open(file_name, 'w') as f:
        f.write(dataset_content)

    # upload the txt file created above to the Datastore and create a dataset from it
    ws = Workspace.from_config()
    data_store = Datastore.get_default(ws)
    data_store.upload_files(['./' + file_name], target_path=PROFILING_DATA)
    datastore_path = [(data_store, PROFILING_DATA + '/' + file_name)]
    sample_request_data = Dataset.Tabular.from_delimited_files(
        datastore_path, separator='\n',
        infer_column_types=True,
        header=dataset_type_definitions.PromoteHeadersBehavior.NO_HEADERS)
    sample_request_data = sample_request_data.register(workspace=ws,
                                                       name=PROFILING_DATA,
                                                       create_new_version=True)

    model = Model(ws, id=args.model_id)
    env = Environment.from_conda_specification(name='rappi-ml-challenge', file_path='.azureml/deploy_env.yml')
    inference_config = InferenceConfig(entry_script=args.entry_script, environment=env)

    input_dataset = Dataset.get_by_name(workspace=ws, name=PROFILING_DATA)
    profile = Model.profile(ws, args.profile_name, [model], inference_config, input_dataset=input_dataset)

    profile.wait_for_completion(True)

    details = profile.get_details()

    print(details)
