from langchain.prompts import PromptTemplate
from ctransformers import AutoConfig, AutoModelForCausalLM, Config
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import CTransformers
from langchain.chains import RetrievalQA
import chainlit as cl
import os

DB_FAISS_PATH = "vectorstore/db_faiss/"
huggingfacehub_api_token=os.environ['HUGGINGFACEHUB_API_TOKEN']


custom_prompt_template='''Use the following pieces of information to answer the users question.
If the question has to do with masters or doctoral degree, use information in the Graduate Catalog and 
if the question has to do with undergraduate or bachelor degree, use information in the Undergraduate Catalog.
If you don't know the answer, please just say that you don't know the answer. Don't make up an answer.

Context:{context}
question:{question}

Only returns the helpful answer below and nothing else.
Helpful answer
'''

print("dones")

def set_custom_prompt():
    '''
    Prompt template for QA retrieval for each vector store
    '''
    prompt = PromptTemplate(template=custom_prompt_template, input_variables=['context','question'])

    return prompt


def load_llm():

    config = AutoConfig(config=Config(temperature=0.5, 
                                      max_new_tokens=2048, context_length=2048, gpu_layers=1
                                     ),
                       )

    
    llm = CTransformers(
        model="TheBloke/Mistral-7B-Instruct-v0.1-GGUF",
        model_type="mistral-7b-instruct-v0.1.Q4_K_M.gguf",
        max_new_tokens=2048, #512,
        config = {'context_length' : 2048,'gpu_layers':1},
        #context_length=2048,
        temperature=0.5
    )
    return llm


def retrieval_qa_chain(llm,prompt,db):
    qa_chain=RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=db.as_retriever(search_kwargs={'k':3}),
        return_source_documents=True,
        chain_type_kwargs={'prompt':prompt  }
    )
    return qa_chain

def qa_bot():
    embeddings=HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2',
                                     model_kwargs={'device':'cpu'})
    #embeddings=HuggingFaceEmbeddings(model_name='sentence-transformers/msmarco-MiniLM-L6-cos-v5',
    #                                 model_kwargs={'device':'cpu'})
    db = FAISS.load_local(DB_FAISS_PATH,embeddings)
    llm=load_llm()
    qa_prompt=set_custom_prompt()
    qa = retrieval_qa_chain(llm,qa_prompt,db)
    return qa 


def final_result(query):
    qa_result=qa_bot()
    response=qa_result({'query':query})
    return response 

## chainlit here
@cl.on_chat_start
async def start():
    chain=qa_bot()
    msg=cl.Message(content="Firing up the info bot...")
    await msg.send()
    msg.content= "Hi, welcome to your info bot. What is your query?"
    await msg.update()
    cl.user_session.set("chain",chain)


@cl.on_message
async def main(message):
    chain=cl.user_session.get("chain")
    cb = cl.AsyncLangchainCallbackHandler(
        stream_final_answer=True, answer_prefix_tokens=["FINAL","ANSWER"])
    cb.ansert_reached=True
    # res=await chain.acall(message, callbacks=[cb])
    res=await chain.acall(message.content, callbacks=[cb])
    answer=res["result"]
    sources=res["source_documents"]

    if sources:
        answer+=f"\nSources: "+str(str(sources))
    else:
        answer+=f"\nNo Sources found"

    await cl.Message(content=answer).send() 