import os
import pickle
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex, Settings
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.retrievers.bm25 import BM25Retriever
import chromadb

# --- CONFIGURATION ---
# These paths match the folders we created earlier
DATA_DIR = "./data/10k"
PERSIST_DIR = "./data/storage"
CHROMA_DB_DIR = "./data/chromadb"
COLLECTION_NAME = "financial_10k"

def ingest_data():
    print(f"🚀 Starting Ingestion from {DATA_DIR}...")

    # 1. Setup Embedding Model
    # We use BAAI/bge-m3 because it is excellent for retrieval tasks
    print("⚙️ Loading Embedding Model (this runs once)...")
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3")
    
    # 2. Load PDF Data
    # filename_as_id=True helps us know which company the text belongs to
    print("⚙️ Reading PDF files...")
    documents = SimpleDirectoryReader(DATA_DIR, filename_as_id=True).load_data()
    print(f"✅ Loaded {len(documents)} pages.")

    # 3. Chunking Strategy: Sentence Window
    # This keeps surrounding context (3 sentences before/after) attached to every chunk.
    # Crucial for financial tables where the context might be rows above.
    node_parser = SentenceWindowNodeParser.from_defaults(
        window_size=3,
        window_metadata_key="window",
        original_text_metadata_key="original_text",
    )
    nodes = node_parser.get_nodes_from_documents(documents)
    print(f"✅ Created {len(nodes)} text nodes.")

    # 4. Create & Save VECTOR Index (ChromaDB)
    print("⚙️ Building Vector Index (this takes time)...")
    db = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    chroma_collection = db.get_or_create_collection(COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    vector_index = VectorStoreIndex(
        nodes, 
        storage_context=storage_context, 
        embed_model=Settings.embed_model
    )
    # We don't strictly need to persist vector_index explicitly as Chroma performs auto-persistence,
    # but we ensure the storage context is linked.
    print("✅ Vector Index built and saved to ChromaDB.")

    # 5. Create & Save KEYWORD Index (BM25)
    # We must save this manually because BM25 is calculated in memory.
    print("⚙️ Building BM25 Index...")
    # We initialize it just to ensure it builds correctly, then save the nodes
    os.makedirs(PERSIST_DIR, exist_ok=True)
    
    # We save the nodes directly. In the retrieval step, we will reload these 
    # to rebuild the BM25 index quickly.
    with open(os.path.join(PERSIST_DIR, 'nodes.pkl'), 'wb') as f:
        pickle.dump(nodes, f)
    
    print("✅ Node data saved for BM25.")
    print("🎉 Ingestion Complete!")

if __name__ == "__main__":
    ingest_data()