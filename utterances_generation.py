import openai
import pandas as pd
import numpy as np
import os
import regex
import re

#api_key=
os.environ['OPENAI_API_KEY'];

filepath=input("Please enter the filepath that contains the csv file that needs utterances (please include the final slash):\n")
file=input("Please enter the name of the csv filename that contains the questions that need utterances generation:\n")

# functions to format the data correctly:

def remove_number_period(text):
    return re.sub(r'^\d{1,3}\.', '', text)

def remove_character(s):
    return s.replace('Â', '')
    
# function to generate utterances from a dataframe entry:

# function to generate utterances from a dataframe entry:

def generate_alternate_sentences(dataframe, column_name, num_variations=20):
    """
    Generate alternate versions of sentences in a specified column of a DataFrame.

    :param api_key: OpenAI API key
    :param dataframe: DataFrame containing the sentences
    :param column_name: Name of the column with sentences
    :param num_variations: Number of alternate versions to generate
    :return: DataFrame with original sentences and their alternate versions
    """
    #openai.api_key = api_key
    results = []

    for sentence in dataframe[column_name]:
        try:
            #prompt=f"Rewrite the following sentence in {num_variations} different ways: '{sentence}'"
            prompt='Rewrite the following sentence in 20 different ways ' + sentence
            response = openai.chat.completions.create(
                model="gpt-4",
                #"gpt-3.5-turbo",  # or another model of your choice
                messages = [ # Change the prompt parameter to messages parameter
                    {'role': 'user', 'content': prompt}
                ]
                #prompt=f"Rewrite the following sentence in {num_variations} different ways: '{sentence}'",
                #max_tokens=200,
                #n=num_variations,
                #stop=["\n"]
            )
            #alternates = [response.choices[i].text.strip() for i in range(num_variations)]
            choices = response.choices
            chat_completion = choices[0]
            alternates = chat_completion.message.content
            
            results.append({'Original': sentence, 'Alternates': alternates})
        except Exception as e:
            print(f"An error occurred: {e}")
            results.append({'Original': sentence, 'Alternates': []})

    return pd.DataFrame(results)

if __name__ == "__main__":
    test_df = pd.read_csv(filepath + file)
    test_df.dropna(subset=['Question'], inplace=True)
    test_df = test_df.loc[:, ['Question']]
    test_df['Question']=test_df['Question'].astype('string')
    test_df['Question'] = test_df['Question'].apply(remove_number_period)
    new_df = generate_alternate_sentences(test_df, 'Question')

    new_df.to_csv('utterances_'+ file, sep=',', index=False, encoding='utf-8')
    
    print("Utterances for ", file, " have been generated in utterances_", file)


