import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.document_loaders import UnstructuredHTMLLoader, BSHTMLLoader
from langchain.document_loaders import TextLoader
from langchain.document_loaders import JSONLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import os

print("Please make sure you have a HUGGINGFACEHUB_API_TOKEN environment variable set up in your system\n")

path = input("Please provide the directory containing datafiles that need embedding and vector database storage: \n")
DATA_PATH = path

faiss_path = input("Please provide where you'd like to generate a FAISS vector database: \n")
DB_FAISS_PATH = faiss_path



huggingfacehub_api_token=os.environ['HUGGINGFACEHUB_API_TOKEN']

def create_vector_db():
    documents=[]
    processed_htmls=0
    processed_pdfs=0
    processed_txts=0
    processed_jsons=0
    for f in os.listdir(DATA_PATH):
        try:
            if f.endswith(".pdf"):
                pdf_path = DATA_PATH + f
                loader = PyPDFLoader(pdf_path)
                documents.extend(loader.load())
                processed_pdfs+=1
            elif f.endswith(".html"):
                html_path = DATA_PATH + f
                loader = BSHTMLLoader(html_path)
                documents.extend(loader.load())
                processed_htmls+=1
            elif f.endswith(".txt"):
                txt_path = DATA_PATH + f
                loader = TextLoader(txt_path)
                documents.extend(loader.load())
                processed_txts+=1
            elif f.endswith(".json"):
                json_path = DATA_PATH + f
                loader = JSONLoader(json_path)
                documents.extend(loader.load())
                processed_jsons+=1
                
        except:
            print("issue with ",f)
            pass
    print("Processed",processed_txts, "text files, ", processed_jsons,
          "json files, ", processed_htmls,"html files, and ",
          processed_pdfs,"pdf files")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    texts=text_splitter.split_documents(documents)

    embeddings=HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2',
                                     model_kwargs={'device':'cpu'})

    db=FAISS.from_documents(texts,embeddings)
    db.save_local(DB_FAISS_PATH)

if __name__=="__main__":
    create_vector_db()