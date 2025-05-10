# """Imports files from the data folder to the chromaDB vectorstore"""

# import argparse
# import os
# import shutil
# import more_itertools as it
# from wakepy import keep
# from langchain_community.document_loaders import PyPDFDirectoryLoader
# from langchain_community.vectorstores import Chroma
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain.schema.document import Document
# from chromadb.config import Settings

# import chromadb
# from chromadb.config import Settings
# import os
# from PyPDF2 import PdfReader
# from tqdm import tqdm

# from get_embedding_function import get_embedding_function

# CHROMA_PATH = "chroma"
# DATA_PATH = "source_data"

# def read_pdf(file_path):
#     """Extract text from PDF file"""
#     reader = PdfReader(file_path)
#     text = ""
#     for page in reader.pages:
#         text += page.extract_text() + "\n"
#     return text

# def split_text(text, chunk_size=1000, overlap=100):
#     """Split text into overlapping chunks"""
#     chunks = []
#     start = 0
#     text_length = len(text)
    
#     while start < text_length:
#         end = start + chunk_size
#         chunk = text[start:end]
#         chunks.append(chunk)
#         start = end - overlap
    
#     return chunks

# def main():
#     with keep.running():
#         """run the main script"""
#         # Check if the database should be cleared (using the --clear flag).
#         parser = argparse.ArgumentParser()
#         parser.add_argument("--reset", action="store_true", help="Reset the database.")
#         parser.add_argument("--update", type=bool, default=False, help="Update database")
#         args = parser.parse_args()
#         if args.reset:
#             print("✨ Clearing Database")
#             clear_database()

#         # Create (or update) the data store.
#         documents = load_documents()
#         chunks = split_documents(documents)
#         add_to_chroma(chunks, args)


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


# if __name__ == "__main__":
#     main()
import argparse
import os
import shutil
from tqdm import tqdm
import chromadb
from chromadb.config import Settings
from PyPDF2 import PdfReader

CHROMA_PATH = "chroma"
SOURCE_DATA_DIR = "source_data"
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 60

def read_pdf(file_path):
    """Extract text from PDF file"""
    reader = PdfReader(file_path)
    text = ""
    for page_num, page in enumerate(reader.pages):
        text += f"Page {page_num + 1}: " + page.extract_text() + "\n"
    return text

def split_text(text, source_file):
    """Split text into overlapping chunks with metadata"""
    chunks = []
    chunk_ids = []
    metadata_list = []
    
    start = 0
    chunk_num = 0
    
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        
        # Create unique ID and metadata
        chunk_id = f"{source_file}_{chunk_num}"
        metadata = {
            "source": source_file,
            "chunk_number": chunk_num,
            "start_char": start,
            "end_char": end
        }
        
        chunks.append(chunk)
        chunk_ids.append(chunk_id)
        metadata_list.append(metadata)
        
        start = end - CHUNK_OVERLAP
        chunk_num += 1
    
    return chunks, chunk_ids, metadata_list

def identify_headings(text):
    """Identify potential headings in the text"""
    lines = text.split('\n')
    heading_indices = []
    
    for i, line in enumerate(lines):
        # Common heading patterns
        if (
            # All caps lines that aren't too long
            (line.isupper() and len(line) < 100) or
            # Lines ending with common heading punctuation
            line.strip().endswith(':') or
            # Numbered headings (e.g., "1.", "1.1", "A.")
            (line.strip() and line.strip()[0].isalnum() and line.strip().split('.')[0].isalnum()) or
            # Lines followed by blank lines (common heading pattern)
            (line.strip() and i < len(lines)-1 and not lines[i+1].strip())
        ):
            heading_indices.append(i)
    
    return lines, heading_indices

def split_text_with_headings(text, chunk_size=1000, overlap=100):
    """Split text into chunks while preserving headings with their content"""
    lines, heading_indices = identify_headings(text)
    chunks = []
    current_chunk = []
    current_length = 0
    last_heading = ""
    
    for i, line in enumerate(lines):
        # If this is a heading, store it
        if i in heading_indices:
            last_heading = line
        
        # Add the line to current chunk
        current_chunk.append(line)
        current_length += len(line) + 1  # +1 for newline
        
        # Check if we should create a new chunk
        if current_length >= chunk_size:
            # Join the current chunk and add it
            chunk_text = '\n'.join(current_chunk)
            chunks.append(chunk_text)
            
            # Start new chunk with overlap
            # Include the last heading for context
            current_chunk = []
            if last_heading:
                current_chunk.append(f"[Context: {last_heading.strip()}]")
            # Add some lines from the end of previous chunk for overlap
            overlap_lines = current_chunk[-overlap:]
            current_chunk.extend(overlap_lines)
            current_length = sum(len(line) + 1 for line in current_chunk)
    
    # Add the final chunk if there's anything left
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks

def get_existing_sources(collection):
    """Get list of already processed files from collection metadata"""
    try:
        metadata = collection.get()['metadatas']
        return set(m['source'] for m in metadata if 'source' in m)
    except:
        return set()
    
# def populate_database(args):
#     """Create or update the database with documents"""
#     client = chromadb.PersistentClient(
#         path=CHROMA_PATH,
#         settings=Settings(anonymized_telemetry=False)
#     )
    
#     # Create or get collection
#     collection_name = "cost_estimating"
#     if args.reset and collection_name in [col.name for col in client.list_collections()]:
#         client.delete_collection(collection_name)
#         print("✨ Cleared existing collection")
    
#     collection = client.create_collection(
#         name=collection_name,
#         metadata={"description": "cost estimation documents"},
#     )
    
#     print("Processing PDF files...")
#     for filename in tqdm(os.listdir(SOURCE_DATA_DIR)):
#         if filename.endswith('.pdf'):
#             file_path = os.path.join(SOURCE_DATA_DIR, filename)
            
#             # Extract text
#             text = read_pdf(file_path)
            
#             # Use the new splitting function
#             chunks = split_text_with_headings(text, chunk_size=1200, overlap=60)
#             chunk_ids = [f"{filename}_{i}" for i in range(len(chunks))]
#             metadata_list = [{
#                 "source": filename,
#                 "chunk_number": i,
#                 "has_heading": bool(chunks[i].startswith("[Context:"))
#             } for i in range(len(chunks))]
            
#             if args.update:
#                 # Update existing documents
#                 existing_ids = collection.get(ids=chunk_ids)["ids"]
#                 for i, chunk_id in enumerate(chunk_ids):
#                     if chunk_id in existing_ids:
#                         collection.update(
#                             ids=[chunk_id],
#                             documents=[chunks[i]],
#                             metadatas=[metadata_list[i]]
#                         )
#             else:
#                 # Add new documents in batches
#                 batch_size = 100
#                 for i in range(0, len(chunks), batch_size):
#                     end_idx = min(i + batch_size, len(chunks))
#                     collection.add(
#                         documents=chunks[i:end_idx],
#                         ids=chunk_ids[i:end_idx],
#                         metadatas=metadata_list[i:end_idx]
#                     )
    
#     total_docs = len(collection.get()["ids"])
#     print(f"✅ Database populated with {total_docs} total chunks")

# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--reset", action="store_true", help="Reset the database")
#     parser.add_argument("--update", action="store_true", help="Update existing documents")
#     args = parser.parse_args()
    
#     if not os.path.exists(SOURCE_DATA_DIR):
#         os.makedirs(SOURCE_DATA_DIR)
#         print(f"Created {SOURCE_DATA_DIR} directory. Please add PDF files to this directory.")
#         return
    
#     if args.reset:
#         if os.path.exists(CHROMA_PATH):
#             shutil.rmtree(CHROMA_PATH)
#             print("✨ Cleared Database")
    
#     populate_database(args)

# if __name__ == "__main__":
#     main()
def populate_database():
    """Create or update the database with documents"""
    client = chromadb.PersistentClient(
        path=CHROMA_PATH,
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Get or create collection
    collection_name = "architecture_docs"
    try:
        collection = client.get_collection(collection_name)
        print(f"Using existing collection: {collection_name}")
    except:
        collection = client.create_collection(
            name=collection_name,
            metadata={"description": "Architecture documents and papers"}
        )
        print(f"Created new collection: {collection_name}")
    
    # Get list of already processed files
    existing_sources = get_existing_sources(collection)
    
    # Process each PDF in the source_data directory
    new_files = False
    for filename in os.listdir(SOURCE_DATA_DIR):
        if filename.endswith('.pdf') and filename not in existing_sources:
            new_files = True
            print(f"\nProcessing new file: {filename}")
            file_path = os.path.join(SOURCE_DATA_DIR, filename)
            
            # Extract text
            text = read_pdf(file_path)
            
            # Split into chunks with headings
            chunks = split_text_with_headings(text)
            chunk_ids = [f"{filename}_{i}" for i in range(len(chunks))]
            metadata_list = [{
                "source": filename,
                "chunk_number": i,
                "has_heading": bool("[Context:" in chunk)
            } for i, chunk in enumerate(chunks)]
            
            # Add documents in batches
            batch_size = 100
            for i in range(0, len(chunks), batch_size):
                end_idx = min(i + batch_size, len(chunks))
                collection.add(
                    documents=chunks[i:end_idx],
                    ids=chunk_ids[i:end_idx],
                    metadatas=metadata_list[i:end_idx]
                )
                print(f"Added chunks {i} to {end_idx} of {len(chunks)}")
    
    if not new_files:
        print("\nNo new files to process!")
    else:
        print("\n✅ Database update complete!")
        total_docs = len(collection.get()['ids'])
        print(f"Total documents in collection: {total_docs}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database")
    args = parser.parse_args()
    
    if args.reset:
        if os.path.exists(CHROMA_PATH):
            shutil.rmtree(CHROMA_PATH)
            print("✨ Cleared existing database")
    
    populate_database()