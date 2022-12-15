import boto3
import requests
import logging
import uuid

from pennprov.config import config


PENNSIEVE_URL = "https://api.pennsieve.io"

class PennsieveClient:
    '''
    Client for app.pennsieve.io platform
    '''

    def __init__(self):
        r = requests.get(f"{PENNSIEVE_URL}/authentication/cognito-config")
        r.raise_for_status()

        cognito_app_client_id = r.json()["tokenPool"]["appClientId"]
        cognito_region = r.json()["tokenPool"]["region"]

        print("Connecting to " + cognito_region + ", app " + cognito_app_client_id)

        cognito_idp_client = boto3.client(
            "cognito-idp",
            region_name=cognito_region,
            aws_access_key_id=""
            aws_secret_access_key="",
        )

        # Authenticate to AWS Cognito
        #
        # Hack: stub the access and secret keys with empty values so boto does
        # not look for AWS credentials in the environment. Some versions of boto
        # fail when they cannot find AWS credentials even though Cognito does
        # not need creds.
        login_response = cognito_idp_client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": config.pennsieve.api_key, 
            "PASSWORD": config.pennsieve.api_secret},
            ClientId=cognito_app_client_id,
        )

        self.token = login_response["AuthenticationResult"]["AccessToken"]

    def _post(self, url, payload, headers):
        '''
        Post message to Pennsieve, with token attached
        '''
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Bearer " + self.token
        }

        return requests.post(url, json=payload, headers=headers)

    def _create_model_if_needed(self, ds_id):
        payload = {
            "name": "provenance",
            "displayName": "provenance",
            "description": "mProv provenance link",
            "locked": True,
            "templateId": uuid.uuid4()
        }

        # Create provenance model
        try:
            response = self._post(f"{PENNSIEVE_URL}/models/v1/datasets/datasetId/concepts", json=payload)

            payload = [
                {
                    "id": ds_id,
                    "name": "prov_url",
                    "displayName": "Provenance URL",
                    "description": "Provenance URL",
                    "locked": True,
                    "default": True,
                    "conceptTitle": False,
                    "dataType": "string",
                    "required": True
                }
            ]

            response = self._post(f"{PENNSIEVE_URL}/models/v1/datasets/datasetId/concepts/url/properties", json=payload)

            return response['id']

        except:
            pass
        return None

    def attach_provenance(self, ds_id, file_id, prov_url):

        # Make sure there is a Model for the provenance property
        self._create_model_if_needed(ds_id)

        payload = {"values": [
                {
                    "name": "prov_url",
                    "value": prov_url
                },
                {
                    "name": "file",
                    "value": file_id
                },
            ]}

        response = self._post(f"{PENNSIEVE_URL}/models/v1/datasets/" + ds_id + "/concepts/provenance/instances", payload)

        return

# Sample code
c = PennsieveClient()
c.attach_provenance("N:dataset:0194ebba-8766-4d11-aa62-dda7cc0e28bd", "N:package:68abc46c-fd65-4cdd-8216-22b6eeab0718", "mprov://123-456-789")
