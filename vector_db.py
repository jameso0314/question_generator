import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
import numpy as np
import uuid

class VectorDB:
    def __init__(self, db_path="chromadb_data"):
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        self.client = chromadb.PersistentClient(path=db_path)
        self.embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name='all-MiniLM-L6-v2'
        )
        self.collection = self.client.get_or_create_collection(
            name="questions", 
            embedding_function=self.embedding_func,
            metadata={"hnsw:space": "cosine"}
        )

    def add_question(self, question, topic):
        embedding = self.model.encode([question])[0].tolist()
        self.collection.add(
            documents=[question],
            metadatas=[{'topic': topic}],
            embeddings=[embedding],
            ids=[str(uuid.uuid4())]  # Generate a unique ID for each document
        )

    def is_similar(self, new_question, topic, threshold=0.85):
        # Check if the topic exists
        existing_docs = self.collection.query(
            query_texts=[f"What is the question related to {topic}?"],
            n_results=1
        )
        if not existing_docs['documents']:
            return False
        
        # If the topic exists, proceed to check similarity
        embedding = self.model.encode([new_question])[0].tolist()
        similar_docs = self.collection.query(
            query_embeddings=[embedding], 
            n_results=10
        )
        for doc, dist in zip(similar_docs['documents'], similar_docs['distances']):
            if 'metadata' in doc and 'topic' in doc['metadata'] and doc['metadata']['topic'] == topic and dist < threshold:
                return True
        return False
