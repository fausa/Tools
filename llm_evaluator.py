from ctransformers import AutoConfig, AutoModelForCausalLM, Config

import openai
import pandas as pd
import numpy as np
import os
import regex
import re
from transformers import AutoTokenizer, AutoModel
import torch
from langchain.evaluation import load_evaluator
from langchain.evaluation import EvaluatorType
#import langchain.evaluator as evaluator


##########################################################################
##########################################################################

# USAGE:
# enter the filepath and filename as prompted

# INPUT
# Input file should be a csv file list of questions to be sent to the bot

# OUTPUT:
# This will output a csv file with the Original question and the bot responses

##########################################################################
##########################################################################

#api_key=
os.environ['OPENAI_API_KEY'];
huggingfacehub_api_token=os.environ['HUGGINGFACEHUB_API_TOKEN']

# User inputs:

filepath=input("Please enter the path and filename of the csv that contains the questions, bot responses, and root truth answers that require analysis:\n")

#config = AutoConfig(config=Config(temperature=0.5, 
#                                  max_new_tokens=2048, context_length=2048, gpu_layers=1
#                                 ),
#                   )
#llm = AutoModelForCausalLM.from_pretrained("TheBloke/Mistral-7B-Instruct-v0.1-GGUF",
#                                                       model_file="mistral-7b-instruct-v0.1.Q4_K_M.gguf",
#                                                       config=config,
#                                                      )
#llm = llms["mistral"]

#INSTRUCTIONS = "You are a friendly chat bot willing to help out the user."



##title_summary_var=input("Do you need:\n 1. Title generation \n 2. Summary generation \n 3. Both title and summary generation\n")


def remove_number_period(text):
    return re.sub(r'^\d{1,3}\.', '', text)

def remove_character(s):
    return s.replace('Â', '')

model_name = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def get_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1)

def cosine_similarity(embedding1, embedding2):
    return torch.nn.functional.cosine_similarity(embedding1, embedding2).item()

# Define a custom evaluator
#class ContinuousEvaluator(evaluators.BaseEvaluator):
def evaluate2(ground_truth, generated):
    ground_truth_embedding = get_embedding(ground_truth)
    generated_embedding = get_embedding(generated)
    return cosine_similarity(ground_truth_embedding, generated_embedding)


#def apply_template(instructions, contents):
#    text_row = f"""<s>[INST]{instructions} {contents}[/INST]"""
#    return text_row
    

# function to generate utterances from a dataframe entry:

def response_analysis(dataframe, column_name, column_name2, column_name3):
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
        sentence3 = row[column_name3]
        try:

            evaluator=load_evaluator("labeled_criteria",criteria="correctness")
            eval_result=evaluator.evaluate_strings(prediction=sentence, input=sentence3, reference=sentence2)
        
            #evaluator2 = ContinuousEvaluator()
            ground_truth = sentence2
            generated_response = sentence

            #score = evaluator2.evaluate2(ground_truth, generated_response)
            score = evaluate2(ground_truth, generated_response)
    
            results.append({'Response': sentence, 'Answer': sentence2, 'Correctness Score': eval_result['score'],
                           'Reason': eval_result['reasoning'].replace('\n','').split('.')[:-1],
                           'Similarity': score})
            
            
        except Exception as e:
            print(f"An error occurred: {e}")
            results.append({'Response': sentence, 'Answer': sentence2, 'Correctness Score': [], 'Reason': [],
                           'Similarity': []})

    return pd.DataFrame(results)


if __name__ == "__main__":
    test_df = pd.read_csv(filepath, encoding = "ISO-8859-1")
    test_df.dropna(subset=['Question','Response','Answer'], inplace=True)
    test_df = test_df.loc[:, ['Question','Response','Answer']]
    test_df['Response']=test_df['Response'].astype('string')
    test_df['Answer']=test_df['Answer'].astype('string')
    test_df['Question']=test_df['Question'].astype('string')
    
    remove_character(test_df['Response'])
    #test_df['Question'] = test_df['Question'].apply(remove_number_period)
    analysis_df = response_analysis(test_df, 'Response', 'Answer', 'Question')

        
    # extract filename from filepath variable:
    file=os.path.basename(filepath)

    # write to new csv file using original filename to identify:
    analysis_df.to_csv('CorrectnessPlusSimilarity_' + file, sep=',', index=False, encoding='utf-8')
    
    
    
    