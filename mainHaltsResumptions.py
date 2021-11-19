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
from GeneratePDF import generatePDF,finalGeneratePDF
import mpld3

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
root_directory = os.path.dirname(os.path.realpath(__file__))

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

    dfHalt.rename(columns={'timestamp': 'Date', 'company': 'Company',
                           'ticker':'Ticker','reason':'Reason',
                           'halt_timestamp':'Time of Halt', 'date':'Timestamp'}, inplace=True)
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

    resumptiondf_final.rename(columns={'company': 'Company','ticker': 'Ticker', 'reason': 'Reason','date': 'Timestamp'}, inplace=True)

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
    currentDate = "2021-11-17" #date.today()
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    path_html_directory = root_directory
    html_file = path_html_directory + fr'\Small Cap Reports\HTMLs\Report_HaltResumptions_{currentDate}.html'
    pdf_file = path_html_directory + fr'\Small Cap Reports\PDFs\Report_HaltResumptions_{currentDate}.pdf'

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

    # USA Names:
    #currentDate = date.today()
    path_to_save = root_directory + fr"\UsData\{currentDate}.csv"

    # uncomment to download data for the day
    downloadAmericanHalts(path_to_save)

    dfUSA = pd.read_csv(path_to_save)
    dfUSA = dfUSA[(dfUSA.Reason == 'News pending') | (dfUSA.Reason == 'LULD pause')]

    ##########################
    halt_companies_list = []
    halt_companies_names = []


    todayTickersHalts = list(haltdf[haltdf['Timestamp'] > f'{currentDate} 00:00:00'].Ticker)
    todayCompanyHalts = list(haltdf[haltdf['Timestamp'] > f'{currentDate} 00:00:00'].Company)

    for i,ticker in enumerate(todayTickersHalts):
        try:
            halt_companies_list.append((newsDataframe(ticker).to_html()))
            halt_companies_names.append(todayCompanyHalts[i])
        except Exception as e:
            halt_companies_list.append("NONE")
            halt_companies_names.append(todayCompanyHalts[i])

    resumptions_companies_list = []
    resumptions_companies_names = []

    todayTickersResumptions = list(resumptiondf[resumptiondf['Timestamp'] > f'{currentDate} 00:00:00'].Ticker)
    todayCompanyResumptions = list(resumptiondf[resumptiondf['Timestamp'] > f'{currentDate} 00:00:00'].Company)


    for i,ticker in enumerate(todayTickersResumptions):
        try:
            resumptions_companies_list.append((newsDataframe(ticker).to_html()))
            resumptions_companies_names.append(todayCompanyResumptions[i])
        except Exception as e:
            resumptions_companies_list.append("NONE")
            resumptions_companies_names.append(todayCompanyResumptions[i])


    generatePDF(path_wkhtmltopdf,path_html_directory,html_file,pdf_file,haltdf.to_html(),resumptiondf.to_html(),dfUSA.to_html())

    with open(html_file,"a") as htmlFile:

        htmlFile.write('<h1>Canadian Halted Tickers Specific News</h1>')
        for j,df in enumerate(halt_companies_list):
            htmlFile.write('<br>')
            htmlFile.write('<br>')
            htmlFile.write(f'<p style="background:orange;padding: 1em;font-weight: bold">Company Name: {halt_companies_names[j]}</p>')
            htmlFile.write(df)

        htmlFile.write('<h1>Canadian Resumed Tickers Specific News</h1>')
        for j,df in enumerate(resumptions_companies_list):
            htmlFile.write('<br>')
            htmlFile.write('<br>')
            htmlFile.write(f'<p style="background:orange;padding: 1em;font-weight: bold">Company Name: {resumptions_companies_names[j]}</p>')
            htmlFile.write(df)

        htmlFile.write('<h2>Canadian Resumed Tickers Financial Metrics </h2>')
        for company in resumptiondf.Company:
            try:
                htmlFile.write(f'<p style="background:orange;padding: 1em;font-weight: bold">Company Name: {company}</p>')
                htmlFile.write(f'<p style="font-size:1vw;font-weight: bold"> Company Website: <a href="https://www.google.ca/search?q={company}"> {company} Website</a> </p>')
                df = stockInformation(company).to_html()
                htmlFile.write(df)

                recent_df = recentData(company)
                recent_df = recent_df.reset_index()
                figure = plotStock(recent_df, company)
                html_str = mpld3.fig_to_html(figure)
                htmlFile.write(html_str)

            except Exception as e:
                htmlFile.write(f'<p style="font-size:1vw;font-weight: bold"> Manual Search: <a href="https://www.investing.com/search/?q={company}"> {company}</a> </p>')

        htmlFile.write('<h1>United States Halted/Resumed Tickers Financial Metrics</h1>')
        for company in cleanNamesAmerican(dfUSA):
            try:
                htmlFile.write(f'<p style="background:orange;padding: 1em;font-weight: bold">Company Name: {company}</p>')
                htmlFile.write(f'<p style="font-size:1vw;font-weight: bold"> Company Website: <a href="https://www.google.ca/search?q={company}"> {company} Website</a> </p>')
                df = stockInformation(company).to_html()
                htmlFile.write(df)

                recent_df = recentData(company)
                recent_df = recent_df.reset_index()
                figure = plotStock(recent_df, company)
                html_str = mpld3.fig_to_html(figure)
                htmlFile.write(html_str)
            except Exception as e:
                htmlFile.write(f'<p style="font-size:1vw;font-weight: bold"> Manual Search: <a href="https://www.investing.com/search/?q={company}"> {company}</a> </p>')

    finalGeneratePDF(path_wkhtmltopdf, html_file, pdf_file)
