import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime
import calendar

def historicalHaltsInformation(haltsHistorical):
    finalHalts = []

    for url in haltsHistorical:
        resp = requests.get(url)

        halt_information = []

        for element in BeautifulSoup(resp.content, 'html.parser').find_all('p'):
            element = element.text.replace('\xa0', ' ')
            halt_information.append(element)

        infoHalts = {}

        for i in range(len(halt_information)):
            if i == 0:
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

        infoResumptions = {}
        for i in range(len(halt_information)):
            if i == 0:
                infoResumptions['timestamp'] = halt_information[i].strip()

            if 'Company:' in halt_information[i]:
                try:
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

    adjTime = []
    for i in range(len(clean_time)):
        try:
            adjTime.append(pd.to_datetime(clean_time[i]))
        except Exception as e:
            adjTime.append(pd.to_datetime(clean_time[i].split(" ")[0]))

    for time in adjTime:
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

    adjTime = []
    for i in range(len(clean_time)):
        try:
            adjTime.append(pd.to_datetime(clean_time[i]))
        except Exception as e:
            adjTime.append(pd.to_datetime(clean_time[i].split(" ")[0]))

    for time in adjTime:
        final_clean_time.append(time.isoformat().split('T')[-1])

    for i in range(len(resumptiondf)):
        final_clean_date.append(pd.to_datetime(resumptiondf.timestamp.iloc[i]).isoformat().split('T')[0])

    for i,val in enumerate(final_clean_date):
        timestamp = val + " " + final_clean_time[i]
        final_timestamp.append(timestamp)

    return final_clean_time,final_timestamp

def adjTimeResumption(resumptiondf):
    for index,time in enumerate(resumptiondf.resumption_timestamp):
        if '/' in time:
            for value in time.split(' '):
                value = re.sub(r'[^/0-9]+',"",str(value))
                if '/' in value:
                    resumptiondf.date.iloc[index] = ((str(pd.to_datetime(value,format='%m/%d/%Y')).split(' ')[0])) + " " + resumptiondf.clean_time.iloc[index]

