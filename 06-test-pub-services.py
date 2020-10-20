import argparse
import requests
import json

from azureml.core.authentication import InteractiveLoginAuthentication

if __name__ == "__main__":
    parser = argparse.ArgumentParser("testing")
    parser.add_argument("--aci_id", type=str, help="URI for the model service wrapper")
    args = parser.parse_args()

    # Get a token to authenticate to the compute instance from remote
    interactive_auth = InteractiveLoginAuthentication()
    auth_header = interactive_auth.get_authentication_header()

    # Create and submit a request using the auth header
    headers = auth_header
    # Add content type header
    headers.update({'Content-Type': 'application/json'})

    # Sample data to send to the service
    test_sample = json.dumps({'data': [
        [17, 0, 1, 53.1000, 0, 0, 1, 1, 0, 1, 0, 0],
        [23, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1]
    ]})
    test_sample = bytes(test_sample, encoding='utf8')

    # service_url = "http://localhost:8890/score"
    service_url = f"http://{args.aci_id}.westus.azurecontainer.io/score"
    resp = requests.post(service_url, test_sample, headers=headers)
    print("prediction:", resp.text)
