#improvements to make:
# parsing and handling of json response to dataframe

import json
from xmlrpc.client import Boolean
from utils import check_response
import requests
PRICING_SERVICE_ENDPOINT = "https://www.abebooks.com/servlet/DWRestService/pricingservice"
RECOMMENDATION_SERVICE_ENDPOINT = "https://www.abebooks.com/servlet/RecommendationsApi"


class AbeBooks:

    def __init__(self):
        self.client = requests.Session()

    def __getprice(self,url,payload)->json:
        response = self.client.post(url,data=payload)
        if check_response(response.json(),'price'):
            return response.json()
        else:
            return 'Book not found'

    def getPricingDataByISBN(self,isbn) ->json:
        """
        Parameters:
        - isbn (int) - a book's ISBN13 code
        """
        payload = {'action': 'getPricingDataByISBN',
                   'isbn': isbn,
                   'container': f'pricingService-{isbn}',
                   'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5",
                   'country':'GBP'
                   }

        return self.__getprice(PRICING_SERVICE_ENDPOINT,payload)


    def getPricingDataForAuthorTitleByBinding(self,author,title,binding="soft") -> json:
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

        payload = {'action': 'getPricingDataForAuthorTitleBindingRefinements',
                   'an': author,
                   'tn': title,
                   'container': container}

        return self.__getprice(PRICING_SERVICE_ENDPOINT,payload)

    def getBookRecommendationByISBN(self,isbn):
        """
        Parameters:
        - isbn (str) - book isbn13
        """ 
        payload = {
            'pageId':'plp',
            'itemIsbn13':isbn
        }
        response = requests.get(RECOMMENDATION_SERVICE_ENDPOINT,params=payload)
        #print(response.raise_for_status(),response.status_code)
        #return response.json()
        if check_response(response.json(),'recommendation'):
            return response.json()
        else:
            return 'No recommendations found, make sure you searched for the right ISBN'

if __name__ == "__main__":
    ab = AbeBooks()
    # 9784900737396
    #r = ab.getPricingDataByISBN("9784900737396")
    #r = ab.getPricingDataForAuthorTitleByBinding("david goggins","can't hurt me","hard")
    #r = ab.getPricingDataForAuthorTitleByBinding("david goggins","can't hurt me","soft")
    r = ab.getBookRecommendationByISBN("9784900737396")
    print(r)

