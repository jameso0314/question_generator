# import chromadb
# from chromadb.config import Settings
# from chromadb.utils import embedding_functions
# from sentence_transformers import SentenceTransformer
# import numpy as np
# import uuid

# # Initialize model and ChromaDB client
# model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# try:
#     client = chromadb.PersistentClient(path="chromadb_data")
#     embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
#         model_name='all-MiniLM-L6-v2'
#     )
#     collection = client.get_or_create_collection(
#         name="questions", 
#         embedding_function=embedding_func,
#         metadata={"hnsw:space": "cosine"}
#     )
# except Exception as e:
#     print(f"Error initializing ChromaDB client: {e}")
#     client, collection, embedding_func = None, None, None

# def add_question(question, topic):
#     if not collection:
#         print("ChromaDB client is not initialized.")
#         return
#     embedding = model.encode([question])[0].tolist()
#     collection.add(
#         documents=[question],
#         metadatas=[{'topic': topic}],
#         embeddings=[embedding],
#         ids=[str(uuid.uuid4())]  # Generate a unique ID for each document
#     )

# def is_similar(new_question, topic, threshold=0.85):
#     if not collection:
#         print("ChromaDB client is not initialized.")
#         return False
#     # Check if the topic exists
#     existing_docs = collection.query(
#         query_texts=[f"What is the question related to {topic}?"],
#         n_results=1
#     )
#     if not existing_docs['documents']:
#         return False
    
#     # If the topic exists, proceed to check similarity
#     embedding = model.encode([new_question])[0].tolist()
#     similar_docs = collection.query(
#         query_embeddings=[embedding], 
#         n_results=10
#     )
#     for doc, dist in zip(similar_docs['documents'], similar_docs['distances']):
#         if 'metadata' in doc and 'topic' in doc['metadata'] and doc['metadata']['topic'] == topic and dist < threshold:
#             return True
#     return False
