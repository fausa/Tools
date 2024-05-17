from sentence_transformers import CrossEncoder

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
from transformers import pipeline


##########################################################################
##########################################################################

# USAGE:
# enter the filepath and filename as prompted

# INPUT
# Input file should be a csv file list of questions to be sent to the bot,
# along with the generated output, and the ground truth or expected answer.

# OUTPUT:
# This will output a csv file with the Original question, the bot responses,
# the ground truth responses, along with the correctness, as calculated by 
# langchain's evaluator, cosine similarity, and Vectara's Hallucination 
# scores

##########################################################################
##########################################################################

#api_key=
os.environ['OPENAI_API_KEY'];
huggingfacehub_api_token=os.environ['HUGGINGFACEHUB_API_TOKEN']

# Load the hallucination evaluation model
hallucination_evaluator = pipeline("text-classification", model="vectara/hallucination_evaluation_model")


# User inputs:

filepath=input("Please enter the path and filename of the csv that contains the questions, bot responses, and root truth answers that require analysis:\n")

# If needed, some text cleaning:
def remove_number_period(text):
    return re.sub(r'^\d{1,3}\.', '', text)

def remove_character(s):
    return s.replace('Â', '')

# Define tokenizer/models:
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


# Evaluate responses
def evaluate_vectara(ground_truth, generated):
    evaluation = hallucination_evaluator(f"Ground Truth: {ground_truth} Response: {generated}")
    return evaluation
    #print(f"Response: {item['response']}\nGround Truth: {item['ground_truth']}\nEvaluation: {evaluation}\n")


# Define a custom evaluator
def evaluate2(ground_truth, generated):
    ground_truth_embedding = get_embedding(ground_truth)
    generated_embedding = get_embedding(generated)
    return cosine_similarity(ground_truth_embedding, generated_embedding)



def response_analysis(dataframe, column_name, column_name2, column_name3):


    results = []



    for i, row in dataframe.iterrows():
        sentence = row[column_name]
        sentence2 = row[column_name2]
        sentence3 = row[column_name3]
        try:

            evaluator=load_evaluator("labeled_criteria",criteria="correctness")
            eval_result=evaluator.evaluate_strings(prediction=sentence, input=sentence3, reference=sentence2)
        
            ground_truth = sentence2
            generated_response = sentence

            score = evaluate2(ground_truth, generated_response)
            vectara_score = evaluate_vectara(ground_truth, generated_response)
    
            results.append({'Response': sentence, 'Answer': sentence2, 'Correctness Score': eval_result['score'],
                           'Reason': eval_result['reasoning'].replace('\n','').split('.')[:-1],
                           'Similarity': score,
                           'Vectara Score': vectara_score
                           })
            
            
        except Exception as e:
            print(f"An error occurred: {e}")
            results.append({'Response': sentence, 'Answer': sentence2, 'Correctness Score': [], 'Reason': [],
                           'Similarity': [],
                           'Vectara Score':[]
                           })

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
    analysis_df.to_csv('Correctness_Similarity_Vectara_Scores' + file, sep=',', index=False, encoding='utf-8')
    
    
    
  