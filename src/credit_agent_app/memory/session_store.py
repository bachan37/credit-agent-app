import logging
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory

logger = logging.getLogger(__name__)

_in_memory_store: dict[str, InMemoryChatMessageHistory] = {}

# fallback strategy use in_memory_store
def get_in_memory_history(session_id: str) -> BaseChatMessageHistory:
    """Non-persistent session history."""
    if session_id not in _in_memory_store:
        _in_memory_store[session_id] = InMemoryChatMessageHistory()
    return _in_memory_store[session_id]

def get_redis_chat_history(
    session_id: str, 
    redis_url: str = "redis://localhost:6379/0", 
    ttl: int = 86400
) -> BaseChatMessageHistory:
    """Persistent Redis session history with graceful fallback."""
    print("use redis chat history")
    try:
        return RedisChatMessageHistory(session_id=session_id, url=redis_url, ttl=ttl)
    except Exception as exc:
        logger.warning(f"Redis unavailable ({exc}). Using In-Memory fallback.")
        return get_in_memory_history(session_id)

def inspect_redis_history(session_id: str, redis_url: str = "redis://localhost:6379/0"):
    """Fetch and display chat history stored in Redis for a given session."""
    print(f"\n=================== REDIS CHAT HISTORY ({session_id}) ===================")
    try:
        history = RedisChatMessageHistory(session_id=session_id, url=redis_url)
        messages = history.messages
        if not messages:
            print(f"No messages found in Redis for session '{session_id}'.")
        for msg in messages:
            role = msg.__class__.__name__.replace("Message", "")
            print(f"  [{role}]: {msg.content}")
    except Exception as e:
        print(f"Error fetching from Redis: {e}")
    print("==========================================================================")