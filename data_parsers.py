import pandas as pd
import numpy as np
from typing import List
import re 


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


def parse_response_getBookRecommendationByISBN(responses):
    
    df_responses = pd.DataFrame()
    
    for response in responses:
        
        df_response = pd.DataFrame(response['widgetResponses'][0]['recommendationItems'])
        
        df_response = df_response[['isbn13','title', 'author', 'thumbNailImgUrl', 'itemLink',]]

        
        df_responses = pd.concat([df_responses,df_response])
        
    return df_responses.reset_index(drop=True)


def parse_response_getPricingDataForAuthorTitleByBinding(results):
    for results in results:
        if results['pricingInfoForBestAllConditions'] is None:
            raise ValueError('Book not found.')
        return pd.DataFrame(results['pricingInfoForBestAllConditions'],index=[0])