import argparse

from azureml.core import Workspace, Dataset, Environment, Experiment
from azureml.core.compute import AmlCompute
from azureml.core.runconfig import RunConfiguration
from azureml.exceptions import UserErrorException
from azureml.pipeline.core import Pipeline, PipelineData
from azureml.pipeline.steps import PythonScriptStep

COMPUTE_NAME = "rappi-cp-cluster"

if __name__ == "__main__":
    parser = argparse.ArgumentParser("pipeline")
    parser.add_argument("--input_ds_version", type=int, help="Input dataset version", required=False, default=0)
    args = parser.parse_args()

    ws = Workspace.from_config()

    # 1. Retrieve already created compute target
    compute_target = ws.compute_targets[COMPUTE_NAME]
    if compute_target and type(compute_target) is AmlCompute:
        print("1. Found compute target: " + COMPUTE_NAME)

    # 2. Configure training run environment
    aml_run_config = RunConfiguration()
    aml_run_config.target = compute_target
    aml_run_config.environment.python.user_managed_dependencies = False
    print("2. Training run env configured succesfully")

    # 3. Using rappi run environment for training
    env = Environment.from_conda_specification(name='rappi-ml-challenge', file_path='.azureml/environment.yml')
    aml_run_config.environment = env
    aml_run_config.environment.environment_variables = {
        "APPLICATIONINSIGHTS_CONNECTION_STRING": 'InstrumentationKey=5b8cb8f7-c537-4b6e-8544-5fa5ea6f26ff'
    }
    print("3. Retrieved run environment")

    # 4. Get the input dataset for the pipeline
    default_datastore = ws.get_default_datastore()
    # 4a. Raw data declaration and registry
    try:
        print(f"Trying to get passed over version parameter: {args.input_ds_version}")
        titanic_ds = Dataset.get_by_name(workspace=ws, name='titanic_data', version=args.input_ds_version)
    except UserErrorException:
        print(f"Input version is not available, getting latest...")
        titanic_ds = Dataset.get_by_name(workspace=ws, name='titanic_data')
    raw_data = titanic_ds.as_named_input('raw_data')
    # 4b. Declare the inter pipeline dataset
    preproc_data = PipelineData("preprocessed_data", datastore=default_datastore).as_dataset()
    # 4c. Output data declaration for model stores
    linsvc_path = PipelineData("linear_svc_path", datastore=default_datastore, output_name="out_linsvc_path")
    rf_path = PipelineData("random_forest_path", datastore=default_datastore, output_name="out_rf_path")
    print("4. Got the input dataset for the pipeline")

    # 5. Declare the pipeline steps that conforms the training
    pipeline_dir = "./pipeline-steps"

    data_prep_step = PythonScriptStep(
        name='preprocessing step',
        script_name="preprocess.py",
        source_directory=pipeline_dir,
        arguments=["--output", preproc_data],
        inputs=[raw_data],
        outputs=[preproc_data],
        compute_target=compute_target,
        runconfig=aml_run_config,
        allow_reuse=True
    )
    print("5a. Succesfully configured preproc step")

    train_step = PythonScriptStep(
        name='training step',
        script_name="train.py",
        source_directory=pipeline_dir,
        arguments=["--prepped_data", preproc_data, "--out_linsvc_path", linsvc_path, "--out_rf_path", rf_path],
        inputs=[preproc_data],
        outputs=[linsvc_path, rf_path],
        compute_target=compute_target,
        runconfig=aml_run_config,
        allow_reuse=True
    )
    print("5b. Succesfully configured training step")

    register_step = PythonScriptStep(
        name='register model step',
        script_name="model_registry.py",
        source_directory=pipeline_dir,
        arguments=["--in_linsvc_path", linsvc_path, "--in_rf_path", rf_path],
        inputs=[linsvc_path, rf_path],
        compute_target=compute_target,
        runconfig=aml_run_config,
        allow_reuse=True
    )
    print("5c. Succesfully configured model registration step")

    # 6. Build the pipeline
    pipeline = Pipeline(workspace=ws, steps=[data_prep_step, train_step, register_step])
    print("6. Pipeline built")

    # 7. Submit the pipeline
    pipeline_run = Experiment(ws, 'Titanic_models_exp').submit(pipeline)
    pipeline_run.wait_for_completion()
    print("7. Pipeline submitted")
