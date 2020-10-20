# rappi_prj/preprocess.py
import argparse
import logging
import os
import pandas as pd

from azureml.core import Run
from opencensus.ext.azure.log_exporter import AzureLogHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

logger.addHandler(AzureLogHandler())
logger.info("Starting the preprocessing script...")

run = Run.get_context()
custom_dimensions = {
    "parent_run_id": run.parent.id,
    "step_id": run.id,
    "step_name": run.name,
    "experiment_name": run.experiment.name,
    "run_url": run.parent.get_portal_url(),
    "run_type": "training"
}

logger.info("These are Custom Dimensions of the Preprocess Step", custom_dimensions)

parser = argparse.ArgumentParser("prep")
parser.add_argument("--output", type=str, help="Preprocessed data output path")
args = parser.parse_args()

raw_dataset = run.input_datasets['raw_data']
raw_dataframe = raw_dataset.to_pandas_dataframe()

raw_dataframe = raw_dataframe.drop(['PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1)
raw_dataframe.Age = raw_dataframe.Age.fillna(raw_dataframe.Age.median())
raw_dataframe.Embarked = raw_dataframe.Embarked.fillna('S')

embark_dummies_titanic = pd.get_dummies(raw_dataframe['Embarked'])
sex_dummies_titanic = pd.get_dummies(raw_dataframe['Sex'])
pclass_dummies_titanic = pd.get_dummies(raw_dataframe['Pclass'], prefix="Class")

training = raw_dataframe.drop(['Embarked', 'Sex', 'Pclass'], axis=1)
titanic = training.join([embark_dummies_titanic, sex_dummies_titanic, pclass_dummies_titanic])

os.makedirs(args.output, exist_ok=True)
titanic.to_csv(args.output + "/preproc.csv", index=False)
