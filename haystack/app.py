from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from haystack_integrations.document_stores.weaviate import WeaviateDocumentStore
from haystack_integrations.components.retrievers.weaviate import WeaviateEmbeddingRetriever
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack import Pipeline

app = FastAPI(title="CareerCoachGPT Haystack API")

# Weaviate DocumentStore
print("🔗 Connecting to Weaviate...")
document_store = WeaviateDocumentStore(url="http://weaviate:8080")
print(f"✅ Connected! Documents in store: {document_store.count_documents()}")

# Text Embedder für Queries
text_embedder = SentenceTransformersTextEmbedder(
    model="sentence-transformers/all-MiniLM-L6-v2"
)
text_embedder.warm_up()

# Weaviate Retriever
retriever = WeaviateEmbeddingRetriever(document_store=document_store)

# Pipeline zusammenbauen
pipeline = Pipeline()
pipeline.add_component("text_embedder", text_embedder)
pipeline.add_component("retriever", retriever)
pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

print("✅ Pipeline initialized")


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    filters: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    query: str
    total_results: int
    documents: List[Dict[str, Any]]


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Semantic search in Weaviate via Haystack Pipeline
    
    Example:
    {
        "query": "I am interested in digital marketing and data analysis",
        "top_k": 5
    }
    """
    try:
        # Run the pipeline
        result = pipeline.run({
            "text_embedder": {"text": request.query},
            "retriever": {
                "top_k": request.top_k,
                "filters": request.filters
            }
        })
        
        documents = result.get("retriever", {}).get("documents", [])
        
        # Format results
        formatted_docs = []
        for doc in documents:
            formatted_docs.append({
                "content": doc.content,
                "metadata": doc.meta,
                "score": getattr(doc, 'score', None),
                "id": doc.id
            })
        
        return SearchResponse(
            query=request.query,
            total_results=len(formatted_docs),
            documents=formatted_docs
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        count = document_store.count_documents()
        return {
            "status": "healthy",
            "total_documents": count,
            "document_store": "Weaviate",
            "embedder_model": "sentence-transformers/all-MiniLM-L6-v2"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/stats")
async def stats():
    """Get statistics about stored documents"""
    try:
        # Simple count by document type
        all_docs = document_store.filter_documents()
        
        stats = {
            "total": len(all_docs),
            "by_type": {}
        }
        
        for doc in all_docs:
            doc_type = doc.meta.get("type", "unknown")
            stats["by_type"][doc_type] = stats["by_type"].get(doc_type, 0) + 1
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats failed: {str(e)}")


@app.get("/")
async def root():
    """API information"""
    return {
        "name": "CareerCoachGPT Haystack API",
        "version": "1.0",
        "endpoints": {
            "/search": "POST - Semantic search",
            "/health": "GET - Health check",
            "/stats": "GET - Document statistics",
            "/docs": "GET - API documentation"
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting Haystack API on http://0.0.0.0:8002")
    uvicorn.run(app, host="0.0.0.0", port=8002)