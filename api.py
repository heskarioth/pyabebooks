import asyncio
import json
from typing import List
from utils import generate_retry_intervals, payload_generate_getPricingDataByISBN, payload_generate_getPricingDataForAuthorTitleByBinding,payload_generate_getBookRecommendationByISBN, payload_generate_getPricingDataForAuthorTitleBDP, payload_generate_getHighlightInventoryForBookSearch
from data_parsers import parse_response_getPricingDataByISBN, parse_response_getBookRecommendationByISBN, parse_response_getPricingDataForAuthorTitleByBinding, parse_response_getPricingDataForAuthorTitleBDP, parse_generate_getHighlightInventoryForBookSearch
from aiohttp import ClientSession
from timing import async_timed
import aiohttp
PRICING_SERVICE_ENDPOINT = "https://www.abebooks.com/servlet/DWRestService/pricingservice"
RECOMMENDATION_SERVICE_ENDPOINT = "https://www.abebooks.com/servlet/RecommendationsApi"
HIGHLIGHTINVENTORY_SERVICE_ENDPOINT = 'https://www.abebooks.co.uk/servlet/HighlightInventory'
import pandas as pd
from typing import List
import logging
import sys
#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class AbeBooks:

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    def __init__(self):
        self.__failed_payloads = []
        self.__good_results = []
        self.history = []
    
    def clean_history(self):
        self.history = []

    async def __sendrequest(self,session:ClientSession,payload:str,url:str,method:str) -> json:
        retry_intervals,max_retries = generate_retry_intervals()
        # bug fixed below, session.request instead of session.get
        async with session.request(method,url,params=payload) as result:
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
        
        payloads = payload_generate_getPricingDataByISBN(list_isbns)

        results = await self.__sendrequest_main(payloads,PRICING_SERVICE_ENDPOINT,'POST')
        isbns =  parse_response_getPricingDataByISBN(results)
        self.history.append(isbns)
        self.__good_results = []
        return isbns


    async def __getBookRecommendationByISBN(self,list_isbns:List) -> pd.DataFrame:
        payloads = payload_generate_getBookRecommendationByISBN(list_isbns)
        
        results = await self.__sendrequest_main(payloads,RECOMMENDATION_SERVICE_ENDPOINT,'GET')
        isnbs_recommendations = parse_response_getBookRecommendationByISBN(results)
        self.history.append(isnbs_recommendations)
        self.__good_results = []
        return isnbs_recommendations

    async def __getPricingDataForAuthorTitleByBinding(self,author:str,title:str,binding:str="soft") -> json:
        """
        Parameters:
        - author (str) - book author name
        - title (str) - book title
        - binding(str) - this is the book bindingType
        """
        payloads = payload_generate_getPricingDataForAuthorTitleByBinding(author,title,binding)
        
        results = await self.__sendrequest_main(payloads,PRICING_SERVICE_ENDPOINT,'POST')
        prices = parse_response_getPricingDataForAuthorTitleByBinding(results)
        self.history.append(prices)
        self.__good_results = []
        return prices

    async def __getPricingDataForAuthorTitleBDP(self,author : str,title : str):
        payloads = payload_generate_getPricingDataForAuthorTitleBDP(author,title)
        results = await self.__sendrequest_main(payloads,PRICING_SERVICE_ENDPOINT,'POST')
        results_dict = parse_response_getPricingDataForAuthorTitleBDP(results)
        self.history.append(results_dict)
        self.__good_results = []
        return results_dict

    async def __getHighlightInventoryForBookSearch(self,key_word:str) -> pd.DataFrame:
        payloads = payload_generate_getHighlightInventoryForBookSearch(key_word)
        results = await self.__sendrequest_main(payloads,HIGHLIGHTINVENTORY_SERVICE_ENDPOINT,'POST')
        results_df = parse_generate_getHighlightInventoryForBookSearch(results)
        self.history.append(results_df)
        self.__good_results = []
        return results_df

    # asyncio.main() calls
    def getPricingDataByISBN(self,list_isbns:List):
        results = asyncio.run(self.__getPricingDataByISBN(list_isbns))
        return results

    def getBookRecommendationByISBN(self,list_isnbs:List):
        results = asyncio.run(self.__getBookRecommendationByISBN(list_isbns))
        return results
    
    def getPricingDataForAuthorTitleByBinding(self,author: str,title : str,binding:str):
        results = asyncio.run(self.__getPricingDataForAuthorTitleByBinding(author,title,binding))
        return results

    def getPricingDataForAuthorTitleBDP(self,author : str,title : str):
        #action: getPricingDataForAuthorTitleBDP
        # an: lewis
        # tn: flashboys cracking money code
        # container: pricingService-
        results = asyncio.run(self.__getPricingDataForAuthorTitleBDP(author,title))
        return results
    
    def getHighlightInventoryForBookSearch(self,key_word:str):
        results = asyncio.run(self.__getHighlightInventoryForBookSearch(key_word))
        return results

if __name__ == "__main__":
    ab = AbeBooks()
    # 9784900737396
    list_isbns = ['9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396',
    '9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396',
    '9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396',
    '9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396','9784900737396',
    ]
    #list_isbns = ['020161622X', '0804136696', '006251346X', '0802138292', '0465067107', '059313320X', '1400066638', '1878424505', '0525536558', '0735611319', '0060589469', '0316303593', '1785151126', '1947534300', '0395859999', '0385539304', '0618001905', '0415312086', '0393062139', '1572307404', '067003830X', '1610391403', '1524744182', '0061707803', '0141026839', '0140442332', '0140445625', '0140442537', '0142003786', '067003231X', '0140441239', '0316159352', '0465068405', '074347788X', '0767913736', '0670023019', '140004345X', '006093638X', '0399562710', '0316433799', '1250190517', '0062259520', '1250182190', '055380538X', '9781782397878', '0517888521', '1400049512', '0553807501', '0520070631', '0822333686', '186230002X', '8498160170', '0226124444', '1400078520', '1585673552', '0525952241', '190495538X', '1439150311', '0312330340', '014043268X', '0853459916', '0394522974', '1466860456', '0520221524', '0385489102', '0195050010', '0297852663', '0374157618', '0385469624', '0679751254', '1842121162', '0393356205', '0066620732', '1594206538', '1400047625', '0393328457', '0471468835', '1591842662', '1594201994', '1535069376', '1591846013', '0688053394', '0553293427', '0553293435', '0553293419', '0586062009', '0553299492', '0586025944', '0553803700', '0553587579', '0553293389', '0553803735', '0553803727', '0553803719', '0553565079', '0815410069', '0691089787', '0631227210', '0300047797', '0300022778', '0297776401', '0415218284', '0306804220', '0869818503', '185367303X', '0415183014', '0198148097', '1643138952', '0712618651', '1557506639', '0688151574', '0804100039', '0941419746', '1572246952', '0525953728', '0374528179', '1451611471', '1476704201', '1931836051', '0471782661', '0970693842', '1501116290', '1524760439', '0446540331', '1426217986', '0374227764', '1594486352', '0807845477', '0061138401', '0060957379', '1789291402', '1421439859', '0857526901', '0593182715', '1101982551', '0593241312', '1541600835', '0140244328', '0141000511', '1586483064', '0465027261', '1476795193', '014197981X', '0312253648', '1612004296', '1906598266', '1565122496', '133049394X', '173216892X', '099850520X', '1455583669', '0062913697', '1846141826', '0306809087', '0140036539', '0306805073', '0688060129', '0306805839', '030680686X', '019086902X', '1473826489', '050025124X', '0500251517', '1782438564', '1844158349', '1529301491', '159420411X', '0006380727', '1635573955', '1605208329', '0751579017', '0063018950', '0300179049', '0316584789', '1684511526', '1860460720', '1641711310', '1476777284', '1501153781', '0425286525', '0300230621', '0140114068', '140006662X', '1451668791', '0140442103', '0060925973', '030011575X', '0679400699', '0306801574', '0060920203', '0670067172', '8880861840', '081541224X', '0300102623', '0300105134', '0020493614', '0465028020', '0241300657', '0393324842', '014024364X', '0767900561', '0700608990', '0771009305', '0688029639', '0062570889', '1847922872', '1469065541', '0805062904', '0805062890', '0805062882', '1594202060', '1594200742', '0143034693', '1250131200', '1619026074', '0385537603', '1632864215', '1620403471', '0195085574', '154605958X', '0747595089', '0670021415', '0385515693', '0316409138', '0739467352', '0030403065', '0300190727', '1920694102', '0813335116', '0300057520', '1439183201', '1505114446', '1841155047', '0393352242', '0691091943', '0525533834', '0241309727', '1400067960', '0471677744', '1118494563', '0471249483', '1846684307', '0140443185', '014044145X', '0140443886', '1591843529', '0316461369', '0008340927', '0520208234', '0195168941', '1594202664', '1582340455', '0802135749', '0593152387', '0552168807', '0393059766', '0393059758', '0304366420', '1497637902', '0141020768', '0307271641', '0691212465', '0241256992', '0307273598', '0684829495', '1594206791', '0802135587', '0374280746', '0262019124', '1501183087', '0802127436', '0593084349', '1594202710', '1541768132', '1324003294', '1328846024', '0190239034', '1541742400', '0300234031', '1408889463', '080211959X', '0674055446', '0316547700', '0385313314', '0385313489', '0670025321', '1118172760', '0190495995', '0857197681', '0753556383', '0955576601', '0070504776', '085294134X', '0684811634', '0684829703', '0231153686', '0285630954', '0887305105', '0684840073', '0761526463', '1760295329', '0307952207', '1568493673', '1472130847', '9747100819', '9747551152', '1891620002', '0786713151', '0719565693', '0060578637', '1634312023', '1250041821', '1605981729', '1846270405', '1250024986', '4770019572', '1538733307', '006300187X', '1982132515', '0679726101', '1472942248', '1250200911', '0593098250', '0593098242', '0593098234', '059309932X', '0984358161', '0691167702', '0738285323', '0813332915', '0060803320', '006092103X', '0060007761', '0691130833', '1973170876', '1591810329', '1781556784', '0804835659', '0691175578', '0140449434', '0743223136', '0375756787', '1400032059', '1416591052', '1473637465', '152473165X', '0071453393', '0805092641', '0199678111', '0470627603', '0345341848', '0670022756', '1101981059', '0898865743', '1567310249', '0812993012', '0670025291', '0143037889', '031622104X', '1422162672', '0735213658', '0241294223', '0449908704', '0393339750', '0297845675', '0374529264', '0440243904', '1599869942', '046509760X', '150114331X', '1108425046', '1492056359', '0262032937', '0134034287', '0393330435', '0805079831', '0812969642', '0310501504', '156849095X', '0593139135', '9781929631285', '0393355683', '1541675819', '1847925685', '1400063256', '1400077303', '0521856027', '1846681383', '1842124196', '0316380504', '0316037702', '0743286979', '1982115858', '0596002874', '0596001088', '8896904501', '0710813732', '067473047X', '0837138159', '0140069321', '1929631057', '0415175429', '8390699273', '0872203549', '0141007540', '1594201927', '0241488443', '0679747044', '038541580X', '0593423062', '0063001705', '9781940003009', '1541647467', '1615773762', '0679729526', '1398510394', '8874801734', '0684871521', '1324001542', '1982538503', '0253213053', '0375708227', '0300119852', '147282945X', '1786078929', '0875806341', '1511524170', '0340193883', '0875807224', '0312055102', '125003356X', '0688047831', '0767908791', '0385177003', '0316103993', '0415932149', '0751531995', '1591149266', '150176005X', '0674022130', '0306808609', '0385420536', '9780955274480', '0618688226', '0195119126', '0316727237', '1400069335', '1509511202', '0425244237', '0394710355', '0374118256', '1853674990', '0306811014', '1403973083', '0465003370', '0060927623', '8806176552', '0304356972', '0803259239', '8817125733', '0307453421', '110187032X', '0684824299', '0340394633', '080185668X', '1546090789', '030681076X', '0691027641', '0192854070', '1400078857', '0684832720', '156663721X', '1578644283', '1408701537', '1594205582', '0812967852', '1590304519', '1566630193', '1781556865', '0743200403', '0691010935', '0306806614', '0300221932', '1480401595', '1605981397', '0252064798', '1862075522', '0853035253', '0307715531', '1474608124', '0802128394', '0552172030', '056349333X', '0966638980', '0226511928', '0691018545', '1426215509', '0316544981', '0307887995', '0306813041', '0385535376', '038549565X', '0834800799', '1844137481', '0812970586', '067443000X', 'B08YFLJ55H', '0300100981', '1416532056', '1250104629', '0671216767', '0547669194', '0691176949', '1451651139', '0306806983', '0486433986', '1681771675', '0316435120', '0199592322', '0465093817', '0300137192', '081298367X', '0812968581', '1599951495', '0393082415', '0679768122', '0691166838', '1250162505', '1524762938', '0312426526', '0374277893', '0330346970', '0141390123', '1610399641', '147677725X', '0312622376', '1594487715', '0465097952', '1567926118', '0300180276', '0374201234', '0984358102', '0316530204', '1508279144', '1623366909', '0385528752', '163286830X', '1591840538', '0812995805', '1471113566', '0062839349', '1610397215', '1439102171', '1416592806', '0300178727', '0743289536', '0060787287', '074326049X', '039305974X', '037575895X', '0060518502', '0393358046', '0143036556', '0375508325', '1590300572', '1461471370', '0735214484', '1541646851', '132854639X', '0451485076', '0007547994', '1250237238', '0544935276', '1594203792', '0062405667', '0788163728', '0670022950', '0553805096', '0785289089', '0814472788', '1594487154', '1932429247', '159285849X', '0446691437', '1861977697', '0544634497', '1250103509', '1592407331']
    #list_isbns = ['9784900737396','9784900737396','9784900737396','9784900737396','9784900737396']
    # 31
    list_isbns = '9784900737396'
    ## This method will find me the cheapest.
    #r =  ab.getPricingDataByISBN(list_isbns)
    #r.to_csv('trying.csv',index=False)
    #x = ab.getBookRecommendationByISBN(list_isbns)
    print('das')
    #r = ab.getPricingDataForAuthorTitleByBinding("david goggins","can't hurt me","hard")
    #r= ab.getPricingDataForAuthorTitleBDP("david goggins","can't hurt me")
    r = ab.getHighlightInventoryForBookSearch('9780316017923')
    print("========================")
    #print(ab.history)
    print("============")
    print(r)
