rom selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
driver = webdriver.Chrome(ChromeDriverManager().install())

trendingTickers = []
trendingCompanies = []

gainersTickers = []
gainersCompanies = []

anomalyTickers = []
anomalyCompanies = []

urls = ["https://ceo.ca/?tab=companies&exchange=all&sort_by=trending&tab=companies",
        "https://ceo.ca/?tab=companies&exchange=all&sort_by=gainers&indsutry=all&tab=companies",
        "https://ceo.ca/?tab=companies&exchange=all&sort_by=volume_ratio&indsutry=all&tab=companies"]

for url in urls:

    #driver = webdriver.Chrome(r"C:\Users\mp094\Desktop\selenium_drivers\chromedriver.exe")
    driver.get(url)

    if url == "https://ceo.ca/?tab=companies&exchange=all&sort_by=trending&tab=companies":
        for i in range(1,100,1):
            try:
                trendingTickers.append(driver.find_element_by_xpath(f"/html/body/div/div[4]/div[2]/div/div/div[2]/div/div/div[2]/div/div/div[{i}]/a/div/div[1]/span[2]/span").text)
            except Exception as e:
                pass

        for i in range(1,100,1):
            try:
                trendingCompanies.append(driver.find_element_by_xpath(f"/html/body/div/div[4]/div[2]/div/div/div[2]/div/div/div[2]/div/div/div[{i}]/a/div/div[2]/span/span").text)
            except Exception as e:
                pass

    if url == "https://ceo.ca/?tab=companies&exchange=all&sort_by=gainers&indsutry=all&tab=companies":
        for i in range(1,100,1):
            try:
                gainersTickers.append(driver.find_element_by_xpath(f"/html/body/div/div[4]/div[2]/div/div/div[2]/div/div/div[2]/div/div/div[{i}]/a/div/div[1]/span[2]/span").text)
            except Exception as e:
                pass

        for i in range(1,100,1):
            try:
                gainersCompanies.append(driver.find_element_by_xpath(f"/html/body/div/div[4]/div[2]/div/div/div[2]/div/div/div[2]/div/div/div[{i}]/a/div/div[2]/span/span").text)
            except Exception as e:
                pass

    if url == "https://ceo.ca/?tab=companies&exchange=all&sort_by=volume_ratio&indsutry=all&tab=companies":
        for i in range(1,100,1):
            try:
                anomalyTickers.append(driver.find_element_by_xpath(f"/html/body/div/div[4]/div[2]/div/div/div[2]/div/div/div[2]/div/div/div[{i}]/a/div/div[1]/span[2]/span").text)
            except Exception as e:
                pass

        for i in range(1,100,1):
            try:
                anomalyCompanies.append(driver.find_element_by_xpath(f"/html/body/div/div[4]/div[2]/div/div/div[2]/div/div/div[2]/div/div/div[{i}]/a/div/div[2]/span/span").text)
            except Exception as e:
                pass