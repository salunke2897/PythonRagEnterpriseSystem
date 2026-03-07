class RAGException(Exception):
    """Base exception for RAG domain errors."""


class ValidationException(RAGException):
    """Raised when request or file validation fails."""


class IngestionException(RAGException):
    """Raised when document ingestion fails."""


class RetrievalException(RAGException):
    """Raised when retrieval pipeline fails."""


class LLMException(RAGException):
    """Raised when LLM interaction fails."""
