import json
import numpy as np
import os
import pickle


def init():
    global linsvc
    model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'), 'linsvc_clf.pkl')
    linsvc = pickle.load(open(model_path, "rb"))


def run(data):
    try:
        data_dict = json.loads(data)
        data = np.array(data_dict["data"])
        result = linsvc.predict(data)
        return result.tolist()
    except Exception as e:
        error = str(e)
        return error
