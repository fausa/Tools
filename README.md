# Tools for Data Science 

#### -- Programming Language: Python, Jupyter Notebooks

## Goals
Develop open-source tools to help build upon and use for machine learning/AI projects

## Currently available 
* Data Collection via Webcrawl/Scrape
* Load/embed/store files needed to implement RAG
* Generate variations of a given question (utterances) from a csv file using ChatGPT4
* Evaluate an llm's chatbot responses using LangChain's correctness and cosine similarity scores

## Future Tools
* Data Engineering
* Open-Source LLM chats
* Natural language processing
* Transfer learning

## Purpose
A resource for gathered learning around methods to build upon and assist in larger AI projects

## Motivation
Many tools are available at a cost, or through API's when they can be easily implemented by the developer. 
These tools are meant to be a place to start, and might help with some basic needs.

## Usage
1. webscrape.py
   * Copy/clone to personal directory (remove any appended slashes from the name)
   * Run from prompt window: python webscrape.py
   * Enter precise parent URL address (make sure to use the secure https name if needed)
   * Enter output filename - data will be output as a JSON file
   * Run
2. ingest_data.py
    * Make sure you have a huggingface API token saved in your computer as an environment variable
    * Run from prompt window
    * Enter local path to datafiles (mixed)
    * Enter local path for FAISS vector database indicies - future versions will add options for Chroma and others
    * Your datafiles are then loaded, embeded using HuggingFace (sentence-transformers/all-MiniLM-L6-v2) and stored in a FAISS vector database for use with your LLM
3. utterances_generation.py
    * Make sure your original csv file contains a column named 'Question'
    * Have a valid OpenAI key for using ChatGPT4 API saved into your environment variables
    * Make sure you have enough funds/credits for API usage (1.48 to generate 20 utterances for 102 questions) 
    * Make sure filepath given ends with the final backslash
    * Run
4. llm_evaluator.py
    * Make sure the input csv file contains columns named 'Question', 'Response', and 'Answer'
    * Have a HuggingFace key
    * Run   
## How do the tools work?
Please communicate any errors or shortcomings as these tools are by no means complete and final solutions - that way they can be fixed. 
Thanks in advance ✨

