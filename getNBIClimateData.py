import requests
import re
import ast
import pandas as pd


def getBridgeList(url, headers, totalpages=3, pagesize=10, totalbridges=24):

    bridgerecords = []

    for pageno in range(1, totalpages + 1):

        data = '{"isShowBridgesApplied":true,"gridParam":{"isShowBridgesApplied":true,"PageNumber":' + str(pageno) + ',\
        "PageSize":' + str(pagesize) + ',"SortOrder":"asc","SortIndex":"STATE_NAME","IsFilterApplied":false,"SelectedFilters":null}}'

        r = requests.post(url, headers=headers, data=data)

        print(r.status_code)

        htmlcontent = r.content.decode('utf-8')
        print(htmlcontent)

        htmlcontent = htmlcontent.replace('\\', '')

        currentpageinfo = re.findall(r'"page":\d+', htmlcontent)
        currentpageinfo = int(re.findall(r'\d+', currentpageinfo[0])[0])

        totalpageinfo = re.findall(r'"page":\d+', htmlcontent)
        totalpageinfo = int(re.findall(r'\d+', totalpageinfo[0])[0])

        totalrecords = re.findall(r'"page":\d+', htmlcontent)
        totalrecords = int(re.findall(r'\d+', totalrecords[0])[0])

        if totalrecords != totalbridges or totalpageinfo != totalpages:
            Exception('Check the number of total bridges')

        bridgeinfo = re.findall(r'{"FEATURE_INTERSECTED":.+"STATE_CODE":\d+}', htmlcontent)[0]
        bridgeinfo = bridgeinfo[1:-1]
        bridgeinfo = bridgeinfo.replace('null', 'None')
        bridgeinfo = bridgeinfo.split('},{')

        for bridge in bridgeinfo:
            bridgerecords.append(eval('{' + bridge + '}'))

    bridgeTable = pd.DataFrame(bridgerecords)
    bridgeTable.to_csv('./bridgeTable.csv', index=False)

    return None


def getClimateData(url, headers, bridgeTable, YEAR_RANGE):

    for _, bridgerow in bridgeTable.iterrows():

        BRIDGE_YEARLY_ID = bridgerow['BRIDGE_YEARLY_ID']
        STRUCTURE_NUMBER = bridgerow['STRUCTURE_NUMBER']

        bridgeClimateDict = []

        for SELECTED_YEAR in YEAR_RANGE:
            myheaders = headers.copy()
            myheaders['referer'] = headers['referer'] + str(BRIDGE_YEARLY_ID)

            payload = '{"requestModel":{"SELECTED_TAB":"CLIMATE_TAB","SELECTED_YEAR_ID":null,"IS_NEW_RECORD":false,\
            "IS_YEAR_SELECTED":true,"Is_Overview_Bridge_Selected":false,"SELECTED_YEAR":' + str(SELECTED_YEAR) + ',\
            "CURRENT_YEARLY_ID":' + str(BRIDGE_YEARLY_ID) + ',"BRIDGE_YEARLY_ID":' + str(BRIDGE_YEARLY_ID) + ',"STRUCTURE_NUMBER":null,\
            "STATE_NAME":null,"STATE_CODE":0,"SELECTED_NDE_TAB":"General"}}'

            r = requests.post(url, data=payload, headers=myheaders)

            print(r.status_code)

            htmlcontent = r.content.decode('utf-8')
            print(htmlcontent)

            climatedata = re.findall(r'{"MONTH":\d+,"NO_OF_FREEZE_THAW_CYCLES":\d+,"NO_OF_SNOWFALLS":\d+,"YEAR":\d+}', htmlcontent)

            for v in climatedata:
                monthclimate = ast.literal_eval(v)
                print(monthclimate)
                bridgeClimateDict.append(monthclimate)

        bridgeClimateTable = pd.DataFrame(bridgeClimateDict)
        bridgeClimateTable['STRUCTURE_NUMBER'] = STRUCTURE_NUMBER
        bridgeClimateTable.to_csv('./bridgeClimateTable{}.csv'.format(STRUCTURE_NUMBER), index=False)
    return None


if __name__ == '__main__':

    bridgelisturl = 'https://infobridge.fhwa.dot.gov/Data/GetAllBridges'

    bridgelistheaders = {
        'authority': 'infobridge.fhwa.dot.gov',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'origin': 'https://infobridge.fhwa.dot.gov',
        'x-requested-with': 'XMLHttpRequest',
        '__requestverificationtoken': 'jNqRlPdI4VvCve0Z0Lto_UJKLpFigd04TPqa8HJ2pTRQM233ND3hoOmLW2viUGqGp_CmsaEzlF_2lp-o7T3cdeXTchiB4R8FShfkq7oAXQo1',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'content-type': 'application/json; charset=UTF-8',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'referer': 'https://infobridge.fhwa.dot.gov/Data',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': '_ga=GA1.3.1278235848.1520435010; _ga=GA1.2.1278235848.1520435010; __RequestVerificationToken=CETzxgkjr5wXm0qTfDKbMSBe0wZ5nrzoLpMRVR_eW7yQrU2jDCyUPzlMPlWFgI7zaxbX3bPRRuDR-_GE8ALnaFaIa6cGH9wlthc6eLzn7zI1; mf_user=9a9e7d2d9673fdf31f5a5cc6683c7d6c|; _gid=GA1.2.17339652.1574358314; _ga=GA1.4.1278235848.1520435010; _gid=GA1.4.17339652.1574358314; ASP.NET_SessionId=bb3ocnlezwx0t2k0bfkq2vqx; _gid=GA1.3.17339652.1574358314; fsr.s=%7B%22v%22%3A1%2C%22rid%22%3A%22d489c26-86010607-4db3-5228-f9b76%22%2C%22ru%22%3A%22https%3A%2F%2Fops.fhwa.dot.gov%2Ffreight%2Ffreight_analysis%2Ffaf%2F%22%2C%22r%22%3A%22ops.fhwa.dot.gov%22%2C%22st%22%3A%22%22%2C%22to%22%3A5%2C%22c%22%3A%22https%3A%2F%2Fwww.fhwa.dot.gov%2Fbridge%2Fnbi.cfm%22%2C%22pv%22%3A62%2C%22lc%22%3A%7B%22d0%22%3A%7B%22v%22%3A62%2C%22s%22%3Atrue%7D%7D%2C%22cd%22%3A0%2C%22f%22%3A1574371901468%2C%22sd%22%3A0%2C%22i%22%3A-1%2C%22l%22%3A%22en%22%7D; _gat_gtag_UA_40700489_3=1; _gat=1; mf_e97d6d64-229c-4593-89ab-df7e7ad80fc7=bb04debc29d5ecc66a9c6ccd3427ebda|11214514ee09c76ed318085d95ea7902b106f443.-4352357568.1574374365516$1121417636e7a66f169991b6329c5bc009f71c4e.-4356138953.1574378261478$11215627c7c7c480be542159da0f9710776d54a8.-4356138953.1574378276629$112138577b10e9ba588893309685ae015d0e41b7.-4274963525.1574381018760$112221338616415a57e8202744d30d0488fc09b1.45528185.1574431821935|1574431831949||1|||0|16.22|5',
    }

    getBridgeList(bridgelisturl, bridgelistheaders, totalpages=2, pagesize=10, totalbridges=18)

    bridgeTable = pd.read_csv('./bridgeTable.csv')
    YEAR_RANGE = range(1980, 2018)

    bridgeurl = 'https://infobridge.fhwa.dot.gov/Data/getBridgeInformation'

    bridgeheaders = {
        'authority': 'infobridge.fhwa.dot.gov',
        'accept': 'application/json, text/plain, */*',
        'origin': 'https://infobridge.fhwa.dot.gov',
        'datatype': 'json',
        '__requestverificationtoken': '_3CsMuVx3bohKZoO7sUUfAQbmg74M-a06WzgEKDmwPljP3RUjf5Wgl-7rcNzJUMjZOdS1Pokpqqxf4hwuZvS0yckOSgZ_4-wYZOqhCch1mE1',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'content-type': 'application/json; charset=UTF-8',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'referer': 'https://infobridge.fhwa.dot.gov/Data/BridgeDetail/',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': '_ga=GA1.3.1278235848.1520435010; _ga=GA1.2.1278235848.1520435010; __RequestVerificationToken=CETzxgkjr5wXm0qTfDKbMSBe0wZ5nrzoLpMRVR_eW7yQrU2jDCyUPzlMPlWFgI7zaxbX3bPRRuDR-_GE8ALnaFaIa6cGH9wlthc6eLzn7zI1; mf_user=9a9e7d2d9673fdf31f5a5cc6683c7d6c|; _gid=GA1.2.17339652.1574358314; _ga=GA1.4.1278235848.1520435010; _gid=GA1.4.17339652.1574358314; ASP.NET_SessionId=bb3ocnlezwx0t2k0bfkq2vqx; _gid=GA1.3.17339652.1574358314; fsr.s=%7B%22v%22%3A1%2C%22rid%22%3A%22d489c26-86010607-4db3-5228-f9b76%22%2C%22ru%22%3A%22https%3A%2F%2Fops.fhwa.dot.gov%2Ffreight%2Ffreight_analysis%2Ffaf%2F%22%2C%22r%22%3A%22ops.fhwa.dot.gov%22%2C%22st%22%3A%22%22%2C%22to%22%3A5%2C%22c%22%3A%22https%3A%2F%2Fwww.fhwa.dot.gov%2Fbridge%2Fnbi.cfm%22%2C%22pv%22%3A62%2C%22lc%22%3A%7B%22d0%22%3A%7B%22v%22%3A62%2C%22s%22%3Atrue%7D%7D%2C%22cd%22%3A0%2C%22f%22%3A1574371901468%2C%22sd%22%3A0%2C%22i%22%3A-1%2C%22l%22%3A%22en%22%7D; _gat_gtag_UA_40700489_3=1; _gat=1; mf_e97d6d64-229c-4593-89ab-df7e7ad80fc7=bb04debc29d5ecc66a9c6ccd3427ebda|1121417636e7a66f169991b6329c5bc009f71c4e.-4356138953.1574378261478$11215627c7c7c480be542159da0f9710776d54a8.-4356138953.1574378276629$112138577b10e9ba588893309685ae015d0e41b7.-4274963525.1574381018760$112221338616415a57e8202744d30d0488fc09b1.45528185.1574431821935$112215694f2b2cf135c2b6118043abfa52cd2afb.-4356138953.1574432655271|1574432672174||2|||0|16.22|5',
    }

    getClimateData(bridgeurl, bridgeheaders, bridgeTable, YEAR_RANGE)
