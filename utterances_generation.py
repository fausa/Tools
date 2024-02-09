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
# that at least one column is named "Question"
# This script will remove all other columns

# OUTPUT:
# This will output a csv file with the Original question and a list
# of the utterances for that question in the second column

# FUTURE WORK:
# Further formatting of this can be done, but for now, the second column 
# will contain a numbered list of utterances.

##########################################################################
##########################################################################

#api_key=
os.environ['OPENAI_API_KEY'];

# User inputs:

filepath=input("Please enter the path and filename of the csv that contains the questions that need utterances generation:\n")
num_variations=input("Enter the number of utterances per question you would like to generate:\n")

# functions to format the data correctly:

def remove_number_period(text):
    return re.sub(r'^\d{1,3}\.', '', text)

def remove_character(s):
    return s.replace('Â', '')
    

# function to generate utterances from a dataframe entry:

def generate_alternate_sentences(dataframe, column_name, num_variations):
    """
    Generate alternate versions of sentences in a specified column of a DataFrame.

    :param api_key: OpenAI API key
    :param dataframe: DataFrame containing the sentences
    :param column_name: Name of the column with sentences
    :param num_variations: Number of alternate versions to generate
    :return: DataFrame with original sentences and their alternate versions
    """
    results = []

    for sentence in dataframe[column_name]:
        try:
            prompt='Rewrite the following sentence in ' + num_variations + ' different ways ' + sentence
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
    test_df.dropna(subset=['Question'], inplace=True)
    test_df = test_df.loc[:, ['Question']]
    test_df['Question']=test_df['Question'].astype('string')
    test_df['Question'] = test_df['Question'].apply(remove_number_period)
    new_df = generate_alternate_sentences(test_df, 'Question', num_variations)
    
    # extract filename from filepath variable:
    file=os.path.basename(filepath)

    # write to new csv file using original filename to identify:
    new_df.to_csv('utterances_'+ num_variations + "_" + file, sep=',', index=False, encoding='utf-8')
    
    print("Utterances for ",file," have been generated in utterances_",num_variations,"_",file)


