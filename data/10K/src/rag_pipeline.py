import os
import pickle
import chromadb
from llama_index.core import VectorStoreIndex, StorageContext, Settings, QueryBundle
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.query_engine import RetrieverQueryEngine  # <--- NEW IMPORT
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

# --- CONFIGURATION ---
PERSIST_DIR = "./data/storage"
CHROMA_DB_DIR = "./data/chromadb"
COLLECTION_NAME = "financial_10k"

# --- 1. DEFINE HYBRID RETRIEVER CLASS ---
class HybridRetriever(BaseRetriever):
    def __init__(self, vector_retriever, bm25_retriever):
        self.vector_retriever = vector_retriever
        self.bm25_retriever = bm25_retriever
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle):
        # 1. Get Vector Results
        vector_nodes = self.vector_retriever.retrieve(query_bundle)
        
        # 2. Get BM25 Results
        bm25_nodes = self.bm25_retriever.retrieve(query_bundle)

        # 3. Combine Results (De-duplicate by node ID)
        all_nodes = {}
        for node in vector_nodes:
            all_nodes[node.node.node_id] = node
        
        for node in bm25_nodes:
            if node.node.node_id not in all_nodes:
                all_nodes[node.node.node_id] = node
        
        return list(all_nodes.values())

# --- 2. SETUP FUNCTION ---
def get_rag_engine(model_name="llama3:8b"):
    print(f"⚙️ Loading RAG Engine with {model_name}...")
    
    # A. Load Embeddings
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3")
    
    # B. Load LLM
    Settings.llm = Ollama(model=model_name, request_timeout=300.0)

    # C. Load Vector Index directly from ChromaDB
    db = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    chroma_collection = db.get_or_create_collection(COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    vector_index = VectorStoreIndex.from_vector_store(
        vector_store,
        storage_context=storage_context,
        embed_model=Settings.embed_model
    )
    
    # D. Load BM25 Index
    with open(os.path.join(PERSIST_DIR, 'nodes.pkl'), 'rb') as f:
        nodes = pickle.load(f)
    bm25_retriever = BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=5)

    # E. Create Hybrid Retriever
    vector_retriever = vector_index.as_retriever(similarity_top_k=5)
    hybrid_retriever = HybridRetriever(vector_retriever, bm25_retriever)

    # F. Create Engine (The Fix: Use generic RetrieverQueryEngine)
    query_engine = RetrieverQueryEngine.from_args(
        retriever=hybrid_retriever,
        llm=Settings.llm
    )
    
    return query_engine

# --- 3. TEST RUN ---
if __name__ == "__main__":
    engine = get_rag_engine("llama3:8b")
    
    print("Testing Query...")
    # CHANGED: Use a question that exists in your 5 PDFs
    response = engine.query("What specific risk factors does Alphabet (Google) list regarding Generative AI?")
    
    print("\n\n💬 RESPONSE:\n")
    print(response)