from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from StockNews import newsDataframe,stockInformation,recentData
from CandlestickPlots import plotStock
from GeneratePDF import generatePDF,finalGeneratePDF
import mpld3
import os
import pandas as pd
from datetime import date

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
root_directory = os.path.dirname(os.path.realpath(__file__))

driver = webdriver.Chrome(ChromeDriverManager().install())

trendingTickers = []
trendingCompanies = []
trendingDF = []

driver.get("https://ceo.ca/?tab=companies&exchange=all&sort_by=trending&tab=companies")

for i in range(1,100,1):
    try:
        val = str(driver.find_element_by_xpath(f"/html/body/div/div[4]/div[2]/div/div/div[2]/div/div/div[2]/div/div/div[{i}]/a/div/div[1]/span[2]/span").text)
        val = val.replace("$", "")
        trendingTickers.append(val)
        trendingCompanies.append(driver.find_element_by_xpath(
            f"/html/body/div/div[4]/div[2]/div/div/div[2]/div/div/div[2]/div/div/div[{i}]/a/div/div[2]/span/span").text)
    except Exception as e:
        pass

currentDate = "2021-11-17" #date.today()
path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
path_html_directory = root_directory
base_html = path_html_directory + '\ReportTemplateGainersAnomaly.html'
html_file = path_html_directory + fr'\Small Cap Reports\HTMLs\Report_Trending_{currentDate}.html'
pdf_file = path_html_directory + fr'\Small Cap Reports\PDFs\Report_Trending_{currentDate}.pdf'

for trendTicker in trendingTickers:
    try:
        trendingDF.append(((newsDataframe(trendTicker)).to_html()))
    except Exception as e:
        trendingDF.append("NONE")

with open(html_file,"a") as htmlFile:

    #htmlFile.write('<h1>Top Small Cap Trending</h1>')
    htmlFile.write("""<!DOCTYPE html>
<html>
<body>
     <h1>Top Small Cap Trending</h1>
	<style>
	table, td, th {
            border: 1px solid #ddd;
            text-align: center;
        }


        table {
            border-collapse: collapse;
            width: 100%;
        }


        th, td {
            padding: 15px;
        }

        table { background-color: white; }
        th { background-color: #57D0F1; }
	</style>) """)

    for j,df in enumerate(trendingDF):
        htmlFile.write('<br>')
        htmlFile.write('<br>')
        htmlFile.write(f'<p style="background:orange;padding: 1em;font-weight: bold">Company Name: {trendingCompanies[j]}</p>')
        htmlFile.write(df)


    htmlFile.write('<h2>Financial Metrics </h2>')

    for company in trendingCompanies:
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