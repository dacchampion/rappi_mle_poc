import argparse

from azureml.core import Run
from opencensus.ext.azure.log_exporter import AzureLogHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logger.addHandler(AzureLogHandler())

logger.info("Starting the model registry script...")

parser = argparse.ArgumentParser("register")
parser.add_argument("--in_linsvc_path", type=str, help="Linear SVC storage path")
parser.add_argument("--in_rf_path", type=str, help="Random forest storage path")
args = parser.parse_args()

run = Run.get_context()

custom_dimensions = {
    "parent_run_id": run.parent.id,
    "step_id": run.id,
    "step_name": run.name,
    "experiment_name": run.experiment.name,
    "run_url": run.parent.get_portal_url(),
    "run_type": "training"
}

logger.info("These are Custom Dimensions of the Model Registry Step", custom_dimensions)

OUTPUT_MODELS_DIR = './outputs/models'

runs_list = run.experiment.get_runs()
latest_run = next(runs_list)
train_step_run = latest_run.find_step_run('training step')[0]

linear_model = train_step_run.register_model(model_name='titanic_linear_svc',
                                             tags={'model_type': 'linear_svc'},
                                             model_path=f"{OUTPUT_MODELS_DIR}/linsvc_clf.pkl")
logger.info(f"{linear_model.name}\t{linear_model.id}\t{linear_model.version}")

rf_model = train_step_run.register_model(model_name='titanic_random_forest',
                                         tags={'model_type': 'random_forest'},
                                         model_path=f"{OUTPUT_MODELS_DIR}/rf_clf.pkl")
logger.info(f"{rf_model.name}\t{rf_model.id}\t{rf_model.version}")

run.complete()
