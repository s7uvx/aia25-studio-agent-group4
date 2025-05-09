"""Imports files from the data folder to the chromaDB vectorstore"""

import argparse
import os
import shutil
import more_itertools as it
from wakepy import keep
from llama_parse import LlamaParse
import os
# from langchain_community.document_loaders import PyPDFDirectoryLoader
# from langchain_community.vectorstores import Chroma
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain.schema.document import Document
# from chromadb.config import Settings

# get api key from .env
from dotenv import load_dotenv
import os

load_dotenv()

llama_parse_key = os.getenv("LLAMA_PARSE_KEY")

# from get_embedding_function import get_embedding_function

CHROMA_PATH = "chroma"
DATA_PATH = "source_data"

def main():
    with keep.running():
        """run the main script"""
        # Check if the database should be cleared (using the --clear flag).
        parser = LlamaParse(
            api_key=llama_parse_key,
            result_type="markdown",  # "markdown" or "text"
        num_workers=4,
        verbose=True,
        language="en",
        )

        for doc in os.listdir(DATA_PATH):
            if doc.endswith(".pdf"):
                pdf = parser.parse(os.path.join(DATA_PATH, doc))
                markdown_document = pdf.get_markdown_documents(split_by_page=False)
                with open(os.path.join(DATA_PATH, doc.replace(".pdf", ".md")), "w") as f:
                    f.write(markdown_document)

        # # Create (or update) the data store.
        # documents = load_documents()
        # chunks = split_documents(documents)
        # add_to_chroma(chunks)


# def load_documents():
#     """load pdf documents"""
#     document_loader = PyPDFDirectoryLoader(DATA_PATH)
#     return document_loader.load()


# def split_documents(documents: list[Document]):
#     """split documents into their chunks"""
#     text_splitter = RecursiveCharacterTextSplitter(
#         separators=[
#             "\n\n",
#             "\n",
#             " ",
#             ".",
#             ",",
#             "\u200b",  # Zero-width space
#             "\uff0c",  # Fullwidth comma
#             "\u3001",  # Ideographic comma
#             "\uff0e",  # Fullwidth full stop
#             "\u3002",  # Ideographic full stop
#             "",
#         ],
#         chunk_size=1200,
#         chunk_overlap=60,
#         length_function=len,
#         is_separator_regex=False,
#     )
#     return text_splitter.split_documents(documents)


# def add_to_chroma(chunks: list[Document], args):
#     """add chunks to the chromaDB"""
#     # Load the existing database.
#     db = Chroma(
#         persist_directory=CHROMA_PATH,
#         embedding_function=get_embedding_function(),
#         client_settings=Settings(anonymized_telemetry=False, is_persistent=True)
#     )

#     # Calculate Page IDs.
#     chunks_with_ids = calculate_chunk_ids(chunks)

#     # Add or Update the documents.
#     existing_items = db.get(include=[])  # IDs are always included by default
#     existing_ids = set(existing_items["ids"])
#     print(f"Number of existing documents in DB: {len(existing_ids)}")

#     if args.update is True:
#         i=0
#         for subchunk in it.chunked(chunks_with_ids, 500):
#             print(f"👉 Updating {len(subchunk)+i*500} new documents of {len(chunks_with_ids)}")
#             chunk_ids = [chunky.metadata["id"] for chunky in subchunk]
#             db.update_documents(ids=chunk_ids, documents=subchunk)
#             i+=1
        
#     else:
#         # Only add documents that don't exist in the DB.
#         new_chunks = []
#         for chunk in chunks_with_ids:
#             if chunk.metadata["id"] not in existing_ids:
#                 new_chunks.append(chunk)

#         if new_chunks:
#             i=0
#             for subchunk in it.chunked(new_chunks, 500):
#                 print(f"👉 Adding {len(subchunk)+i*500} new documents of {len(new_chunks)}")
#                 new_chunk_ids = [chunky.metadata["id"] for chunky in subchunk]
#                 db.add_documents(subchunk, ids=new_chunk_ids)
#                 i+=1
#                 # db.persist()
#         else:
#             print("✅ No new documents to add")


# def calculate_chunk_ids(chunks):
#     """add chunk metadata for recall"""
#     last_page_id = None
#     current_chunk_index = 0

#     for chunk in chunks:
#         source = chunk.metadata.get("source")
#         page = chunk.metadata.get("page")
#         current_page_id = f"{source}:{page}"

#         # If the page ID is the same as the last one, increment the index.
#         if current_page_id == last_page_id:
#             current_chunk_index += 1
#         else:
#             current_chunk_index = 0

#         # Calculate the chunk ID.
#         chunk_id = f"{current_page_id}:{current_chunk_index}"
#         last_page_id = current_page_id

#         # Add it to the page meta-data.
#         chunk.metadata["id"] = chunk_id

#     return chunks


# def clear_database():
#     """clear the database if the user uses the --reset flag"""
#     if os.path.exists(CHROMA_PATH):
#         shutil.rmtree(CHROMA_PATH)


if __name__ == "__main__":
    main()
