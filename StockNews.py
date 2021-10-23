import requests as http
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import investpy
import re

def commaNumber(amount):
    orig = amount
    new = re.sub("^(-?\d+)(\d{3})", '\g<1>,\g<2>', amount)
    if orig == new:
        return new
    else:
        return commaNumber(new)



# News Dataframe for each ticker
def newsDataframe(ticker):
    soup = BeautifulSoup(http.get(f"https://ceo.ca/{ticker}").content, 'lxml')
    base_url = 'https://ceo.ca'

    newsdf = pd.DataFrame()

    authors = []
    titles = []
    dates = []
    newslinks = []

    spanArticles = soup.findAll("div", {"class": "articles"})

    newSoup = []
    for element in ((spanArticles[0])):

        if str(element) == '<h3>featured articles</h3>':
            break
        newSoup.append((element))

    newText = []
    for element in newSoup:
        newText.append(str(element))

    new = " ".join(newText)
    soupNew = BeautifulSoup(new, "html.parser")

    for item in soupNew.find_all("span", {"class": "author"}):
        authors.append(item.text)

    for item in soupNew.find_all("span", {"class": "title"}):
        titles.append(item.text)

    for item in soupNew.find_all("span", {"class": "date"}):
        dates.append(item.text)

    for link in soupNew.find_all("a"):
        newslinks.append(base_url + link.get('href'))

    newsdf['Date'] = dates
    newsdf['Title'] = titles
    newsdf['Authors'] = authors
    newsdf['Newslink'] = newslinks

    return newsdf


# Specific Stock News:
def recentData(companyname):
    search_result = investpy.search_quotes(text=companyname, products=['stocks'], n_results=1)
    return search_result.retrieve_recent_data()


def historicalData(companyname, startTime, endTime):
    # startTime: dd/mm/yyyy
    # endTime: dd/mm/yyyy
    search_result = investpy.search_quotes(text=companyname, products=['stocks'], n_results=1)
    return search_result.retrieve_historical_data(from_date=startTime, to_date=endTime)


def stockInformation(companyname):
    search_result = investpy.search_quotes(text=companyname, products=['stocks'], n_results=1)
    metricsDict = search_result.retrieve_information()
    df = pd.DataFrame.from_dict(metricsDict,orient ='index')
    df = df.reset_index()
    df.rename(columns = {'index':'Financial Metric', 0:'Value'}, inplace = True)
    df['Financial Metric'] = ['Previous Close','Daily Range','Revenue','Open','Weekly Range','Earning Per Share',
                              'Volume','Market Cap','Dividend','Average Volume','Ratio','Beta','One Year Return',
                              'Outstanding Shares','Next Earnings Date']

    indices_to_modify = [2,6,7,9,13]

    for i in indices_to_modify:

        df['Value'].iloc[i] = commaNumber(str(df['Value'].iloc[i]))

    return df


