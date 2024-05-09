import os
import shutil
import pandas as pd

from langchain.schema import Document
from langchain.vectorstores.chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from data_preparation import final_data

CHROMA_PATH = "chromadb"

full_data = final_data

with open('openai_api_key.txt', 'r') as f:
    os.environ["openai_api_key"] = f.read().strip()

def main():
    documents = create_documents_from_dataframe(full_data)
    save_to_chroma(documents)

def create_documents_from_dataframe(df: pd.DataFrame):
    documents = [Document(page_content=row['combined_columns'], metadata={"url": row['listing_url']}) for index, row in df.iterrows()]
    return documents

def save_to_chroma(documents: list[Document]):
    lang_chroma_path = CHROMA_PATH
    if os.path.exists(lang_chroma_path):
        shutil.rmtree(lang_chroma_path)
    
    db = Chroma.from_documents(
        documents, OpenAIEmbeddings(), persist_directory=lang_chroma_path
    )
    db.persist()
    print(f"Saved {len(documents)} documents to {lang_chroma_path}.")

if __name__ == "__main__":
    main()
