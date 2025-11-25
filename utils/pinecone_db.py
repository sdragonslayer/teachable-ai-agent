from pinecone import Pinecone
from config import PINECONE_API_KEY, PINECONE_INDEX_NAME, COURSE_MATERIALS_NAMESPACE, ANALYTICS_NAMESPACE

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)


def store_embedding(vector: list, metadata: dict, namespace: str, vector_id: str = None):

    try:
        if vector_id is None:
            vector_id = f"{namespace}_{metadata.get('source_file', 'unknown')}_{metadata.get('chunk_id', 'unknown')}"
        
        index.upsert(
            vectors=[(vector_id, vector, metadata)],
            namespace=namespace
        )
        return vector_id
    except Exception as e:
        print(f"Error storing embedding: {e}")
        return None


def search_similar(query_vector: list, namespace: str, top_k: int = 5) -> list:

    try:
        results = index.query(
            vector=query_vector,
            top_k=top_k,
            namespace=namespace,
            include_metadata=True
        )
        return results.get('matches', [])
    except Exception as e:
        print(f"Error searching: {e}")
        return []


def get_relevant_context(query_vector: list, top_k: int = 3) -> str:

    try:
        results = search_similar(query_vector, COURSE_MATERIALS_NAMESPACE, top_k)
        
        context_parts = []
        for match in results:
            metadata = match.get('metadata', {})
            content = metadata.get('content', '')
            source = metadata.get('source_file', 'Unknown')
            context_parts.append(f"From {source}:\n{content}")
        
        return "\n\n".join(context_parts) if context_parts else "No relevant course materials found."
    except Exception as e:
        print(f"Error retrieving context: {e}")
        return "Error retrieving course materials."


def store_conversation(user_message: str, ai_response: str, embedding: list, 
                       session_id: str, username: str):

    try:
        metadata = {
            "type": "conversation",
            "session_id": session_id,
            "username": username,
            "user_message": user_message[:500],  # Truncate for metadata
            "ai_response": ai_response[:500],
            "timestamp": str(__import__('datetime').datetime.now().isoformat())
        }
        
        vector_id = f"conv_{session_id}_{username}_{__import__('time').time()}"
        store_embedding(embedding, metadata, ANALYTICS_NAMESPACE, vector_id)
    except Exception as e:
        print(f"Error storing conversation: {e}")