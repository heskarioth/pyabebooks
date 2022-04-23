import json
from xmlrpc.client import Boolean


def check_response(json_response:json,request_type) -> Boolean:
    if request_type=='price':
        if json_response['errorTexts'][0]==None:
            return True
        return False
    else:
        if len(json_response['widgetResponses'])!=0:
            return True
        return False
