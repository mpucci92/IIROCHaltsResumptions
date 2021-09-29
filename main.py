import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
from lxml import etree
import codecs
from datetime import date, timedelta, datetime
import calendar

HistoricalFinalHaltsData = []
HistoricalFinalResumptionData = []


def historicalHaltsInformation(haltsHistorical):
    finalHalts = []

    for url in haltsHistorical:
        resp = requests.get(url)

        halt_information = []

        for element in BeautifulSoup(resp.content, 'html.parser').find_all('p'):
            element = element.text.replace('\xa0', ' ')
            halt_information.append(element)

        # print(halt_information)
        infoHalts = {}
        for i in range(len(halt_information)):
            if i == 0:
                # datetime = datetime.strptime(str(halt_information[i]), '%b %d, %Y')
                # datetime = datetime.date()
                infoHalts['timestamp'] = halt_information[i].strip()

            if 'Company:' in halt_information[i]:
                try:
                    company = halt_information[i].split(":")[1]
                    infoHalts['company'] = re.sub(r'[^A-Za-z0-9 ]+', '', company.strip())
                except Exception as e:
                    pass

            if 'Symbol' in halt_information[i]:
                try:
                    ticker = halt_information[i].split(":")[1]
                    infoHalts['ticker'] = ticker.strip()
                except Exception as e:
                    pass

            if 'Reason' in halt_information[i]:
                try:
                    reason = halt_information[i].split(":")[1]
                    infoHalts['reason'] = reason.strip()
                except Exception as e:
                    pass

            if 'Halt Time (ET):' in halt_information[i]:
                # print(halt_information[i])
                try:
                    haltTime = halt_information[i].split(": ")[1]
                    infoHalts['halt_timestamp'] = haltTime.strip()
                except Exception as e:
                    pass

        finalHalts.append(infoHalts)

    return finalHalts


def historicalResumptionsInformation(resumptionsHistorical):
    finalResumptions = []

    for url in resumptionsHistorical:
        resp = requests.get(url)

        halt_information = []

        for element in BeautifulSoup(resp.content, 'html.parser').find_all('p'):
            element = element.text.replace('\xa0', ' ')
            halt_information.append(element)

        # print(halt_information)
        infoResumptions = {}
        for i in range(len(halt_information)):
            if i == 0:
                infoResumptions['timestamp'] = halt_information[i].strip()

            if 'Company:' in halt_information[i]:
                try:
                    # print(halt_information[i])
                    company = halt_information[i].split(":")[1]
                    infoResumptions['company'] = re.sub(r'[^A-Za-z0-9 ]+', '', company.strip())
                except Exception as e:
                    pass

            if 'Symbol' in halt_information[i]:
                try:
                    ticker = halt_information[i].split(":")[1]
                    infoResumptions['ticker'] = ticker.strip()
                except Exception as e:
                    pass

            if 'Resumption (ET):' in halt_information[i]:
                try:
                    reason = halt_information[i].split(": ")[1]
                    infoResumptions['resumption_timestamp'] = reason.strip()
                except Exception as e:
                    pass

        finalResumptions.append(infoResumptions)

    return finalResumptions


def timestampPostProcess(finalHalts, finalResumptions):
    for i, value in enumerate(finalHalts):
        input_ = value['timestamp']
        format_ = '%b %d, %Y'

        date_1 = datetime.strptime(input_, '%b %d, %Y')
        date = date_1.date().strftime("%Y-%m-%d")
        finalHalts[i]['timestamp'] = date

    for i, value in enumerate(finalResumptions):
        input_ = value['timestamp']
        format_ = '%b %d, %Y'

        date_1 = datetime.strptime(input_, '%b %d, %Y')
        date = date_1.date().strftime("%Y-%m-%d")
        finalResumptions[i]['timestamp'] = date


def cleanTimeHalts(haltdf):
    clean_time = []
    final_clean_time = []
    final_clean_date = []
    final_timestamp = []

    for i in range(len(haltdf)):
        time = re.sub(r'[^A-Za-z0-9: ]+', '', str(haltdf['halt_timestamp'].iloc[i]).strip())
        time = time.replace(" ", ":00")
        time = time.replace("AM", " AM")
        time = time.replace("am", " AM")
        time = time.replace("PM", " PM")
        if ('AM' and 'PM') not in time:

            if int(time.split(":")[0]) > 6 and int(time.split(":")[0]) < 12:
                time = time + " " + 'AM'
            else:
                time = time + " " + 'PM'

        time = time.replace("AM AM", "AM")
        time = time.replace(" PM", ":00 PM")
        time = time.replace(" AM", ":00 AM")
        time = time[0:7] + " " + time[-2] + time[-1]

        clean_time.append(time)

    for time in pd.to_datetime(clean_time):
        final_clean_time.append(time.isoformat().split('T')[-1])

    for i in range(len(haltdf)):
        final_clean_date.append(pd.to_datetime(haltdf.timestamp.iloc[i]).isoformat().split('T')[0])

    for i, val in enumerate(final_clean_date):
        timestamp = val + " " + final_clean_time[i]
        final_timestamp.append(timestamp)

    return final_timestamp

def cleanTimeResumptions(resumptiondf):

    clean_time = []
    final_clean_time = []
    final_clean_date = []
    final_timestamp = []

    for i in range(len(resumptiondf)):
        time = re.sub(r'[^A-Za-z0-9: ]+', '',str(resumptiondf['resumption_timestamp'].iloc[i]).strip())
        time = time.replace(" ",":00")
        time = time.replace("AM"," AM")
        time = time.replace("am"," AM")
        time = time.replace("PM"," PM")
        if ('AM' and 'PM') not in time:

            if int(time.split(":")[0]) > 6 and int(time.split(":")[0]) < 12:
                time = time +" "+ 'AM'
            else:
                time = time + " "+ 'PM'

        time = time.replace("AM AM","AM")
        time = time.replace(" PM",":00 PM")
        time = time.replace(" AM",":00 AM")
        time = time[0:7] +" "+time[-2] +time[-1]

        clean_time.append(time)

    for time in pd.to_datetime(clean_time):
         final_clean_time.append(time.isoformat().split('T')[-1])

    for i in range(len(resumptiondf)):
        final_clean_date.append(pd.to_datetime(resumptiondf.timestamp.iloc[i]).isoformat().split('T')[0])

    for i,val in enumerate(final_clean_date):
        timestamp = val + " " + final_clean_time[i]
        final_timestamp.append(timestamp)

    return final_clean_time,final_timestamp

def adjTimeResumption(resumptiondf):
    adj_date = []
    for index,time in enumerate(resumptiondf.resumption_timestamp):
        if '/' in time:
            for value in time.split(' '):
                if '/' in value:
                    resumptiondf.date.iloc[index] = ((str(pd.to_datetime(value,format='%m/%d/%Y')).split(' ')[0])) + " " + resumptiondf.clean_time.iloc[index]

if __name__ == '__main__':

    base_url_historical = 'https://iiroc.mediaroom.com/index.php?o='
    setting1 = [str(i) for i in range(0, 100, 25)]
    url_year = '&s=2429&year='
    setting2 = [str(i) for i in range(2021, 2022, 1)]

    for value2 in setting2:
        for value1 in setting1:
            complete_url = base_url_historical + value1 + url_year + value2

            urlHaltResumptionList = []
            soup = (BeautifulSoup(requests.get(complete_url).content, 'html.parser'))

            if len((soup.find_all('div', attrs={'class': 'item_name'}))) == 0:
                break
            else:
                for foo in soup.find_all('div', attrs={'class': 'item_name'}):
                    bar = foo.find('a', attrs={'class': 'itemlink'})
                    final_url = (bar.get('href'))
                    urlHaltResumptionList.append(final_url)

            haltsHistorical = []
            resumptionsHistorical = []
            othersHistorical = []

            for value in urlHaltResumptionList:
                if 'Resumption' in value:
                    resumptionsHistorical.append(value)
                elif 'Halt' in value:
                    haltsHistorical.append(value)
                else:
                    othersHistorical.append(value)

            for url in othersHistorical:
                if 'Halt' in BeautifulSoup(requests.get(url).content, 'html.parser').find('title').text:
                    haltsHistorical.append(url)
                elif 'Resumption' in BeautifulSoup(requests.get(url).content, 'html.parser').find('title').text:
                    resumptionsHistorical.append(url)

            finalHalts = historicalHaltsInformation(haltsHistorical)
            finalResumptions = historicalResumptionsInformation(resumptionsHistorical)
            # timestampPostProcess(finalHalts,finalResumptions)

            HistoricalFinalHaltsData.append(finalHalts)
            HistoricalFinalResumptionData.append(finalResumptions)

    halt_df_list = []
    for i in range(len(HistoricalFinalHaltsData)):
        for dict_ in HistoricalFinalHaltsData[i]:
            halt_df_list.append(dict_)

    haltdf = pd.DataFrame.from_dict(halt_df_list)
    clean_ticker_halts = []
    clean_reason_halts = []

    for ticker in haltdf.ticker:
        try:
            ticker = ticker.split('.')[0]
            clean_ticker_halts.append(re.sub(r'[^A-Za-z0-9 ]+', '', ticker.strip()))
        except Exception as e:
            clean_ticker_halts.append(ticker)

    for reason in haltdf.reason:
        try:
            clean_reason_halts.append(re.sub(r'[^A-Za-z0-9 ]+', '', reason.strip()))
        except Exception as e:
            clean_reason_halts.append(reason)

    haltdf['ticker'] = clean_ticker_halts
    haltdf['reason'] = clean_reason_halts

    haltdf = haltdf.dropna()

    haltdf['date'] = cleanTimeHalts(haltdf)
    haltdf['date'] = pd.to_datetime(haltdf['date'])


    ###################################################
    resumption_df_list = []
    for i in range(len(HistoricalFinalResumptionData)):
        for dict_ in HistoricalFinalResumptionData[i]:
            resumption_df_list.append(dict_)

    clean_ticker_resumptions = []
    resumptiondf = pd.DataFrame.from_dict(resumption_df_list)
    for ticker in resumptiondf.ticker:
        try:
            ticker = ticker.split('.')[0]
            clean_ticker_resumptions.append(re.sub(r'[^A-Za-z0-9 ]+', '', ticker.strip()))
        except Exception as e:
            clean_ticker_resumptions.append(ticker)

    resumptiondf['ticker'] = clean_ticker_resumptions

    resumptiondf = resumptiondf.dropna()

    resumptiondf['clean_time'] =  cleanTimeResumptions(resumptiondf)[0]
    resumptiondf['date'] = cleanTimeResumptions(resumptiondf)[1]

    adjTimeResumption(resumptiondf)
    resumptiondf_final = resumptiondf.drop(['timestamp','resumption_timestamp','clean_time'],axis=1)
    resumptiondf_final.date = pd.to_datetime(resumptiondf_final.date)


