"""
RAG Service

Vector database routing and query service.
Handles routing logic for multiple vector databases.
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.core.config import settings
from app.models import RAGDocument, RAGIndex, RAGQuery, RAGSwitchLog

logger = logging.getLogger(__name__)


class RAGServiceError(Exception):
    """Base exception for RAG service errors."""
    pass


class IndexNotFoundError(RAGServiceError):
    """RAG index not found."""
    pass


class VectorDBNotAvailableError(RAGServiceError):
    """Vector database not available."""
    pass


class RAGService:
    """
    RAG service for vector database routing and querying.
    
    Routing Logic:
    - file_size < 1MB → LightRAG
    - dataset_size > 1GB → Milvus
    - query.requires_metadata = true → Weaviate
    - structured_memory = true → Graphiti/Zep
    - user.plan = free → SupaVec
    - ocr_result_injected = true → SupaVec/LightRAG
    """
    
    def __init__(self):
        """Initialize RAG service."""
        self._vector_db_clients: dict[str, Any] = {}
        self._initialize_chromadb()
    
    def _initialize_chromadb(self) -> None:
        """Initialize ChromaDB client if configured."""
        if not settings.CHROMA_SERVER_HOST:
            logger.info("ChromaDB not configured. Using placeholder client.")
            return
        
        try:
            import chromadb
            
            chroma_client = chromadb.HttpClient(
                host=settings.CHROMA_SERVER_HOST,
                port=settings.CHROMA_SERVER_HTTP_PORT,
                headers={"Authorization": f"Bearer {settings.CHROMA_SERVER_AUTH_TOKEN}"} if settings.CHROMA_SERVER_AUTH_TOKEN else None,
            )
            
            # Test connection
            chroma_client.heartbeat()
            
            self._vector_db_clients["chromadb"] = {
                "type": "chromadb",
                "client": chroma_client,
                "is_available": True,
            }
            
            logger.info(f"✅ ChromaDB client initialized ({settings.CHROMA_SERVER_HOST}:{settings.CHROMA_SERVER_HTTP_PORT})")
            
        except ImportError:
            logger.warning("ChromaDB not installed. Install with: pip install chromadb")
        except Exception as e:
            logger.warning(f"Failed to initialize ChromaDB client: {e}. Using placeholder.")
    
    def select_vector_db(
        self,
        session: Session,
        index_id: uuid.UUID,
        query_requirements: dict[str, Any] | None = None,
    ) -> str:
        """
        Select appropriate vector database for a query.
        
        Args:
            session: Database session
            index_id: RAG index ID
            query_requirements: Optional query requirements dictionary
            
        Returns:
            Vector database type (e.g., "chromadb", "milvus", "weaviate")
        """
        if not query_requirements:
            query_requirements = {}
        
        # Get index
        index = session.get(RAGIndex, index_id)
        if not index:
            raise IndexNotFoundError(f"RAG index {index_id} not found")
        
        # Get index statistics
        document_count = session.exec(
            select(RAGDocument).where(RAGDocument.index_id == index_id)
        ).all()
        total_size = sum(len(doc.content) for doc in document_count)
        dataset_size_mb = total_size / (1024 * 1024)
        
        # Routing logic
        requires_metadata = query_requirements.get("requires_metadata", False)
        structured_memory = query_requirements.get("structured_memory", False)
        ocr_result_injected = query_requirements.get("ocr_result_injected", False)
        user_plan = query_requirements.get("user_plan", "free")
        
        # Structured memory → Graphiti/Zep (not implemented yet, fallback to SupaVec)
        if structured_memory:
            return "supavec"  # Fallback until Graphiti/Zep is integrated
        
        # Metadata filtering → Weaviate
        if requires_metadata:
            return "weaviate"
        
        # Large dataset → Milvus
        if dataset_size_mb > 1024:  # > 1GB
            return "milvus"
        
        # OCR result injected → SupaVec/LightRAG
        if ocr_result_injected:
            if dataset_size_mb < 1:  # < 1MB
                return "lightrag"
            return "supavec"
        
        # Free plan → SupaVec
        if user_plan == "free":
            return "supavec"
        
        # Small files → LightRAG
        if dataset_size_mb < 1:  # < 1MB
            return "lightrag"
        
        # Default → ChromaDB (lightweight)
        return "chromadb"
    
    def query(
        self,
        session: Session,
        index_id: uuid.UUID,
        query_text: str,
        top_k: int = 5,
        query_requirements: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Query a RAG index.
        
        Args:
            session: Database session
            index_id: RAG index ID
            query_text: Query text
            top_k: Number of results to return
            query_requirements: Optional query requirements
            
        Returns:
            Query results dictionary
        """
        start_time = datetime.utcnow()
        
        # Get index
        index = session.get(RAGIndex, index_id)
        if not index:
            raise IndexNotFoundError(f"RAG index {index_id} not found")
        
        # Select vector database
        vector_db_type = self.select_vector_db(
            session=session,
            index_id=index_id,
            query_requirements=query_requirements,
        )
        
        # Log routing decision
        routing_reason = self._generate_routing_reason(
            index_id=index_id,
            query_requirements=query_requirements,
            selected_db=vector_db_type,
            session=session,
        )
        
        switch_log = RAGSwitchLog(
            query_id=None,  # Will be set after query is logged
            routing_decision=vector_db_type,
            routing_reason=routing_reason,
        )
        session.add(switch_log)
        session.commit()
        session.refresh(switch_log)
        
        # Get vector DB client
        vector_db_client = self._get_vector_db_client(vector_db_type)
        
        # Execute query
        try:
            results = self._execute_query(
                client=vector_db_client,
                index_id=index_id,
                query_text=query_text,
                top_k=top_k,
                session=session,
            )
            
            latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Log query
            query_log = RAGQuery(
                index_id=index_id,
                query_text=query_text,
                results={
                    "vector_db": vector_db_type,
                    "top_k": top_k,
                    "results_count": len(results.get("results", [])),
                },
                latency_ms=latency_ms,
            )
            session.add(query_log)
            session.commit()
            session.refresh(query_log)
            
            # Update switch log with query ID
            switch_log.query_id = query_log.id
            session.add(switch_log)
            session.commit()
            session.refresh(switch_log)
            
            return {
                "query_id": str(query_log.id),
                "vector_db": vector_db_type,
                "results": results,
                "latency_ms": latency_ms,
            }
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}", exc_info=True)
            raise RAGServiceError(f"Query execution failed: {e}")
    
    def _get_vector_db_client(self, vector_db_type: str) -> Any:
        """
        Get client for a specific vector database.
        
        Args:
            vector_db_type: Vector database type
            
        Returns:
            Vector database client
        """
        if vector_db_type not in self._vector_db_clients:
            # Initialize client if not already initialized
            if vector_db_type == "chromadb":
                self._initialize_chromadb()
            else:
                # Placeholder client for other vector DBs
                self._vector_db_clients[vector_db_type] = {
                    "type": vector_db_type,
                    "is_available": False,
                }
        
        client = self._vector_db_clients.get(vector_db_type, {
            "type": vector_db_type,
            "is_available": False,
        })
        
        if not client.get("is_available"):
            logger.warning(f"Vector DB '{vector_db_type}' not available. Using placeholder.")
        
        return client
    
    def _execute_query(
        self,
        client: Any,
        index_id: uuid.UUID,
        query_text: str,
        top_k: int,
        session: Session,
    ) -> dict[str, Any]:
        """
        Execute query on vector database client.
        
        Args:
            client: Vector database client
            index_id: Index ID
            query_text: Query text
            top_k: Number of results
            session: Database session for fetching documents
            
        Returns:
            Query results with real document data
        """
        vector_db_type = client.get("type", "unknown")
        
        # If ChromaDB is available, use it for vector similarity search
        if vector_db_type == "chromadb" and client.get("is_available") and "client" in client:
            try:
                import chromadb
                from chromadb.utils import embedding_functions
                
                chroma_client = client["client"]
                
                # Get or create collection for this index
                collection_name = f"rag_index_{index_id}"
                try:
                    collection = chroma_client.get_collection(name=collection_name)
                except Exception:
                    # Collection doesn't exist, create it
                    collection = chroma_client.create_collection(name=collection_name)
                
                # Generate query embedding (using default embedding function)
                # For now, use a simple text search if embeddings aren't available
                # In production, you'd use an embedding model here
                
                # Query ChromaDB
                results = collection.query(
                    query_texts=[query_text],
                    n_results=top_k,
                )
                
                # Map ChromaDB results to our format
                query_results = []
                if results.get("ids") and len(results["ids"][0]) > 0:
                    for i, doc_id in enumerate(results["ids"][0]):
                        # Get document from database using the ID
                        doc = session.get(RAGDocument, uuid.UUID(doc_id))
                        if doc:
                            query_results.append({
                                "document_id": str(doc.id),
                                "content": doc.content,
                                "score": results.get("distances", [[1.0]])[0][i] if results.get("distances") else 0.9,
                                "metadata": doc.document_metadata,
                            })
                
                # If ChromaDB didn't return results, fall back to database search
                if not query_results:
                    return self._execute_database_query(session, index_id, query_text, top_k)
                
                return {
                    "results": query_results,
                    "vector_db": "chromadb",
                }
            except Exception as e:
                logger.warning(f"ChromaDB query failed: {e}. Falling back to database query.")
                return self._execute_database_query(session, index_id, query_text, top_k)
        
        # For other vector DBs or if ChromaDB is not available, use database-based search
        return self._execute_database_query(session, index_id, query_text, top_k)
    
    def _execute_database_query(
        self,
        session: Session,
        index_id: uuid.UUID,
        query_text: str,
        top_k: int,
    ) -> dict[str, Any]:
        """
        Execute query using database documents (fallback when vector DB is not available).
        
        Uses simple text matching to find relevant documents.
        In production, this could use full-text search or simple keyword matching.
        
        Args:
            session: Database session
            index_id: Index ID
            query_text: Query text
            top_k: Number of results
            
        Returns:
            Query results with real document data
        """
        # Get all documents for this index
        documents = session.exec(
            select(RAGDocument).where(RAGDocument.index_id == index_id)
        ).all()
        
        if not documents:
            return {
                "results": [],
                "vector_db": "database",
            }
        
        # Simple text matching: score based on keyword matches
        # In production, use proper full-text search or embeddings
        query_words = set(query_text.lower().split())
        scored_docs = []
        
        for doc in documents:
            content_words = set(doc.content.lower().split())
            # Calculate simple similarity score
            matches = len(query_words.intersection(content_words))
            total_words = len(query_words)
            score = matches / total_words if total_words > 0 else 0.0
            
            scored_docs.append({
                "document": doc,
                "score": score,
            })
        
        # Sort by score and take top_k
        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        top_docs = scored_docs[:top_k]
        
        # Format results
        results = []
        for item in top_docs:
            doc = item["document"]
            results.append({
                "document_id": str(doc.id),
                "content": doc.content,
                "score": item["score"],
                "metadata": doc.document_metadata,
            })
        
        return {
            "results": results,
            "vector_db": "database",
        }
    
    def create_index(
        self,
        session: Session,
        name: str,
        vector_db_type: str,
        owner_id: uuid.UUID,
    ) -> RAGIndex:
        """
        Create a new RAG index.
        
        Args:
            session: Database session
            name: Index name
            vector_db_type: Vector database type
            owner_id: Owner user ID
            
        Returns:
            RAGIndex instance
        """
        index = RAGIndex(
            name=name,
            vector_db_type=vector_db_type,
            owner_id=owner_id,
        )
        session.add(index)
        session.commit()
        session.refresh(index)
        
        logger.info(f"Created RAG index: {name} (ID: {index.id}, Vector DB: {vector_db_type})")
        
        return index
    
    def add_document(
        self,
        session: Session,
        index_id: uuid.UUID,
        content: str,
        metadata: dict[str, Any] | None = None,
        embedding: list[float] | None = None,
    ) -> RAGDocument:
        """
        Add a document to a RAG index.
        
        Args:
            session: Database session
            index_id: Index ID
            content: Document content
            metadata: Optional document metadata
            embedding: Optional pre-computed embedding
            
        Returns:
            RAGDocument instance
        """
        # Verify index exists
        index = session.get(RAGIndex, index_id)
        if not index:
            raise IndexNotFoundError(f"RAG index {index_id} not found")
        
        document = RAGDocument(
            index_id=index_id,
            content=content,
            document_metadata=metadata or {},
            embedding=embedding,
        )
        session.add(document)
        session.commit()
        session.refresh(document)
        
        # Sync to ChromaDB if the index uses ChromaDB
        if index.vector_db_type == "chromadb":
            try:
                chroma_client = self._vector_db_clients.get("chromadb")
                if chroma_client and chroma_client.get("is_available") and "client" in chroma_client:
                    import chromadb
                    
                    collection_name = f"rag_index_{index_id}"
                    try:
                        collection = chroma_client["client"].get_collection(name=collection_name)
                    except Exception:
                        # Collection doesn't exist, create it
                        collection = chroma_client["client"].create_collection(name=collection_name)
                    
                    # Add document to ChromaDB
                    # Use document ID as ChromaDB ID
                    collection.add(
                        ids=[str(document.id)],
                        documents=[content],
                        metadatas=[metadata or {}],
                        embeddings=[embedding] if embedding else None,
                    )
                    logger.info(f"Synced document {document.id} to ChromaDB collection {collection_name}")
            except Exception as e:
                logger.warning(f"Failed to sync document to ChromaDB: {e}. Document saved to database only.")
        
        logger.info(f"Added document to index {index_id} (Document ID: {document.id})")
        
        return document
    
    def get_index(self, session: Session, index_id: uuid.UUID) -> RAGIndex:
        """
        Get RAG index by ID.
        
        Args:
            session: Database session
            index_id: Index ID
            
        Returns:
            RAGIndex instance
        """
        index = session.get(RAGIndex, index_id)
        if not index:
            raise IndexNotFoundError(f"RAG index {index_id} not found")
        return index
    
    def list_indexes(
        self,
        session: Session,
        owner_id: uuid.UUID | None = None,
    ) -> list[RAGIndex]:
        """
        List RAG indexes.
        
        Args:
            session: Database session
            owner_id: Optional owner ID filter
            
        Returns:
            List of RAGIndex instances
        """
        if owner_id:
            statement = select(RAGIndex).where(RAGIndex.owner_id == owner_id)
        else:
            statement = select(RAGIndex)
        
        indexes = session.exec(statement).all()
        return list(indexes)
    
    def initialize_vector_db_client(
        self,
        vector_db_type: str,
        config: dict[str, Any],
    ) -> None:
        """
        Initialize a vector database client.
        
        Args:
            vector_db_type: Vector database type
            config: Client configuration
        """
        # Placeholder - will be implemented per vector DB
        self._vector_db_clients[vector_db_type] = {
            "type": vector_db_type,
            "config": config,
            "is_available": True,
        }
        logger.info(f"Initialized vector DB client: {vector_db_type}")
    
    def evaluate_routing(
        self,
        session: Session,
        index_id: uuid.UUID,
        query_requirements: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Evaluate routing decision without executing query.
        Useful for workflow switch nodes.
        
        Args:
            session: Database session
            index_id: RAG index ID
            query_requirements: Optional query requirements
            
        Returns:
            Routing evaluation result with decision and reasoning
        """
        if not query_requirements:
            query_requirements = {}
        
        # Get index
        index = session.get(RAGIndex, index_id)
        if not index:
            raise IndexNotFoundError(f"RAG index {index_id} not found")
        
        # Get index statistics
        documents = session.exec(
            select(RAGDocument).where(RAGDocument.index_id == index_id)
        ).all()
        total_size = sum(len(doc.content) for doc in documents)
        dataset_size_mb = total_size / (1024 * 1024)
        document_count = len(documents)
        
        # Select vector database
        selected_db = self.select_vector_db(
            session=session,
            index_id=index_id,
            query_requirements=query_requirements,
        )
        
        # Generate routing reason
        routing_reason = self._generate_routing_reason(
            index_id=index_id,
            query_requirements=query_requirements,
            selected_db=selected_db,
            session=session,
        )
        
        return {
            "selected_vector_db": selected_db,
            "routing_reason": routing_reason,
            "index_statistics": {
                "document_count": document_count,
                "dataset_size_mb": round(dataset_size_mb, 2),
                "current_vector_db": index.vector_db_type,
            },
            "query_requirements": query_requirements,
        }
    
    def _generate_routing_reason(
        self,
        index_id: uuid.UUID,
        query_requirements: dict[str, Any],
        selected_db: str,
        session: Session,
    ) -> str:
        """
        Generate human-readable routing reason.
        
        Args:
            index_id: Index ID
            query_requirements: Query requirements
            selected_db: Selected vector database
            session: Database session
            
        Returns:
            Routing reason string
        """
        reasons = []
        
        # Get index statistics
        documents = session.exec(
            select(RAGDocument).where(RAGDocument.index_id == index_id)
        ).all()
        total_size = sum(len(doc.content) for doc in documents)
        dataset_size_mb = total_size / (1024 * 1024)
        
        # Check requirements
        if query_requirements.get("structured_memory"):
            reasons.append("Structured memory required → SupaVec")
        
        if query_requirements.get("requires_metadata"):
            reasons.append("Metadata filtering required → Weaviate")
        
        if dataset_size_mb > 1024:
            reasons.append(f"Large dataset ({dataset_size_mb:.2f}MB > 1GB) → Milvus")
        
        if query_requirements.get("ocr_result_injected"):
            if dataset_size_mb < 1:
                reasons.append("OCR result injected + small dataset → LightRAG")
            else:
                reasons.append("OCR result injected → SupaVec")
        
        if query_requirements.get("user_plan") == "free":
            reasons.append("Free plan → SupaVec")
        
        if dataset_size_mb < 1:
            reasons.append(f"Small dataset ({dataset_size_mb:.2f}MB < 1MB) → LightRAG")
        
        # Default reason
        if not reasons:
            reasons.append(f"Default routing → {selected_db}")
        
        return "; ".join(reasons)


# Default RAG service instance
default_rag_service = RAGService()

