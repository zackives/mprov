import boto3
import jwt
import requests
import logging
import uuid
import datetime
from requests.exceptions import HTTPError
from pennprov.config import config

logger = logging.getLogger(__name__)

PENNSIEVE_URL = "https://api.pennsieve.io"


class PennsieveClient:
    '''
    Client for app.pennsieve.io platform
    '''

    def __init__(self):
        r = requests.get(f"{PENNSIEVE_URL}/authentication/cognito-config")
        r.raise_for_status()

        self.cognito_app_client_id = r.json()["tokenPool"]["appClientId"]
        self.cognito_region = r.json()["region"]
        self.cognito_idp_client = boto3.client(
            "cognito-idp",
            region_name=self.cognito_region,
            aws_access_key_id="",
            aws_secret_access_key="",
        )
        self.api_session = None

    def _ensure_active_api_session(self):
        if self.api_session is None or self.api_session.is_almost_expired():
            logger.debug(f"Connecting to {self.cognito_region}, app {self.cognito_app_client_id}")

            # Authenticate to AWS Cognito
            #
            # Hack: stub the access and secret keys with empty values so boto does
            # not look for AWS credentials in the environment. Some versions of boto
            # fail when they cannot find AWS credentials even though Cognito does
            # not need creds.
            login_response = self.cognito_idp_client.initiate_auth(
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={"USERNAME": config.pennsieve.api_key,
                                "PASSWORD": config.pennsieve.api_secret},
                ClientId=self.cognito_app_client_id,
            )

            access_token = login_response["AuthenticationResult"]["AccessToken"]
            id_token = login_response["AuthenticationResult"]["IdToken"]

            claims = jwt.decode(id_token, options={'verify_signature': False})
            expiration = claims['exp']
            organization_node_id = claims['custom:organization_node_id']
            self.api_session = APISession(
                token=access_token,
                expiration=expiration,
                organization_node_id=organization_node_id
            )

    def _base_headers(self):
        self._ensure_active_api_session()
        return {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Bearer " + self.api_session.token,
            "X-ORGANIZATION-ID": self.api_session.organization_node_id
        }

    def _post(self, url, payload):
        '''
        Post message to Pennsieve, with token attached
        '''
        headers = self._base_headers()
        return requests.post(url, json=payload, headers=headers)

    def _put(self, url, payload):
        headers = self._base_headers()
        return requests.put(url, json=payload, headers=headers)

    def _create_model_if_needed(self, ds_id):
        model_name = "provenance"
        model_payload = {
            "name": model_name,
            "displayName": model_name,
            "description": "mProv provenance link",
            "locked": True,
            "templateId": str(uuid.uuid4())
        }

        # Create provenance model
        try:
            model_response = self._post(f"{PENNSIEVE_URL}/models/v1/datasets/{ds_id}/concepts", payload=model_payload)
            model_response.raise_for_status()
            payload = [
                {
                    "id": ds_id,
                    "name": "prov_url",
                    "displayName": "Provenance URL",
                    "description": "Provenance URL",
                    "locked": True,
                    "default": True,
                    "conceptTitle": True,
                    "dataType": "String",
                    "required": True
                }
            ]

            property_response = self._put(
                f"{PENNSIEVE_URL}/models/v1/datasets/{ds_id}/concepts/{model_name}/properties",
                payload=payload)
            property_response.raise_for_status()

        except HTTPError as e:
            if model_response.status_code == requests.codes.bad_request:
                logger.debug(f"Ignoring bad create model request. Model probably already exists: {e}")
            else:
                raise e
        return model_name

    def _attach_file_to_record(self, ds_id, file_id, record_id):
        payload = {
            "externalId": file_id,
            "targets": [
                {
                    "direction": "FromTarget",
                    "linkTarget": {
                        "ConceptInstance": {
                            "id": record_id
                        }
                    },
                    "relationshipType": "belongs_to",
                    "relationshipData": []
                }
            ]
        }
        response = self._post(
            f'{PENNSIEVE_URL}/models/datasets/{ds_id}/proxy/package/instances', payload=payload)
        return response

    def attach_provenance(self, ds_id, file_id, prov_url):

        # Make sure there is a Model for the provenance property
        model_name = self._create_model_if_needed(ds_id)
        payload = {"values": [
            {
                "name": "prov_url",
                "value": prov_url
            }
        ]}

        response = self._post(f"{PENNSIEVE_URL}/models/v1/datasets/{ds_id}/concepts/{model_name}/instances", payload)
        record_id = response.json()['id']
        self._attach_file_to_record(ds_id, file_id, record_id)
        return


class APISession:
    """Holds session info for Pennsieve API

    Attributes:
    ----------
    token: str
        The AccessToken returned by Cognito. This token is needed to access Pennsieve API endpoints.
        Used as the Bearer token in the Authorization header in Pennsieve API requests.
    organization_node_id: str
        The node id of the user's organization.
        Used as the value of the X-ORGANIZATION-ID header in Pennsieve API requests.
    expiration: datetime.datetime
        the expiration datetime of the token in UTC

    Methods:
    --------
    is_almost_expired()
        returns True if token is "near" its expiration time, False if not

    """
    EXPIRATION_MARGIN = datetime.timedelta(minutes=1)

    def __init__(
            self,
            token: str,
            expiration: datetime.datetime | int,
            organization_node_id: str):
        """Constructor for APISession

            Parameters:
            ----------
            token: str
                The AccessToken returned by Cognito.
                Used as the Bearer token in the Authorization header for Pennsieve API requests.
            expiration: datetime | int
                The expiration datetime of the token in UTC.
                If this is a datetime, it should be in UTC.
                If this is an int, it should be a POSIX timestamp. It will be converted to a datetime
            organization_node_id: str
                The node id of the user's organization.
                Used as the value of the X-ORGANIZATION-ID header in Pennsieve API requests.
        """
        self.token = token
        self.expiration = datetime.datetime.fromtimestamp(expiration,
                                                          datetime.timezone.utc) if isinstance(expiration,
                                                                                               int) else expiration
        self.organization_node_id = organization_node_id

    def is_almost_expired(self) -> bool:
        now = datetime.datetime.now(datetime.timezone.utc)
        if now > self.expiration - APISession.EXPIRATION_MARGIN:
            return True
        return False

    def __str__(self):
        return str(self.__dict__)

# Sample code
# c = PennsieveClient()
# c.attach_provenance("N:dataset:0194ebba-8766-4d11-aa62-dda7cc0e28bd", "N:package:68abc46c-fd65-4cdd-8216-22b6eeab0718", "mprov://123-456-789")
