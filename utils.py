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

def parse_response_getPricingDataByISBN(list_responses: List) -> pd.DataFrame:
    df_responses = pd.DataFrame()
    
    for response in list_responses:
        dict_response = {}
        dict_response['title'] = ''
        dict_response['isbn'] = response['isbn']
        dict_response['author'] = ''
        dict_response['publisher'] = ''
        dict_response['marketplace'] = 'abebooks'
        if response['pricingInfoForBestUsed'] is None:
            used_shipping_cost = np.nan
            dict_response['used_shipping_cost'] = np.nan
            dict_response['used_price'] = np.nan
        else:
            used_shipping_cost = response['pricingInfoForBestUsed']['domesticShippingPriceInPurchaseCurrencyWithCurrencySymbol'] if response['pricingInfoForBestUsed']['vendorCountryNameInSurferLanguage'] =='United Kingdom' else response['pricingInfoForBestUsed']['shippingToDestinationPriceInPurchaseCurrencyWithCurrencySymbol']
            dict_response['used_shipping_cost'] = float((re.compile(r'[^\d.,]+').sub('', used_shipping_cost)).replace(',','.'))
            dict_response['used_price'] = float(response['pricingInfoForBestUsed']['nonPaddedPriceInListingCurrencyValueOnly'])
        if response['pricingInfoForBestNew'] is None:
            new_shipping_cost = np.nan
            dict_response['new_shipping_cost'] = np.nan
            dict_response['new_price'] = np.nan
        else:
            new_shipping_cost = response['pricingInfoForBestNew']['domesticShippingPriceInPurchaseCurrencyWithCurrencySymbol'] if response['pricingInfoForBestNew']['vendorCountryNameInSurferLanguage'] =='United Kingdom' else response['pricingInfoForBestNew']['shippingToDestinationPriceInPurchaseCurrencyWithCurrencySymbol']
            dict_response['new_shipping_cost'] = float((re.compile(r'[^\d.,]+').sub('', new_shipping_cost)).replace(',','.'))
            dict_response['new_price'] = float(response['pricingInfoForBestNew']['nonPaddedPriceInListingCurrencyValueOnly'])
        dict_response['new_total'] = dict_response['new_shipping_cost'] + dict_response['new_price']
        dict_response['used_total'] = dict_response['used_shipping_cost'] + dict_response['used_price']
        dict_response['urlPurchase'] = 'https://www.abebooks.co.uk/servlet/SearchResults?bi=0&bx=off&cm_sp=SearchF-_-Advtab1-_-Results&fe=off&ds=30&{}'.format(response['refinementList'][0]['url']) if response['success']==True else ''
        df_responses = pd.concat([df_responses,pd.DataFrame(dict_response,index=[0])])
    
    return df_responses.reset_index(drop=True)