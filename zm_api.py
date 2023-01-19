# Some portions of this class influenced by the pyzm project, so thanks for that.

import sys
import requests
import time
from datetime import datetime

class ZMAPI:
    def __init__(self, localserver, username, password, webserver=None, verify_ssl=True,
                 debug_level=1):
        self.username = username
        self.password = password
        self.verify = verify_ssl
        self.debug_level = debug_level

        self.apipath = localserver + '/zm/api'
        if webserver is None:
            self.webpath = localserver + '/zm/index.php'
        else:
            self.webpath = webserver + '/zm/index.php'
        self.access_init = None
        self.refresh_init = None

        self.access_token = None
        self.access_timeout = 0
        self.refresh_token = None
        self.refresh_timeout = 0

    def _needAccess(self, access_buffer=300):
        '''Checks if we need a new access token (soon or already)'''
        if self.access_token is None or self._access_timeout <= time.time()+access_buffer:
            return True
        return False

    def _needRefresh(self, refresh_buffer=600):
        '''Checks if we need a new refresh token (soon or already)'''

        if self.refresh_token is None or self.refresh_timeout <= time.time()+refresh_buffer:
            return True
        return False

    def _refreshTokens(self):
        '''Refreshes tokens if needed'''

        if self._needRefresh():
            # Get new tokens via username and password if the refresh token has expired
            check = self.login(method='password')
        else:
            # Get a new access token if needed. Otherwise take no action.
            if self._needAccess():
                check = self.login(method='refresh_token')
        return check

    def _makeRequest(self, url, params=[], method="get", post_data=None):
        '''Makes a request to the API, appending access token, and returns response.
           params is a list of options to be appended at the end of the url (other
           than the access token). Automatically refreshes tokens if required.
           method: 'get' or 'post'
           post_data: optional dict of data to go along with a post request'''

        # Initialize r as bad request so calling method can catch it on error
        r = requests.Response()
        r.status_code = 400

        # Refresh tokens if needed
        if not self._refreshTokens():
            return r

        # Put together the url
        access_url = url + '?token={:s}'.format(self.access_token)
        for item in params:
            access_url += '&' + item

        # Make the request and return the response
        if method == 'get':
            try:
                r = requests.get(access_url, verify=self.verify)
            except requests.exceptions.ConnectionError:
                self.debug(1, "Get request failed due to connection error.", "stderr")
        elif method == 'post':
            try:
                r = requests.post(access_url, data=post_data, verify=self.verify)
            except requests.exceptions.ConnectionError:
                self.debug(1, "Post request failed due to connection error.", "stderr")
        return r

    def debug(self, level, message, pipename='stdout'):
        if level >= self.debug_level:
            curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if pipename == "stderr":
                sys.stderr.write("{:s} zm_api: {:s}\n".format(curr_time, message))
            else:
                sys.stdout.write("{:s} zm_api: {:s}\n".format(curr_time, message))

    def login(self, method='password'):
        '''Performs login and saves access and refresh tokens. Returns True if successful
           and False if not.'''

        login_url = self.apipath + '/host/login.json'
        if method == 'password' or self._needRefresh():
            login_data = {'user': self.username, 'pass': self.password}
        else:
            login_data = {'token': self.refresh_token}
        try:
            r = requests.post(url=login_url, data=login_data, verify=self.verify)
            if r.ok:
                rj = r.json()
                self.access_token = rj['access_token']
                self.access_timeout = float(rj['access_token_expires']) + time.time()
                self.refresh_token = rj['refresh_token']
                self.refresh_token_timeout = float(rj['refresh_token_expires']) + time.time()
                api_version = rj['apiversion']
                if api_version != '2.0':
                    self.debug(1, "API version 2.0 required.", "stderr")
                    return False
                access_init = time.time()
                refresh_init = time.time()
            else:
                self.debug(1, "Login failed with status {:d}.".format(r.status_code), "stderr")
                return False
        except requests.exceptions.ConnectionError:
            self.debug(1, "Login failed due to connection error.", "stderr")
            return False

        return True

    def logout(self):
        '''Logs out of the API and returns True if successful, False if not'''

        logout_url = self.apipath + '/host/logout.json'
        r = self._makeRequest(logout_url)
        return r.ok

    def getDaemonStatus(self):
        '''Returns True if ZoneMinder is running, False if not or on error'''

        daemon_url = self.apipath + '/host/daemonCheck.json'
        r = self._makeRequest(daemon_url)
        if r.ok:
            status = int(r.json()['result'])
            return status == 1
        else:
            self.debug(1, "Connection error in getDaemonStatus", "stderr")
        return False

    def getRunStates(self):
        '''Returns a list of run states. Each item in the list is a dict with the form:
           item['id']: Id of the run state in the DB
           item['name']: run state name
           item['active']: True/False: whether this is the active run state. Note that just
                           because a run state is listed as active doesn't mean ZM is running.
                           It could just be the last one that ran. Use getDaemonStatus to
                           determine if it is running.
           List will be empty if there is an error.'''

        runstates = []
        stateurl = self.apipath + "/states.json"
        r = self._makeRequest(stateurl)
        if not r.ok:
            self.debug(1, "Error getting run states", "stderr")
            return runstates
        rj = r.json()
        states = rj['states']
        for state in states:
            statedict = state['State']
            runstates.append({'id': statedict['Id'],
                              'name': statedict['Name'],
                              'active': statedict['IsActive']==1})
        return runstates

    def changeRunState(self, runstate_name):
        '''Changes run state. Returns True on success or False on error.'''

        stateurl = self.apipath + "/states/change/{:s}.json".format(runstate_name)
        r = self._makeRequest(stateurl, method="post")
        return r.ok
