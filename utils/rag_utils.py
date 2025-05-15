from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from collections import Counter
import re

import chromadb
from chromadb.config import Settings
from server.config import *
# from llm_calls import rag_answer

from flashrank import Ranker, RerankRequest

CHROMA_PATH = "chroma"

def get_chroma_client():
    """Get ChromaDB client with embedding function"""
    from chromadb.utils import embedding_functions
    
    # Use the same embedding function as during creation
    embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
        api_base="http://localhost:1234/v1",
        api_key="not-needed",
        model_name="nomic-embed-text"
    )
    
    client = chromadb.PersistentClient(
        path=CHROMA_PATH,
        settings=Settings(anonymized_telemetry=False)
    )
    return client, embedding_fn
# This script is only used as a RAG tool for other scripts.

def get_embedding(text, model=embedding_model):
    text = text.replace("\n", " ")
    if mode == "openai":
        response = client.embeddings.create(input = [text], dimensions = 768, model=model)
    else:
        response = client.embeddings.create(input = [text], model=model)
    vector = response.data[0].embedding
    return vector

def rag_answer(question, prompt, model=completion_model):
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", 
             "content": prompt
            },
            {"role": "user", 
             "content": question
            }
        ],
        temperature=0.1,
    )
    return completion.choices[0].message.content

def rerank_results(results, question, max_length=4000):
    """Rerank results and trim to fit context window"""
    # Calculate relevance scores using basic keyword matching
    scored_results = []
    question_words = set(question.lower().split())
    
    for doc in results['documents'][0]:
        # Count keyword matches
        doc_words = set(doc.lower().split())
        score = len(question_words.intersection(doc_words))
        
        # Add document length as a penalty factor
        length_penalty = len(doc) / 1000  # Penalize very long documents
        final_score = score / length_penalty
        
        scored_results.append((doc, final_score))
    
    # Sort by score and select best results that fit in context
    scored_results.sort(key=lambda x: x[1], reverse=True)
    
    selected_docs = []
    total_length = 0
    
    for doc, _ in scored_results:
        if total_length + len(doc) <= max_length:
            selected_docs.append(doc)
            total_length += len(doc)
    
    return selected_docs

def calculate_semantic_similarity(query_embedding, doc_embedding):
    """Calculate cosine similarity between query and document embeddings"""
    return cosine_similarity(
        np.array(query_embedding).reshape(1, -1),
        np.array(doc_embedding).reshape(1, -1)
    )[0][0]

def calculate_keyword_score(question, doc):
    """Calculate keyword matching score with weights for important terms"""
    # Architecture-specific important keywords
    important_keywords = {
        'architect': 2.0, 'design': 1.5, 'building': 1.5, 'structure': 1.5,
        'space': 1.5, 'form': 1.5, 'function': 1.5, 'style': 1.2,
        'material': 1.2, 'construction': 1.2
    }
    
    question_words = question.lower().split()
    doc_words = doc.lower().split()
    
    # Count matching keywords with weights
    score = 0
    for word in question_words:
        if word in doc_words:
            score += important_keywords.get(word, 1.0)
    
    return score

def calculate_position_score(doc_index, total_docs):
    """Give higher weight to documents appearing earlier in search results"""
    return 1 - (doc_index / total_docs)

def enhanced_rerank_results(results, question, max_length=4000):
    """Enhanced reranking using multiple signals"""
    scored_results = []
    total_docs = len(results['documents'][0])
    
    # Get question embedding
    question_embedding = results['embeddings'][0]
    
    for idx, (doc, doc_embedding) in enumerate(zip(results['documents'][0], results['embeddings'])):
        # Calculate different scoring signals
        semantic_score = calculate_semantic_similarity(question_embedding, doc_embedding)
        keyword_score = calculate_keyword_score(question, doc)
        position_score = calculate_position_score(idx, total_docs)
        
        # Calculate document density (information per length)
        doc_length = len(doc)
        unique_words = len(set(doc.lower().split()))
        density_score = unique_words / (doc_length + 1)  # Add 1 to avoid division by zero
        
        # Combine scores with weights
        final_score = (
            semantic_score * 0.4 +    # Semantic similarity
            keyword_score * 0.3 +     # Keyword matching
            position_score * 0.2 +    # Position in results
            density_score * 0.1       # Information density
        )
        
        scored_results.append((doc, final_score))
    
    # Sort by score and select best results that fit context
    scored_results.sort(key=lambda x: x[1], reverse=True)
    
    selected_docs = []
    total_length = 0
    context_window = max_length
    
    for doc, score in scored_results:
        if total_length + len(doc) <= context_window:
            selected_docs.append(doc)
            total_length += len(doc)
    
    return selected_docs

def rag_call(question, n_results=10, max_context_length=4000):
    """Updated RAG call using enhanced reranking"""
    print("Initiating RAG with enhanced reranking...")
    
    client, embedding_fn = get_chroma_client()
    collections = client.list_collections()
    if not collections:
        raise ValueError("No collections found in the database.")
    
    # Get collection WITH embedding function
    collection = client.get_collection(
        name=collections[0].name,
        embedding_function=embedding_fn
    )
    
    # Rest of the function remains the same
    results = collection.query(
        query_texts=[question],
        n_results=n_results * 2,
        include=['embeddings', 'documents']
    )
    
    # Apply enhanced reranking
    selected_docs = enhanced_rerank_results(results, question, max_context_length)
    rag_result = "\n".join(selected_docs)
    
    prompt = f"""Answer the question based on the provided information.
                Focus on the most relevant details and maintain coherence.
                If you don't know the answer, just say "I do not know."
                QUESTION: {question}
                PROVIDED INFORMATION: {rag_result}"""
    
    return rag_answer(question=question, prompt=prompt)

def init_rag():
    print("Initiating RAG with enhanced reranking...")
    
    client, embedding_fn = get_chroma_client()
    collections = client.list_collections()
    if not collections:
        raise ValueError("No collections found in the database.")
    
    # Get collection WITH embedding function
    collection = client.get_collection(
        name=collections[0].name,
        embedding_function=embedding_fn
    )

    print(os.getcwd())

    ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir=os.path.join(os.getcwd(), "models"))

    return collection, ranker

def rag_call_alt(question, collection, ranker, n_results=10, max_context_length=4000):
    results = collection.query(
        query_texts=[question],
        n_results=n_results * 2,
        include=['embeddings', 'documents']
    )

    
    passagedocs = [{'id': i, 'text': doc} for i, doc in enumerate(results['documents'][0])]
    rerankrequest = RerankRequest(query=question, passages=passagedocs)

    selected_docs = ranker.rerank(rerankrequest)

    # rag_result = "\n".join(selected_docs)
    rag_result = "\n".join([doc['text'] for doc in selected_docs])[:max_context_length]


    prompt = f"""Answer the question based on the provided information.
                Focus on the most relevant details and maintain coherence.
                If you don't know the answer, just say "I do not know."
                QUESTION: {question}
                PROVIDED INFORMATION: {rag_result}"""
    
    return rag_answer(question=question, prompt=prompt)
