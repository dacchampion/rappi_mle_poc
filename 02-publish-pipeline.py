from azureml.core import Experiment, Workspace

ws = Workspace.from_config()
titanic_exp = Experiment(ws, "Titanic_models_exp")

runs_list = titanic_exp.get_runs()
latest_run = next(runs_list)

pub_titanic_models = latest_run.publish_pipeline(
    name="Published_titanic_models",
    description="This pipeline trained successful models for the Titanic sink dataset",
    version="1.0")
