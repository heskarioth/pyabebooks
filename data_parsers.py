import pandas as pd
import numpy as np
from typing import List, Dict
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


def parse_response_getPricingDataForAuthorTitleBDP(response : List) -> Dict:
    response = response[0]

    dict_prices = {}
    if response['success']==False:
        return {'msg':'No book found with searching criterias.'}

    if response['pricingInfoForBestUsed'] is None:
        used_shipping_cost = np.nan
        dict_prices['used_shipping_cost'] = np.nan
        dict_prices['used_price'] = np.nan
    else:
        used_shipping_cost = response['pricingInfoForBestUsed']['domesticShippingPriceInPurchaseCurrencyWithCurrencySymbol'] if response['pricingInfoForBestUsed']['vendorCountryNameInSurferLanguage'] =='United Kingdom' else response['pricingInfoForBestUsed']['shippingToDestinationPriceInPurchaseCurrencyWithCurrencySymbol']
        dict_prices['used_shipping_cost'] = float((re.compile(r'[^\d.,]+').sub('', used_shipping_cost)).replace(',','.'))
        dict_prices['used_price'] = float(response['pricingInfoForBestUsed']['nonPaddedPriceInListingCurrencyValueOnly'])
    if response['pricingInfoForBestNew'] is None:
        new_shipping_cost = np.nan
        dict_prices['new_shipping_cost'] = np.nan
        dict_prices['new_price'] = np.nan
    else:
        new_shipping_cost = response['pricingInfoForBestNew']['domesticShippingPriceInPurchaseCurrencyWithCurrencySymbol'] if response['pricingInfoForBestNew']['vendorCountryNameInSurferLanguage'] =='United Kingdom' else response['pricingInfoForBestNew']['shippingToDestinationPriceInPurchaseCurrencyWithCurrencySymbol']
        dict_prices['new_shipping_cost'] = float((re.compile(r'[^\d.,]+').sub('', new_shipping_cost)).replace(',','.'))
        dict_prices['new_price'] = float(response['pricingInfoForBestNew']['nonPaddedPriceInListingCurrencyValueOnly'])
    dict_prices['new_total'] = dict_prices['new_shipping_cost'] + dict_prices['new_price']
    dict_prices['used_total'] = dict_prices['used_shipping_cost'] + dict_prices['used_price']
    
    url_base = 'https://www.abebooks.co.uk/servlet/SearchResults?'
    df_book_options = pd.DataFrame(response['refinementList'])
    
    df_book_options['url'] = df_book_options['url'].str.replace('an=',url_base+'an=')
    dict_response = {}
    dict_response['pricing_info'] = dict_prices
    dict_response['book_options'] = (df_book_options.to_dict('records'))
    return dict_response


def parse_generate_getHighlightInventoryForBookSearch(response : Dict) -> pd.DataFrame:
    columns = list(response[0]['highlightedItemsMap'].keys())
    df_response = pd.DataFrame()
    for column in columns:
        for i in range(len(response[0]['highlightedItemsMap'][column])):
            df_response = pd.concat([df_response,pd.DataFrame([response[0]['highlightedItemsMap'][column][i]])])
    df_response = df_response.drop(['bsaCodes','priceInDomainCurrency'],axis=1)
    return df_response