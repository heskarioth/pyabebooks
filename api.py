#improvements to make:
# parsing and handling of json response to dataframe

import asyncio
import json
from typing import List
import aiohttp
from utils import generate_retry_intervals
from data_parsers import parse_response_getPricingDataByISBN, parse_response_getBookRecommendationByISBN, parse_response_getPricingDataForAuthorTitleByBinding
from aiohttp import ClientSession
from timing import async_timed
import aiohttp
PRICING_SERVICE_ENDPOINT = "https://www.abebooks.com/servlet/DWRestService/pricingservice"
RECOMMENDATION_SERVICE_ENDPOINT = "https://www.abebooks.com/servlet/RecommendationsApi"
import pandas as pd

import logging
from typing import Callable, Awaitable
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class AbeBooks:

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    def __init__(self):
        self.__failed_payloads = []
        self.__good_results = []
        self.history = []
    
    async def __sendrequest(self,session:ClientSession,payload:str,url:str,method:str) -> json:
        retry_intervals,max_retries = generate_retry_intervals()
        async with session.get(url,params=payload) as result:
            if result.status!=200:
                for idx, retry_num in enumerate(range(0,max_retries)):
                    async with session.request(method,url,params=payload) as result:
                    #async with session.get(url,params=payload) as result:
                        if result.status==200:
                            result = await result.json()
                            return result
                    await asyncio.sleep(retry_intervals[idx])
                
                # we want our object to return us the actual error code
                self.__failed_payloads.append(payload)
                #logging.exception('this is an exception', exc_info=False)
                raise aiohttp.ClientError()
            
            response = await result.json()
            
            return response
    

    @async_timed()
    async def __sendrequest_main(self,payloads:List,url:str,method) ->json:
        
        """
        Parameters:
        - list_isbns (list) - list of isnbs13 books
        """
        # we also have to limit number of connections on client settings.
        async with ClientSession() as session:
            
            pending = [asyncio.create_task(self.__sendrequest(session,payload,url,method)) for payload in payloads]
            self.__good_results = []
            
            while pending:
                done, pending = await asyncio.wait(pending,return_when=asyncio.FIRST_EXCEPTION)
                
                print(f'Done tasks:{len(done)}')
                print(f'Pending tasks:{len(pending)}')
                
                for done_task in done:
                    if done_task.exception() is None:
                        self.__good_results.append(await done_task)
                    else:
                        new_tasks = [asyncio.create_task(self.__sendrequest(session,payload,url,method)) for payload in self.__failed_payloads]
                        self.__failed_payloads = []
                        for new_task in new_tasks:
                            pending.add(new_task)
            
            
            return self.__good_results
    
    ## funcs for endpoint mains
    async def __getPricingDataByISBN(self, list_isbns : List) ->pd.DataFrame:
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

        results = await self.__sendrequest_main(payloads,PRICING_SERVICE_ENDPOINT,'POST')
        isbns =  parse_response_getPricingDataByISBN(results)
        self.history.append(isbns)
        self.__good_results = []
        return isbns


    async def __getBookRecommendationByISBN(self,list_isbns:List) -> pd.DataFrame:
        list_isbns = list_isbns if (isinstance(list_isbns,list)) else [list_isbns] # make sure user has is using list.
        payloads = []
        for isbn in list_isbns:
            payload = {'pageId':'plp','itemIsbn13':isbn}
            payloads.append(payload)

        results = await self.__sendrequest_main(payloads,RECOMMENDATION_SERVICE_ENDPOINT,'GET')
        isnbs_recommendations = parse_response_getBookRecommendationByISBN(results)
        self.history.append(isnbs_recommendations)
        self.__good_results = []
        return isnbs_recommendations

    async def __getPricingDataForAuthorTitleByBinding(self,author,title,binding="soft") -> json:
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
            
            results = await self.__sendrequest_main(payloads,PRICING_SERVICE_ENDPOINT,'POST')
            prices = parse_response_getPricingDataForAuthorTitleByBinding(results)
            self.history.append(prices)
            self.__good_results = []
            return prices




    # asyncio.main() calls
    def getPricingDataByISBN(self,list_isbns):
        results = asyncio.run(self.__getPricingDataByISBN(list_isbns))
        return results

    def getBookRecommendationByISBN(self,list_isnbs):
        results = asyncio.run(self.__getBookRecommendationByISBN(list_isbns))
        return results
    
    def getPricingDataForAuthorTitleByBinding(self,author,title,binding):
        results = asyncio.run(self.__getPricingDataForAuthorTitleByBinding(author,title,binding))
        return results

if __name__ == "__main__":
    ab = AbeBooks()
    # 9784900737396
    list_isbns = ['9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396',
    '9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396',
    '9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396',
    '9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396',
    ]
    #list_isbns = ['9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396']
    # 31
    #list_isbns = '9784900737396'
    ## This method will find me the cheapest.
    #r =  ab.getPricingDataByISBN(list_isbns)
    #r.to_csv('trying.csv',index=False)
    #x = ab.getBookRecommendationByISBN(list_isbns)
    #x.to_csv('rec.csv',index=False)
    r = ab.getPricingDataForAuthorTitleByBinding("david goggins","can't hurt me","hard")
    #r = ab.getPricingDataForAuthorTitleByBinding("david goggins","can't hurt me","soft")
    #r = ab.getBookRecommendationByISBN("9784900737396")
    print(r)
