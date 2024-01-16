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


one_stop_dict=dict()
visited_urls = []


# Gets user input
url = input("What is the website you would like to scrape? (note: enter without appending / at the end)\n")
initial_url = [url]

# Format the url string for javascript use:
url_java = url
url_java = url_java.replace("'", "").replace('"', "")
url_java = str.format(url_java)


json_name = input("What would you like your filename to be?")
json_filename = json_name + ".json"


# Uses user input to print out information
print("Webcrawling URL " + url)
driver = webdriver.Firefox()



javascript_code = """
var allElements = document.querySelectorAll('h1,h2,h3,h4,h5,h6,p,th,tbody');
var content = [];

// var content = Array.from(allElements).map(el => el.textContent);

for (var i = 0; i < allElements.length; i++) {
  content.push(allElements[i].textContent);
}


return content;
"""

javascript_code_url5 = """// Define the origin address
var originAddress = arguments[0];

console.log(originAddress);

// Select all <a> elements on the page
var links = document.querySelectorAll('a');

// Initialize an array to store valid URLs
var validLinks = [];

// Regular expression for matching URLs
var urlPattern = /^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$/;

// Loop through each <a> element and extract the href attribute
for (var i = 0; i < links.length; i++) {
  var link = links[i];
  var href = link.getAttribute('href');

  // Check if the href attribute matches the URL pattern
  if (urlPattern.test(href)) {
    // Check if the URL starts with the specified origin address
    if (href.startsWith(originAddress) || href==originAddress) {
      // Check if the URL does not end with ".pdf"
      if (!href.endsWith(".pdf")) {
        // Store the valid URL
        validLinks.push(href);
      }
    }
  }
}
return validLinks
// Output the valid URLs
console.log(validLinks);
"""

# Start the crawl
queue = [initial_url]
queue = [url]

while queue:
    current_url = queue.pop(0)

    if (current_url not in visited_urls):
        driver.get(current_url)
        time.sleep(2)
        visited_urls.append(current_url)
        #headers, text, tableheader, tabletext= driver.execute_script(javascript_code)
        data_method = driver.execute_script(javascript_code)
        #one_stop_dict[current_url]=[[headers, text, tableheader, tabletext]]
        one_stop_dict[current_url]=data_method
        print(f"Scraping {current_url}")
        
        links_on_page = driver.execute_script(javascript_code_url5, url_java)

        
        queue.extend(link for link in links_on_page if link not in visited_urls)
    
        


# Close the WebDriver
driver.quit()

one_stop_json_nopdf2=json.dumps(one_stop_dict)
    
with open(json_filename, 'w') as f:
    json.dump(one_stop_json_nopdf2, f)
