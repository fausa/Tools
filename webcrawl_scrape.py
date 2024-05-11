import nest_asyncio
import random
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import datetime
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import os

path=os.environ['path'];
one_stop_dict=dict()
visited_urls = []


# Gets user input
url = input("What is the website you would like to scrape? \n")
initial_url = [url]

# Format the url string for javascript use:
url_java = url
url_java = url_java.replace("'", "").replace('"', "")
url_java = str.format(url_java)


json_name = input("What would you like your filename to be? \n")
json_filename = json_name + ".json"


# Uses user input to print out information
print("Webcrawling URL " + url)

# Use a webdriver Chrome, Mozilla, Edge since 
# javascript files are scraped using Microsoft Edge:

# Setup the driver selenium will use so that it runs in
# the background without opening the browser GUI:
def setup_edge():
    # Initialize the Edge driver
    #driver = webdriver.Edge(executable_path=path)
    options = Options()
    #options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    options.add_argument("--window-size=1920,1080")  # Specify window size
    options.add_argument("--ignore-certificate-errors")  # Ignore certificate errors

    service = Service(executable_path=r'C:\\Users\\afaus\\Documents\\edgedriver_win64\\msedgedriver.exe')
    # Initialize the Edge driver
    driver = webdriver.Edge(service=service, options=options)
    #driver = webdriver.Edge(executable_path='C:\\Users\\afaus\\Documents\\edgedriver_win64\\msedgedriver.exe')
    return driver


# javascript to gather (scrape) all elements on the webpage
# to save on file:
javascript_code_gather_elements = """
var allElements = document.querySelectorAll('h1,h2,h3,h4,h5,h6,p,th,tbody');
var content = [];

// var content = Array.from(allElements).map(el => el.textContent);

for (var i = 0; i < allElements.length; i++) {
  content.push(allElements[i].textContent);
}


return content;
"""

# javascript to gather the links on the webpage
# so these too can be scraped, but only if they share the 
# root URL address and are not PDFs:
javascript_code_gather_urls = """
// Define the origin address
    
var originAddress = arguments[0];
console.log(originAddress);

var links = document.querySelectorAll('a');
var validLinks = [];
var urlPattern = /^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$/;
for (var i = 0; i < links.length; i++) {
    var link = links[i];
    var href = link.getAttribute('href');
    if (href && (urlPattern.test(href) || href.startsWith('/'))) {
        var fullUrl = href.startsWith('http') ? href : originAddress + href;
        if (fullUrl.startsWith(originAddress) && !fullUrl.endsWith('.pdf')) {
            validLinks.push(fullUrl);
        }
    }
}
return validLinks;
console.log(validLinks);

"""
# some websites we know we want to scrape:
ind_websites=["https://www.sandiego.edu/academics",
              "https://www.sandiego.edu/careers",
             ]
# Start the crawl
driver=setup_edge()
queue = [initial_url]
queue = [url]

# scrape website that requires full crawl:
while queue:
    current_url = queue.pop(0)

    if (current_url not in visited_urls):
        driver.get(current_url)
        time.sleep(2)
        visited_urls.append(current_url)
        data_method = driver.execute_script(javascript_code_gather_elements)
        
        # save data scraped on a website referenced to the current URL:
        one_stop_dict[current_url]=data_method
        print(f"Scraping {current_url}")
        
        # gather the URLs to then add to queue: 
        links_on_page = driver.execute_script(javascript_code_gather_urls, url_java)
        queue.extend(link for link in links_on_page if link not in visited_urls)

print("\n Now Scraping INDIVIDUAL SITES \n\n")
        
# now scrape the individual sites that don't
# require crawling:
while ind_websites:
    current_url_ind = ind_websites.pop(0)

    if (current_url_ind not in visited_urls):
        driver.get(current_url_ind)
        time.sleep(2)
        visited_urls.append(current_url)
        data_method_ind = driver.execute_script(javascript_code_gather_elements)
        
        # save data scraped on a website referenced to the current URL:
        one_stop_dict[current_url_ind]=data_method_ind
        print(f"Scraping {current_url_ind}")
        
# Close the WebDriver
driver.quit()

one_stop_json_nopdf2=json.dumps(one_stop_dict)
    
with open(json_filename, 'w') as f:
    json.dump(one_stop_json_nopdf2, f)
