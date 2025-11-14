"""
Qdrant Vector Store Implementation
High-performance local vector database with persistent storage
"""

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    Range
)
from typing import List, Dict, Optional, Any
import uuid
from sentence_transformers import SentenceTransformer


class QdrantVectorStore:
    """
    Local vector database using Qdrant.
    Faster than ChromaDB, better filtering, production-ready.
    """
    
    def __init__(
        self,
        collection_name: str = "default_collection",
        host: str = "localhost",
        port: int = 6333,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize Qdrant client and embedding model.
        
        Args:
            collection_name: Name of the collection
            host: Qdrant server host
            port: Qdrant server port
            embedding_model: SentenceTransformer model name
        """
        # Connect to Qdrant server
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        
        # Initialize embedding model
        print(f"Loading embedding model: {embedding_model}...")
        self.encoder = SentenceTransformer(embedding_model)
        self.vector_size = self.encoder.get_sentence_embedding_dimension()
        
        # Create collection if doesn't exist
        self._ensure_collection()
        
        print(f"✓ Connected to Qdrant at {host}:{port}")
        print(f"✓ Collection '{collection_name}' ready (dim={self.vector_size})")
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [col.name for col in collections]
        
        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            print(f"✓ Created new collection: {self.collection_name}")
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of text documents
            metadatas: Optional metadata for each document
            ids: Optional custom IDs (auto-generated if None)
            
        Returns:
            List of document IDs
        """
        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(documents))]
        
        # Generate embeddings
        embeddings = self.encoder.encode(documents, show_progress_bar=False)
        
        # Prepare metadata
        if metadatas is None:
            metadatas = [{} for _ in range(len(documents))]
        
        # Add document text to metadata for retrieval
        for i, doc in enumerate(documents):
            metadatas[i]["text"] = doc
        
        # Create points
        points = [
            PointStruct(
                id=ids[i],
                vector=embeddings[i].tolist(),
                payload=metadatas[i]
            )
            for i in range(len(documents))
        ]
        
        # Upload to Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        print(f"✓ Added {len(documents)} documents")
        return ids
    
    def query(
        self,
        query_text: str,
        n_results: int = 5,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[Any]]:
        """
        Query the vector store for similar documents.
        
        Args:
            query_text: Query string
            n_results: Number of results to return
            filter_conditions: Optional metadata filters
                Example: {"category": "tech", "year": 2024}
            
        Returns:
            Dictionary with ids, documents, metadatas, and scores
        """
        # Generate query embedding
        query_vector = self.encoder.encode(query_text).tolist()
        
        # Build filter if provided
        query_filter = None
        if filter_conditions:
            conditions = []
            for key, value in filter_conditions.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
            query_filter = Filter(must=conditions)
        
        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=n_results,
            query_filter=query_filter,
            with_payload=True
        )
        
        # Format results
        ids = [hit.id for hit in results]
        documents = [hit.payload.get("text", "") for hit in results]
        metadatas = [
            {k: v for k, v in hit.payload.items() if k != "text"}
            for hit in results
        ]
        scores = [hit.score for hit in results]
        
        return {
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas,
            "scores": scores
        }
    
    def get_by_ids(self, ids: List[str]) -> Dict[str, List[Any]]:
        """
        Retrieve documents by their IDs.
        
        Args:
            ids: List of document IDs
            
        Returns:
            Dictionary with documents and metadata
        """
        results = self.client.retrieve(
            collection_name=self.collection_name,
            ids=ids,
            with_payload=True
        )
        
        documents = [r.payload.get("text", "") for r in results]
        metadatas = [
            {k: v for k, v in r.payload.items() if k != "text"}
            for r in results
        ]
        
        return {
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas
        }
    
    def update_documents(
        self,
        ids: List[str],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Update existing documents.
        
        Args:
            ids: IDs of documents to update
            documents: New document texts (optional)
            metadatas: New metadata (optional)
        """
        if documents is not None:
            # Re-embed and update
            self.add_documents(documents, metadatas, ids)
        elif metadatas is not None:
            # Update metadata only
            for i, doc_id in enumerate(ids):
                self.client.set_payload(
                    collection_name=self.collection_name,
                    payload=metadatas[i],
                    points=[doc_id]
                )
        
        print(f"✓ Updated {len(ids)} documents")
    
    def delete_documents(self, ids: List[str]) -> None:
        """
        Delete documents by ID.
        
        Args:
            ids: List of document IDs to delete
        """
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=ids
        )
        print(f"✓ Deleted {len(ids)} documents")
    
    def count(self) -> int:
        """Return the number of documents in the collection."""
        info = self.client.get_collection(self.collection_name)
        return info.points_count
    
    def reset(self) -> None:
        """Clear all documents from the collection."""
        self.client.delete_collection(self.collection_name)
        self._ensure_collection()
        print(f"✓ Reset collection {self.collection_name}")
    
    def list_collections(self) -> List[str]:
        """List all available collections."""
        collections = self.client.get_collections().collections
        return [col.name for col in collections]
    
    def switch_collection(self, collection_name: str) -> None:
        """
        Switch to a different collection.
        
        Args:
            collection_name: Name of collection to switch to
        """
        self.collection_name = collection_name
        self._ensure_collection()
        print(f"✓ Switched to collection: {collection_name}")


def main():
    """
    Example usage demonstrating Qdrant features.
    """
    # Initialize vector store
    store = QdrantVectorStore(
        collection_name="documents",
        host="localhost",
        port=6333
    )
    
    # Example 1: Add documents with metadata
    documents = [
        "Qdrant is a high-performance vector database written in Rust",
        "Vector embeddings capture semantic meaning of text efficiently",
        "Machine learning models understand context through embeddings",
        "RAG systems combine retrieval with language generation",
        "Python is widely used for AI and machine learning development"
    ]
    
    metadatas = [
        {"category": "database", "language": "rust", "year": 2023},
        {"category": "embeddings", "year": 2023},
        {"category": "ml", "year": 2024},
        {"category": "architecture", "year": 2024},
        {"category": "programming", "language": "python", "year": 2024}
    ]
    
    ids = store.add_documents(documents, metadatas=metadatas)
    
    # Example 2: Semantic search
    print("\n" + "="*50)
    print("SEMANTIC SEARCH")
    print("="*50)
    results = store.query(
        query_text="How do I store vectors efficiently?",
        n_results=3
    )
    
    for i, (doc, metadata, score) in enumerate(zip(
        results['documents'],
        results['metadatas'],
        results['scores']
    )):
        print(f"\n{i+1}. [Score: {score:.4f}]")
        print(f"   {doc}")
        print(f"   Metadata: {metadata}")
    
    # Example 3: Filtered search (Qdrant's strength)
    print("\n" + "="*50)
    print("FILTERED SEARCH (category='ml')")
    print("="*50)
    filtered_results = store.query(
        query_text="machine learning concepts",
        n_results=2,
        filter_conditions={"category": "ml"}
    )
    
    for doc in filtered_results['documents']:
        print(f"  • {doc}")
    
    # Example 4: Stats
    print("\n" + "="*50)
    print("STATS")
    print("="*50)
    print(f"Total documents: {store.count()}")
    print(f"Collections: {store.list_collections()}")
    
    # Example 5: Get by ID
    print("\n" + "="*50)
    print("GET BY ID")
    print("="*50)
    retrieved = store.get_by_ids([ids[0]])
    print(f"Retrieved: {retrieved['documents'][0]}")


if __name__ == "__main__":
    main()
