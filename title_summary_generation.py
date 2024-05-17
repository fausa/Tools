import openai
import pandas as pd
import numpy as np
import os
import regex
import re

##########################################################################
##########################################################################

# USAGE:
# enter the filepath and filename as prompted, and then
# enter the number of utterances per question you'd like to generate.

# INPUT
# Input file should be a csv file list of questions where it indicates
# that at least two columns each named "Question" and "Answer", respecively
# This script will remove all other columns

# OUTPUT:
# This will output a csv file with a generated "Summary" and "Title" for
# each entry, using an LLM, in this case, ChatGPT4.0


##########################################################################
##########################################################################

#api_key=
os.environ['OPENAI_API_KEY'];

# User inputs:

filepath=input("Please enter the path and filename of the csv that contains the questions and answers that need titles and summaries:\n")

title_summary_var=input("Do you need:\n 1. Title generation \n 2. Summary generation \n 3. Both title and summary generation\n")


def remove_number_period(text):
    return re.sub(r'^\d{1,3}\.', '', text)

def remove_character(s):
    return s.replace('Â', '')
    

# function to generate utterances from a dataframe entry:

def generate_title(dataframe, column_name, column_name2):
    """
    Generate alternate versions of sentences in a specified column of a DataFrame.

    :param api_key: OpenAI API key
    :param dataframe: DataFrame containing the sentences
    :param column_name: Name of the column with sentences
    :param num_variations: Number of alternate versions to generate
    :return: DataFrame with original sentences and their alternate versions
    """
    results = []

    #for sentence,index in dataframe[column_name]:
    for i, row in dataframe.iterrows():
        #for sentence2 in dataframe[column_name2]:
        sentence = row[column_name]
        sentence2 = row[column_name2]
        try:
            prompt='Write a 5 to 6 word title for an entry with this question ' + sentence + 'and this answer ' + sentence2 
            response = openai.chat.completions.create(
                model="gpt-4",
                #"gpt-3.5-turbo",  # or another model of your choice
                messages = [ # Change the prompt parameter to messages parameter
                    {'role': 'user', 'content': prompt}
                ]

            )
            choices = response.choices
            chat_completion = choices[0]
            alternates = chat_completion.message.content
            
            results.append({'Original': sentence, 'Alternates': alternates})
        except Exception as e:
            print(f"An error occurred: {e}")
            results.append({'Original': sentence, 'Alternates': []})

    return pd.DataFrame(results)

def generate_summary(dataframe, column_name, column_name2):
    """
    Generate alternate versions of sentences in a specified column of a DataFrame.

    :param api_key: OpenAI API key
    :param dataframe: DataFrame containing the sentences
    :param column_name: Name of the column with sentences
    :param num_variations: Number of alternate versions to generate
    :return: DataFrame with original sentences and their alternate versions
    """
    results = []

    #for sentence,index in dataframe[column_name]:
    for i, row in dataframe.iterrows():
        #for sentence2 in dataframe[column_name2]:
        sentence = row[column_name]
        sentence2 = row[column_name2]
        try:
            prompt='Write a short summary for an entry with this question ' + sentence + 'and this answer ' + sentence2 
            response = openai.chat.completions.create(
                model="gpt-4",
                #"gpt-3.5-turbo",  # or another model of your choice
                messages = [ # Change the prompt parameter to messages parameter
                    {'role': 'user', 'content': prompt}
                ]

            )
            choices = response.choices
            chat_completion = choices[0]
            alternates = chat_completion.message.content
            
            results.append({'Original': sentence, 'Alternates': alternates})
        except Exception as e:
            print(f"An error occurred: {e}")
            results.append({'Original': sentence, 'Alternates': []})
                
    return pd.DataFrame(results)


if __name__ == "__main__":
    test_df = pd.read_csv(filepath, encoding = "ISO-8859-1")
    test_df.dropna(subset=['Question','Answer'], inplace=True)
    test_df = test_df.loc[:, ['Question','Answer']]
    test_df['Question']=test_df['Question'].astype('string')
    test_df['Answer']=test_df['Answer'].astype('string')
    
    #test_df['Question'] = test_df['Question'].apply(remove_number_period)
    if title_summary_var==1 | title_summary_var==3:
        new_df1 = generate_title(test_df, 'Question', 'Answer')
    if title_summary_var==2 | title_summary_var==3:
        new_df2 = generate_summary(test_df, 'Question', 'Answer')
    
    if title_summary_var==3:
        new_df = pd.concat([new_df1, new_df2])
    elif title_summary_var==1:
        new_df = new_df1
    else:
        new_df = new_df2
        
    # extract filename from filepath variable:
    file=os.path.basename(filepath)

    # write to new csv file using original filename to identify:
    new_df.to_csv('title_summary_' + "_" + file, sep=',', index=False, encoding='utf-8')
    
    print("Title and Summary columns for ",file," have been generated in title_summary_","_",file)


