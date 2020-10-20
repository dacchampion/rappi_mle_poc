# rappi_prj/00-upload-data.py
import argparse
import os

from azureml.data.datapath import DataPath
from azureml.core import Dataset, Workspace
from azureml.exceptions import UserErrorException

TITANIC_DS_PATH = 'datasets/titanic'

if __name__ == "__main__":
    parser = argparse.ArgumentParser("data")
    parser.add_argument("--dataset_path", type=str, help="Local dataset path to be registered", required=True)
    args = parser.parse_args()

    ws = Workspace.from_config()
    # Getting the default datastore
    def_data_store = ws.get_default_datastore()

    version = 1
    try:
        titanic_ds = Dataset.get_by_name(workspace=ws, name='titanic_data')
        version = titanic_ds.version + 1
    except UserErrorException:
        pass

    train_file = os.path.basename(args.dataset_path)
    train_file_dir = os.path.dirname(args.dataset_path)
    azure_ds_path = f'{TITANIC_DS_PATH}/v{version}'
    def_data_store.upload(src_dir=train_file_dir, target_path=azure_ds_path, overwrite=True)

    titanic_ds = Dataset.Tabular.from_delimited_files(DataPath(def_data_store, f'{azure_ds_path}/{train_file}'))
    titanic_ds = titanic_ds.register(ws, 'titanic_data', create_new_version=True)
