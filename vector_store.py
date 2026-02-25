__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')


from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from config import CHROMA_DB_PATH, EMBEDDING_MODEL, COLLECTION_NAME
import chromadb

class VectorStoreManager:
    def __init__(self):
        # Embeddings usando modelo local
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Cliente ChromaDB persistente
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        
        # Vector store
        self.vector_store = None
        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Inicializa ou carrega o vector store"""
        try:
            self.vector_store = Chroma(
                client=self.client,
                collection_name=COLLECTION_NAME,
                embedding_function=self.embeddings
            )
        except Exception as e:
            print(f"Erro ao inicializar vector store: {e}")
    
    def add_documents(self, chunks):
        """Adiciona documentos ao vector store"""
        if not chunks:
            return False
        
        try:
            self.vector_store.add_documents(chunks)
            return True
        except Exception as e:
            print(f"Erro ao adicionar documentos: {e}")
            return False
    
    def similarity_search(self, query, k=4):
        """Busca por similaridade"""
        try:
            results = self.vector_store.similarity_search(query, k=k)
            return results
        except Exception as e:
            print(f"Erro na busca: {e}")
            return []
    
    def get_collection_count(self):
        """Retorna número de documentos no banco"""
        try:
            collection = self.client.get_collection(COLLECTION_NAME)
            return collection.count()
        except:
            return 0
    
    def delete_collection(self):
        """Deleta toda a coleção"""
        try:
            self.client.delete_collection(COLLECTION_NAME)
            self._initialize_vector_store()
            return True
        except Exception as e:
            print(f"Erro ao deletar coleção: {e}")
            return False