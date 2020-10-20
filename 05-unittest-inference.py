import json
import unittest

from azureml.core import Workspace, Webservice

ws = Workspace.from_config()
rf_service = Webservice(workspace=ws, name='rfservice')
linsvservice = Webservice(workspace=ws, name='linsvservice')


class InferenceTest(unittest.TestCase):
    rose = json.dumps({'data': [
        [17, 0, 1, 53.1000, 0, 0, 1, 1, 0, 1, 0, 0]
    ]})

    jack = json.dumps({'data': [
        [23, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1]
    ]})

    def test_linear_survivor(self):
        test_result = linsvservice.run(self.rose)[0]
        self.assertEqual(test_result, 1, "Problems with survivor prediction with linear model")

    def test_linear_casualty(self):
        test_result = linsvservice.run(self.jack)[0]
        self.assertEqual(test_result, 0, "Problems with casualty prediction with linear model")

    def test_rf_survivor(self):
        test_result = rf_service.run(self.rose)[0]
        self.assertEqual(test_result, 1, "Problems with survivor prediction with random forest")

    def test_rf_casualty(self):
        test_result = rf_service.run(self.jack)[0]
        self.assertEqual(test_result, 0, "Problems with casualty prediction with random forest")


unittest.main()
