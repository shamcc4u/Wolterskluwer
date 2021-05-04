import requests
import json
import sys
import argparse

parser = argparse.ArgumentParser(description='cnlp app server response test.')
parser.add_argument("--oauth-host", help="fully qualified domain name of the host along with port number (ex: http://stgsec01.healthlanguage.com:7000) (required)", required=True)
parser.add_argument("--oauth-client-id", help="client_id obtained from keycloack server (ex: cnlp_integration_test_1) (required)", type=str, required=True)
parser.add_argument("--oauth-client-secret", help="client_secretobtained from keycloack server (ex: 1380cbed-beb0-4157-869f-418a398ffde3)", type=str, required=True)
parser.add_argument("--app-host", help="fully qualified domain name of the host along with port number (ex: http://stageindex01:8282) (required)", required=True)
args = parser.parse_args()


oauth_host = args.oauth_host
oauth_client_id = args.oauth_client_id
oauth_client_secret = args.oauth_client_secret
app_host = args.app_host
#Global variables
timeout_sec = 60

#Oauth2 - keycloack related variables
#oauth_host = "http://stgsec01.healthlanguage.com:7000"
oauth_url = oauth_host+"/auth/realms/master/protocol/openid-connect/token"
#oauth_client_id = "cnlp_integration_test_1"
#oauth_client_secret = "1380cbed-beb0-4157-869f-418a398ffde3"
oauth_grant_type = "client_credentials"
oauth_verb = "POST"
oauth_headers = {'content-type': "application/x-www-form-urlencoded"}
oauth_payload = "client_id="+oauth_client_id+"&client_secret="+oauth_client_secret+"&grant_type="+oauth_grant_type

#App server variables
#app_host = "http://stageindex01:8282"
app_url = app_host+"/job/v1/enrich/async"
app_payload = "{\r\n    \"enrichmentInput\": \r\n\r\n{         \"text\": \"Problems: MI\\nFH: father had lung cancer\",         \"useCaseId\": \"all_domains\"     }\r\n}"
app_server_verb = "POST"

# method to fetch auth token from respective oauth server.
def fetch_auth_token():
    try:
      response = requests.request(oauth_verb, oauth_url, data=oauth_payload, headers=oauth_headers, timeout=timeout_sec)
      if response.status_code == 200:
          try:
            access_token = json.loads(response.text)['access_token']
            return access_token
          except ValueError:
            print("ERROR : Unable to parse the json returned from Oauth2 server(keycloack) ")
      else:
          output_msg = "ERROR : "+oauth_url+"  Oauth2 server(keycloack) returned non 200 status code. Please check.."
          print(output_msg)
          sys.exit(1)
    except requests.exceptions.RequestException as response_err:
      print("ERROR :  Oauth2 server(keycloack) returned an exception. Please check.."+str(response_err))
      sys.exit(1)

#method to process application server data.
def app_server_call():
    headers = {
        'authorization': "Bearer "+ fetch_auth_token(),
        'content-type' : "application/json"
    }
    try:
      response = requests.request(app_server_verb, app_url, data=app_payload, headers=headers, timeout=timeout_sec)
      if response.status_code == 200:
        try:
          result_count = len(json.loads(response.text)['output'].items())
          if result_count > 0:
            print("SUCCESS : Result count is greater than zero.")
            sys.exit(0)
          else:
            print("ERROR : Result count is zero.")
            sys.exit(1)
        except ValueError:
          print("ERROR : Unable to parse the json returned from App server")
          sys.exit(1)
      else:
        print("ERROR : "+app_url+"  App server returned non 200 status code. Please check..")
        sys.exit(1)
    except requests.exceptions.RequestException as response_err:
      print("ERROR :  App Server returned an exception. Please check.."+str(response_err))
      sys.exit(1)


app_server_call()
