from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import numpy as np
import os
import regex
import re
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import os

# Gather variables needed specific to the
# driver for the selenium browser and
# the chatbot and the specific text box
# address/output (bubble) and links provided
# these are found as objects when right clicking 
# on the object in the website and choosing
# Inspect (Q):

path=os.environ['edgedriver_path']
chatbot_URL=os.environ['webchat_URL']
input_textbox=os.environ['webchat_textbox']
bubble_content=os.environ['webchat_bubble_content']
links=os.environ['webchat_div_links']

confused_response=os.environ['webchat_confused']
feedback_response=os.environ['webchat_feedbackrq']

# Take user input as to the CSV file that will be used
# to feed questions to the Copilot bot:
filepath=input("Please enter the path and filename of the csv that contains the questions you would like to ask to test the chatbot:\n")

results=[]



def interact_with_chatbot(dataframe):
    # in order to ensure the selenium webdriver does not open 
    # a browser, options and service must be specified. For this, the webdriver
    # must be installed and the path to that service given:
    
    options = Options()
    
    # Some options that can be added, but were commented in our case:
    #options.add_experimental_option('excludeSwitches', ['enable-logging'])
    #options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    #options.add_argument("--window-size=1920,1080")  # Specify window size
    
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--ignore-certificate-errors")  # Ignore certificate errors

    # path to the edge driver (or chrome, depending on the webdriver used):
    service = Service(executable_path=path)
    
    # Initialize the Edge driver
    driver = webdriver.Edge(service=service, options=options)
    
    # Navigate to the webpage that contains our Copilot chatbot:
    driver.get(chatbot_URL)

    # Various delays are added to keep from over
    # burdening the chatbot:
    time.sleep(3)

    # We know the chatbot requires an input whether user is Undergraduate,
    # Graduate or Alumni, here we select to use the chatbot as an Undergraduate:
    question1="Undergraduate"
    input_field = driver.find_element(By.CSS_SELECTOR, input_textbox)
    input_field.send_keys(question1)
    input_field.send_keys("\n")
    
    time.sleep(4) 
    
    # Now, run through each row of Questions in the CSV
    # file that was given from the user and run them through
    # the chat and record the responses, and save them:
    for i, row in dataframe.iterrows():
        sentence = row[column_name]
        try:
            input_field.send_keys(sentence)
            input_field.send_keys("\n")
            
            time.sleep(6)
            
            chat_bubbles = driver.find_elements(By.CSS_SELECTOR, bubble_content)

            # Select the last chat bubble in the list
            latest_chat_bubble = chat_bubbles[-1] if chat_bubbles else None
            output_element=latest_chat_bubble
            response = output_element.text
            
            # Only record the response and links if the bot does not get confused:
            if (response!=confused_response) & (response!=feedback_response):

                # Get the text form of the hyperlink
                hyperlinks = latest_chat_bubble.find_elements(By.TAG_NAME, "a")

                # Get the URLs of all hyperlinks
                hyperlink_urls = [hyperlink.get_attribute("href") for hyperlink in hyperlinks]
                results.append({'Question': sentence, 'Response': response, 'Hyperlinks': hyperlink_urls})
                
          
                time.sleep(6)    
            
            # in the case where the bot gets confused, we try asking one more time
            # if this still confuses the bot, we save null responses and if needed
            # reset or restart the bot:
            elif (response==confused_response):
                input_field.send_keys(sentence)
                input_field.send_keys("\n")
                time.sleep(6)
            
                chat_bubbles = driver.find_elements(By.CSS_SELECTOR, bubble_content)
                # Select the last chat bubble in the list
                latest_chat_bubble = chat_bubbles[-1] if chat_bubbles else None
                
                output_element=latest_chat_bubble
                response = output_element.text
                
                if (response!=feedback_response):

                    # Get the text form of the hyperlink
                    hyperlinks = latest_chat_bubble.find_elements(By.TAG_NAME, "a")

                    # Get the URLs of all hyperlinks
                    hyperlink_urls = [hyperlink.get_attribute("href") for hyperlink in hyperlinks]
                    results.append({'Question': sentence, 'Response': response, 'Hyperlinks': hyperlink_urls})
                    time.sleep(6)
                    
                else:
                    results.append({'Question': sentence, 'Response': response, 'Hyperlinks': ""})
                    links = driver.find_elements(By.CSS_SELECTOR, links)
                    for link in links:
                        if "Start over" in link.text:
                            link.click()
                            time.sleep(4)
                            input_field = driver.find_element(By.CSS_SELECTOR, input_textbox)
                            input_field.send_keys("Yes")
                            input_field.send_keys("\n")
                            time.sleep(10)
                    
            elif (response==feedback_response):
                results.append({'Question': sentence, 'Response': response, 'Hyperlinks': ""})
                links = driver.find_elements(By.CSS_SELECTOR, links)
                for link in links:
                    if "Start over" in link.text:
                        link.click()
                        time.sleep(4)
                        input_field = driver.find_element(By.CSS_SELECTOR, input_textbox)
                        input_field.send_keys("Yes")
                        input_field.send_keys("\n")
                        time.sleep(10)
                        
        # Error management:          
        except Exception as e:
                print(f"An error occurred: {e}")
                results.append({'Question': sentence, 'Response': "", 'hyperlink_text': ""})
                
               
        
        time.sleep(6)    
        
    # Close the driver by the end of looping:               
    driver.quit()
    
    return pd.DataFrame(results)


if __name__ == "__main__":
    
    test_indexed=[]
    url_indexed=[]
    test_df = pd.read_csv(filepath)#, encoding = "ISO-8859-1")
    
    # Taking both the Title and Question of the 
    # dataframe as the Title also indicates what
    # must be appended to the URL to find each article
    # and can be used to compare URLs/links provided
    # by the chat. Ideally, the chat references the corresponding
    # URL with appended Title (with hyphens instead of spaces)
    # for the given question:
    test_df = test_df.loc[:,['Title', 'Question']]
    test_df['Title']=test_df['Title'].astype('string')
    test_df['Question']=test_df['Question'].astype('string')

    
    column_name='Question'
    file=os.path.basename(filepath)
    # Example usage
    row_error=[]

    response_df = interact_with_chatbot(test_df)
    file=os.path.basename(filepath)
        
    # write to new csv file using original filename to identify:
    response_df.to_csv('copilot_test_' + file, sep=',', index=False, encoding='utf-8')
        
    