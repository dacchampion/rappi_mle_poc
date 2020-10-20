# rappi_prj/train.py
import argparse
import datetime as dt
import logging
import os
import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier

from azureml.core import Run
from opencensus.ext.azure.log_exporter import AzureLogHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logger.addHandler(AzureLogHandler())

logger.info("Starting the training script...")

parser = argparse.ArgumentParser("train")
parser.add_argument("--prepped_data", type=str, help="Preprocessed data path")
parser.add_argument("--out_linsvc_path", type=str, help="Linear SVC storage path")
parser.add_argument("--out_rf_path", type=str, help="Random forest storage path")
args = parser.parse_args()

run = Run.get_context()
run.log("Training start time", str(dt.datetime.now()))

custom_dimensions = {
    "parent_run_id": run.parent.id,
    "step_id": run.id,
    "step_name": run.name,
    "experiment_name": run.experiment.name,
    "run_url": run.parent.get_portal_url(),
    "run_type": "training"
}

logger.info("These are Custom Dimensions of the Preprocess Step", custom_dimensions)

titanic = pd.read_csv(args.prepped_data + "/preproc.csv")

X_all = titanic.drop('Survived', axis=1)
y_all = titanic.Survived

num_test = 0.20
X_train, X_test, y_train, y_test = train_test_split(X_all, y_all, test_size=num_test, random_state=23)

logger.info(f"Train features shape - {X_train.shape}")
logger.info(f"Train label shape - {y_train.shape}")
logger.info(f"Test features shape - {X_test.shape}")
logger.info(f"Test label shape - {y_test.shape}")

linsvc_clf = LinearSVC()
linsvc_clf.fit(X_train, y_train)
pred_linsvc = linsvc_clf.predict(X_test)
acc_linsvc = accuracy_score(y_test, pred_linsvc)

run.log('Linear SVC accuracy: ', acc_linsvc)

rf_clf = RandomForestClassifier()
rf_clf.fit(X_train, y_train)
pred_rf = rf_clf.predict(X_test)
acc_rf = accuracy_score(y_test, pred_rf)

run.log('Random Forest accuracy: ', acc_rf)
run.log("Training end time", str(dt.datetime.now()))

OUTPUT_MODELS_DIR = './outputs/models'
if not os.path.isdir(OUTPUT_MODELS_DIR):
    os.mkdir(OUTPUT_MODELS_DIR)
pickle.dump(linsvc_clf, open(f"{OUTPUT_MODELS_DIR}/linsvc_clf.pkl", 'wb'))

# if not os.path.isdir(args.out_rf_path):
#    os.mkdir(args.out_rf_path)
pickle.dump(rf_clf, open(f"{OUTPUT_MODELS_DIR}/rf_clf.pkl", 'wb'))
