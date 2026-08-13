import chromadb
from sentence_transformers import SentenceTransformer
import os

class KnowledgeBase:
    def __init__(self, collection_name="voice_agent_kb"):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection = self.client.get_or_create_collection(name=collection_name)
        print(f"Knowledge Base '{collection_name}' initialized.")

    def add_document(self, text: str, metadata: dict = None):
        embedding = self.encoder.encode(text).tolist()
        doc_id = str(hash(text))
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata] if metadata else None
        )

    def query(self, query_text: str, n_results: int = 2):
        query_embedding = self.encoder.encode(query_text).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results['documents'][0] if results['documents'] else []
