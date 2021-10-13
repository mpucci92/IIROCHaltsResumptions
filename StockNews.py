import requests as http
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import investpy


# News Dataframe for each ticker
def newsDataframe(ticker):
    soup = BeautifulSoup(http.get(f"https://ceo.ca/{ticker}").content,'lxml')
    base_url = 'https://ceo.ca'

    newsdf = pd.DataFrame()

    authors = []
    titles = []
    dates = []
    newslinks = []

    spanArticles = soup.findAll("div", {"class": "articles"})

    for item in spanArticles[0].find_all("span", {"class": "author"}):
        authors.append(item.text)

    for item in spanArticles[0].find_all("span", {"class": "title"}):
        titles.append(item.text)

    for item in spanArticles[0].find_all("span", {"class": "date"}):
        dates.append(item.text)

    for link in spanArticles[0].find_all("a"):
        newslinks.append(base_url + link.get('href'))

    newsdf['date'] = dates
    newsdf['title'] = titles
    newsdf['authors'] = authors
    newsdf['newslink'] = newslinks

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
    return search_result.retrieve_information()
