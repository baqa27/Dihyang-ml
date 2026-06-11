import os
import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from dotenv import load_dotenv

class GeminiEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        load_dotenv(override=True)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "MASUKKAN_API_KEY_ANDA_DI_SINI":
            return [[0.0] * 768 for _ in input]
            
        import google.genai as genai
        client = genai.Client(api_key=api_key)
        
        embeddings = []
        for text in input:
            try:
                result = client.models.embed_content(
                    model="gemini-embedding-2",
                    contents=text,
                    config=genai.types.EmbedContentConfig(output_dimensionality=768)
                )
                embeddings.append(result.embeddings[0].values)
            except Exception as e:
                print(f"Embedding error: {e}")
                embeddings.append([0.0] * 768)
        return embeddings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'chroma_db')

try:
    chroma_client = chromadb.PersistentClient(path=DB_PATH)
    # Gunakan default embedding (SentenceTransformers: all-MiniLM-L6-v2) yang berjalan secara lokal (offline)
    # Ini menghindari limit API Gemini (429 RESOURCE EXHAUSTED) untuk embedding.
    collection = chroma_client.get_or_create_collection(
        name="dieng_knowledge_local"
    )
except Exception as e:
    print(f"Error initializing ChromaDB: {e}")
    collection = None

def index_data(documents: list, metadatas: list, ids: list):
    """Mengosongkan collection lama dan mengindeks ulang data baru."""
    if not collection: return
    
    try:
        existing = collection.get()
        if existing and existing["ids"]:
            collection.delete(ids=existing["ids"])
            
        if documents:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"✅ RAG Engine: Berhasil mengindeks {len(documents)} dokumen ke ChromaDB.")
    except Exception as e:
        print(f"RAG Indexing Error: {e}")

def retrieve_relevant_context(query: str, n_results: int = 5) -> str:
    """Mengambil konteks destinasi yang paling relevan dengan query."""
    if not collection: return ""
    
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if not results['documents'] or not results['documents'][0]:
            return ""
            
        context_str = "BERIKUT ADALAH DATA DESTINASI/RETRIBUSI YANG RELEVAN DENGAN PERTANYAAN (WAJIB GUNAKAN DATA INI, JANGAN MENGARANG):\n\n"
        for doc in results['documents'][0]:
            context_str += f"---\n{doc}\n"
            
        return context_str
    except Exception as e:
        return f"DEBUG RAG ERROR: {str(e)}"
