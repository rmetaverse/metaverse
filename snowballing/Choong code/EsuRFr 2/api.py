import functools
import requests
import logging

from config import APP_ID
from maspyutil import RateLimitedMin #rate_limited
from random import randint
from time import sleep

class MASError(Exception):
    """
    Base Exception thrown by the MAS Object when there is an error with the
    API.
    """

class MASResponse(object):
    """
    Response from a MAS Request
    """

class MAS(object):
    base_url = "http://academic.research.microsoft.com/json.svc/search"

    error_messages = (
        "The request is succeeded",
        "The AppID has no access rights to the MAS API",
        "Parameters are invalid",
        "The MAS service is temporarily unavailable",
        "The search condition is not supported yet",
    )

    result_objects = (
        "Author",
        "Publication",
        "Conference",
        "Journal",
        "Domain",
        "Organization",
        "Keyword",
    )

    def __getattr__(self, k):
        try:
            return object.__getattr__(self, k)
        except AttributeError:
            k = k.capitalize()
            assert k in self.result_objects

            def function(obj_type, **params):
                params['ResultObjects'] = obj_type
                return self.request(params)

            return functools.partial(function, k)

    def __init__(self, app_id):
        self.app_id = app_id
    
    @RateLimitedMin(180) #@rate_limited(180,60)
    def request(self, params):
        params['AppId'] = self.app_id
        print "PARAMS", params # FIXME logging
        result_objects = params['ResultObjects']        
        resp = requests.request("GET", self.base_url, params=params)
        try:
            resp_data = resp.json()['d']
            okflag = True
        except:
            print "The json response has no 'd' key"
            print "Response TEXT", resp.raw
            #print "Response JSON", resp.json()
            #raise            
            okflag = False
        
        okcount = 1
        fulltextq = [u'text mining',u'autoregressive',u'database',u'language processing',u'machine learning']
        while okflag == False:
            sleep(randint(30,60))            
            faked = {'StartIdx': '1', 'FulltextQuery': u'', 'EndIdx': '30', 'PublicationContent': 'AllInfo', 'AppId': '', 'ResultObjects': 'Publication'}
            faked['AppId'] = self.app_id
            no = okcount - (okcount//5)*5 - 1
            faked['FulltextQuery'] = fulltextq[no]
            resp = requests.request("GET", self.base_url, params=faked)
            sleep(randint(30,60))
            resp = requests.request("GET", self.base_url, params=params)
            try:
                resp_data = resp.json()['d']
                okflag = True
            except:
                okcount += 1
                print "The json response has no 'd' key AGAIN : %s" %(okcount)
                
                #raise
        # Check that the request is successfull
        try:
            result_code = resp_data['ResultCode']
            assert result_code == 0
        # Print meaningful error message
        except AssertionError:
            print self.error_messages[result_code]
        return resp_data[result_objects]

class MASFacade(object):
    def __init__(self, app_id):
        self.api = MAS(app_id)

    def author(self, author_id):
        resp = self.api.author({"AuthorID": author, "StartIdx": 1, "EndIdx": 1})
        try:
            return resp['Author']['Result'][0]
        except IndexError:
            print "No Author found with the specified AuthorID", author_id
            raise
        except: # KeyError should never happen
            print "Unexplainable Error"
            raise

api = MAS(APP_ID)

