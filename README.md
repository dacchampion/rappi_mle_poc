# Rappi MLE challenge solution

The following repository contains a set of file scripts solving most of the tasks involved in the development and provisioning of the two tasks of the challenge:
1. Model training pipeline development and provisioning
2. API publishing and misc tasks

Both tasks were developed in Azure cloud platform and most of the configuratons were written as python scripts which are creating resources in the cloud or querying
them, some few local files are used but most of what is necessary is hosted by Azure.

Following, there is an introduction to the scripts and the associated artifacts in the order they are required to solve the two main tasks and their technical
requirements. So, the following is a mean to descriibe the generated scripts and how they try to solve a problem, if there is no source code then a description
of how this was tackled or would have been on the platform is given.


## Azure configuration steps

### Prerequisites
- Hold an Azure subscription
- Create a resource group (for this excercise _rappi_rg_)
- Check for the subscrption id on Azure dashboard

### Procedure (_Locally_)
- 1. Create an anaconda environment (_rappi_env_) to hold package requirements
- 2. Install **azureml-sdk** under the created environment
- 3. Start a local project (_rappi_prj_) where scripts are to be developed
- 4. Make a hidden directory _.azureml_ where workspace config is going to reside for seamless connectivity

### Workspace and compute resource creation
**create_workspace.py**: This file contains the steps for creating a Machine Learning workspace _rappii_ws_ in Azure
**create_compute.py**: Script in charge of provisioning a compute resource. For this use case, I choose a small size cluster with 2 vCPUs and 7GB of memory.

## Model-training pipeline

The created pipeline was fully developed in python scripts, there wa not need of using Azure ML studio with Drag & Drop functionality. The steps were also
created in independent steps in form of python scripts. Following the prcedure to generate the pipeline:

**00-upload-data.py**: The goal of this script is to upload raw data files for this problem and create a dataset with different versions each time it is run.
it relies on an input scrpt parameter *dataset_path* indicating where the raw data resides locally. For this example the files exist in */data/titanic* and
there are two samples in different subfolders *ds_full* and *ds_half*.

**01-training-pipelne.py**: This script creates a pipeline in the before mentioned workspace using the compute resource as a target and generates an environment 
configuration from an yml file created on the hidden confog folder. The only parameter to this script is the data verson for the dataset *input_ds_version*, 
if it is zero wiill recover the latest one. Following the steps achieved by this script:

- 1. Retrieve the compute target
- 2. Configure the training run **virtual environment**
- 3. Using rappi run environment for training (the one given by the challenge)
- 4. Get the default datastore
  - 4a. Retrieve the dataset by version
  - 4b. Declare inter pipeline data
  - 4c. Declare output data holder
- 5. Declare the pipeline steps that conforms the training procedure
  - 5a. Prepreocessing step backed by script **pipeline-steps/preprocess.py**
  - 5b. Training step backed by script **pipeline-steps/train.py**
  - 5c. Register model step backed by script **pipeline-steps/model_registry.py**
- 6. Pipeline built
- 7. Piepline submission to the cloud

**02-publish-pipelne.py**: This script retrieves the latest run from the pipeline created experiment _Titanic_models_exp_ and call the publish pipeline.

**03-execute-pub-pipelne.py**: The goal of this script is to test the external service to invoke the pipelin in order to provision possible **automation**. 
Once the pipeline is published can be called as a Rest service using a pipeline endpoint.

## API creation and publishing steps
Once the models are registerd on the Azure ML platform they are candidates for giving them the ability for generating traces, web service endpoints, enabling 
a separate / scalable compute resource and additional tasks like generating an API front-end with API management (**HTTP connection management and processing**) 
and handling traffc for **A/B testing**.

**04-deploy-models.py**: This script tackles model deployment once they are registered, in this case is using an Azure Container Instance as a Kubernetes one
requires a bigger cluster and is much more expensive. In the end, it will be generating an endpoint which can be consumed from anywhere. The script has 3 parameters:

* a) *entry_script*: It is the script file path which is in charge of providing with inferences can be either **./deploy_src/linsvc_inference.py** or 
**./deploy_src/rf_inference.py**
* b) *model_name*: It is the registered model name on Azure
* c) *pub_service_name*: This is the name which will be used inside the platform for versioning matters and public naming

**05-unittest-inference.py**: Having the webservice endpoints ready, it is possible to **unit test** the different outcomes with this test case script containing 4
considering the different possibilities being the models and their outcomes.

**06-test-pub-services.py**: This script checks the published model endpoint and verifies that it provides single and multiple predictions.

**07-profile-service.py**: According to the requirements for **API profiling** this script is performing this check by using an existing *model_id* registerd in
Azure. In addition it requires a parameter for the *inferencing script*, the same ones as in *4a*, and finally, it asks for the *profile_name* which is just
informative.

**09-dockerize-model.py**: With an existing registerd model the goal of this script is to generate docker artifacts. The **Dockerized solution** container artifacts 
are downloaded and saved on a local directory *./titanic_container*. For this, it requires the following parameters:

* a) *model_id*: Within this parameter it is specified the registered model identifier
* b) *entry_script*: It is an inferencing script, can be any of the provided ones in **4a**

Additional requirements like **Proper error handling** and **A/B testing**, are to be tackled in that order. For the former by providing a proper front-end and 
processing steps by means of the API Management component providd by Azure and for the latter once having this API ready, can be used the wrapped entries to 
generate traffic diversion on the App Web facility in order to collect data and do further study analysis.
