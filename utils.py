import json
from typing import List, Type
from xmlrpc.client import Boolean
import re
import numpy as np
import pandas as pd

def generate_retry_intervals():
    max_retries = 5
    base_wait = 2.1
    retry_intervals = [(base_wait**retry_n) + np.random.uniform(0.3,0.8) for retry_n in range(max_retries)]
    return retry_intervals, max_retries

def check_response(json_response:json,request_type:str='price') -> Boolean:
    if request_type=='price':
        if json_response['errorTexts'][0]==None:
            return True
        return False
    else:
        if len(json_response['widgetResponses'])!=0:
            return True
        return False

def payload_generate_getPricingDataByISBN(list_isbns : List) ->List:
    list_isbns = list_isbns if (isinstance(list_isbns,list)) else [list_isbns] # make sure user has is using list.
    payloads = []
    for isbn in list_isbns:
        payload = {'action': 'getPricingDataByISBN',
                'isbn': isbn,
                'container': f'pricingService-{isbn}',
                'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5",
                'country':'GBP'
                }
        payloads.append(payload)
    return payloads

def payload_generate_getPricingDataForAuthorTitleByBinding(author:str,title:str,binding:str="soft") -> List:
    """
    Parameters:
    - author (str) - book author name
    - title (str) - book title
    - binding(str) - this is the book bindingType
    """
    if binding.upper()=="HARD":
        container = "priced-from-hard"
    elif binding.upper()=="SOFT":
        container = "priced-from-soft"
    else:
        raise ValueError("Invalid parameter. Binding must be either 'hard' or 'soft'")

    payloads = [{'action': 'getPricingDataForAuthorTitleBindingRefinements',
            'an': author,
            'tn': title,
            'container': container}]
    return payloads


def payload_generate_getPricingDataForAuthorTitleBDP(author:str,title:str,binding:str="soft") -> List:
    """
    Parameters:
    - author (str) - book author name
    - title (str) - book title
    """
    payloads = [{'action': 'getPricingDataForAuthorTitleBDP',
            'an': author,
            'tn': title,
            'container': 'pricingService-'}]
    return payloads

def payload_generate_getBookRecommendationByISBN(list_isbns:List) -> List:
    list_isbns = list_isbns if (isinstance(list_isbns,list)) else [list_isbns] # make sure user has is using list.
    payloads = []
    for isbn in list_isbns:
        payload = {'pageId':'plp','itemIsbn13':isbn}
        payloads.append(payload)
    return payloads

def payload_generate_getHighlightInventoryForBookSearch(key_word : str):
    payload = [{'kn': key_word,'sortby': 30}]
    return payload