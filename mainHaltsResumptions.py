import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime
import os
from CanadianHaltsResumptions import historicalHaltsInformation,historicalResumptionsInformation,cleanTimeHalts,cleanTimeResumptions,adjTimeResumption
from UnitedStatesHaltsResumptions import cleanNamesAmerican,downloadAmericanHalts
from StockNews import newsDataframe,stockInformation,recentData
from CandlestickPlots import plotStock

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

def createURL(complete_url):
    urlHaltResumptionList = []
    soup = (BeautifulSoup(requests.get(complete_url).content, 'html.parser'))

    if len((soup.find_all('div', attrs={'class': 'item_name'}))) == 0:
        print('Length of item name is zero!')
    else:
        for foo in soup.find_all('div', attrs={'class': 'item_name'}):
            bar = foo.find('a', attrs={'class': 'itemlink'})
            final_url = (bar.get('href'))
            urlHaltResumptionList.append(final_url)

    return urlHaltResumptionList


def splitURL(urlHaltResumptionList):
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

    return haltsHistorical,resumptionsHistorical

def createHalts(HistoricalFinalHaltsData):
    # 1. Halt Tickers
    halt_df_list = []

    for i in range(len(HistoricalFinalHaltsData)):
        for dict_ in HistoricalFinalHaltsData[i]:
            halt_df_list.append(dict_)

    dfHalt = pd.DataFrame.from_dict(halt_df_list)
    clean_ticker_halts = []
    clean_reason_halts = []


    for ticker in dfHalt.ticker:
        try:
            ticker = ticker.split('.')[0]
            clean_ticker_halts.append(re.sub(r'[^A-Za-z0-9 ]+', '', ticker.strip()))
        except Exception as e:
            clean_ticker_halts.append(ticker)

    for reason in dfHalt.reason:
        try:
            clean_reason_halts.append(re.sub(r'[^A-Za-z0-9 ]+', '', reason.strip()))
        except Exception as e:
            clean_reason_halts.append(reason)

    dfHalt['ticker'] = clean_ticker_halts
    dfHalt['reason'] = clean_reason_halts

    dfHalt = dfHalt.dropna()                 # Contains ALl Halted Tickers in Dataframe format
    dfHalt['date'] = cleanTimeHalts(dfHalt)
    dfHalt['date'] = pd.to_datetime(dfHalt['date'])

    return dfHalt

def createResumptions(HistoricalFinalResumptionData):
    # 2. Resumption Tickers
    resumption_df_list = []
    for i in range(len(HistoricalFinalResumptionData)):
        for dict_ in HistoricalFinalResumptionData[i]:
            resumption_df_list.append(dict_)

    clean_ticker_resumptions = []
    dfResumption = pd.DataFrame.from_dict(resumption_df_list)
    for ticker in dfResumption.ticker:
        try:
            ticker = ticker.split('.')[0]
            clean_ticker_resumptions.append(re.sub(r'[^A-Za-z0-9 ]+', '', ticker.strip()))
        except Exception as e:
            clean_ticker_resumptions.append(ticker)

    dfResumption['ticker'] = clean_ticker_resumptions
    dfResumption = dfResumption.dropna()

    dfResumption['clean_time'] = cleanTimeResumptions(dfResumption)[0]
    dfResumption['date'] = cleanTimeResumptions(dfResumption)[1]

    adjTimeResumption(dfResumption)
    resumptiondf_final = dfResumption.drop(['timestamp', 'resumption_timestamp', 'clean_time'], axis=1)
    resumptiondf_final.date = pd.to_datetime(resumptiondf_final.date)  # Contains ALl Resumed Tickers in Dataframe format

    return resumptiondf_final

def companyInformationCanada(df):
    for company in df.company:
        try:
            print(company)
            recent_df = recentData(company)
            recent_df = recent_df.reset_index()
            print(stockInformation(company))
            (plotStock(recent_df,company))
        except Exception as e:
            pass

def companyInformationUSA(companylist):

    for company in companylist:
        try:
            print(company)
            recent_df = recentData(company)
            recent_df = recent_df.reset_index()
            print(stockInformation(company))
            (plotStock(recent_df,company))
        except Exception as e:
            pass


if __name__ == '__main__':
    #1. Canada Names

    HistoricalFinalHaltsData = []
    HistoricalFinalResumptionData = []

    base_url_historical = 'https://iiroc.mediaroom.com/index.php?o='
    parameter1 = "0"
    parameter2 = "2021"
    url_year = '&s=2429&year='

    complete_url = base_url_historical + parameter1 + url_year + parameter2

    urlHaltResumptionList = createURL(complete_url)

    haltsHistorical = splitURL(urlHaltResumptionList)[0]
    resumptionsHistorical = splitURL(urlHaltResumptionList)[1]

    finalHalts = historicalHaltsInformation(haltsHistorical)
    finalResumptions = historicalResumptionsInformation(resumptionsHistorical)

    HistoricalFinalHaltsData.append(finalHalts)
    HistoricalFinalResumptionData.append(finalResumptions)

    haltdf = createHalts(HistoricalFinalHaltsData)
    resumptiondf = createResumptions(HistoricalFinalResumptionData)

    print("------------------------------------------------------------")
    print('Halt Dataframe: Canada')
    print(haltdf)
    print("------------------------------------------------------------")
    print('Resumption Dataframe: Canada')
    print(resumptiondf)

    # USA Names:

    currentDate = date.today()
    path_to_save = os.path.dirname(os.path.abspath(__file__)) + fr"\UsData\{currentDate}.csv"
    # uncomment to download data for the day
    downloadAmericanHalts(path_to_save)

    df = pd.read_csv(path_to_save)
    df = df[(df.Reason == 'News pending') | (df.Reason == 'LULD pause')]

    print("------------------------------------------------------------")
    print('USA Halts and Resumptions')
    print(df)

    print("------------------------------------------------------------")
    print('News Section')

    print('Canada News:')
    print("Canada Halted Tickers News:")

    todayTickersHalts = list(haltdf[haltdf['date'] > f'{currentDate} 00:00:00'].ticker)

    for ticker in todayTickersHalts:
        try:
            print('--------------------------------')
            print(f'Ticker: {ticker}')
            print((newsDataframe(ticker)))
        except Exception as e:
            pass

    print(" ")
    print("Canada Resumed Tickers News:")

    todayTickersResumptions = list(resumptiondf[resumptiondf['date'] > f'{currentDate} 00:00:00'].ticker)

    for ticker in todayTickersResumptions:
        try:
            print('--------------------------------')
            print(f'Ticker: {ticker}')
            print((newsDataframe(ticker)))
        except Exception as e:
            pass

    print("------------------------------------------------------------")
    print("USA Tickers News:")

    todayTickers = list(df.Symbol)
    print('Under Construction')

    print("-------------------------------------------")
    print("Canada News Information:")
    companyInformationCanada(resumptiondf)

    print("------------------------------------------------------------")
    print("USA News Information:")
    companyInformationUSA(cleanNamesAmerican(df))
