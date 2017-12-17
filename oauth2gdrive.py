from __future__ import print_function
import os
 
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
 
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
 
CLIENT_SECRET_FILE = 'client_secret.json'
CREDENTIAL_DIR = '.credentials'
CREDENTIAL_FILE = 'google-drive-credential.json'
 
def get_credentials(application_name, scopes):
    """Gets valid user credentials from storage.
 
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
 
    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.dirname(os.path.abspath(__file__))
    credential_dir = os.path.join(home_dir, CREDENTIAL_DIR)
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, CREDENTIAL_FILE)
 
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, scopes)
        flow.user_agent = application_name
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials
