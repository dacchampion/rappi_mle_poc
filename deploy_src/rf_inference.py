import json
import numpy as np
import os
import pickle


def init():
    global rf
    model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'), 'rf_clf.pkl')
    rf = pickle.load(open(model_path, "rb"))


def run(data):
    try:
        data_dict = json.loads(data)
        data = np.array(data_dict["data"])
        result = rf.predict(data)
        return result.tolist()
    except Exception as e:
        error = str(e)
        return error
