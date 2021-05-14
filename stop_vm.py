import base64
from pprint import pprint

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

def hello_pubsub(event, context):
  credentials = GoogleCredentials.get_application_default()

  service = discovery.build('compute', 'v1', credentials=credentials)

  # Project ID for this request.
  project = 'analytics-research-255320'  # TODO: Update placeholder value.

  # The name of the zone for this request.
  zone = 'us-west1-b'  # TODO: Update placeholder value.

  # Name of the instance resource to start.
  instance = 'ajimen-ui'  # TODO: Update placeholder value.

  request = service.instances().stop(project=project, zone=zone, instance=instance)
  response = request.execute()

  # TODO: Change code below to process the `response` dict:
  pprint(response)