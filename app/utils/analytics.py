"""Analytics and logging utilities."""
import logging
from datetime import datetime
from typing import Dict
from app.database.sql_db import get_call_stats

logger = logging.getLogger(__name__)

async def log_call(caller_id: str, status: str, query: str = None, response: str = None):
    """Log call details for analytics tracking."""
    log_data = {
        "ts": datetime.utcnow().isoformat(),
        "id": caller_id,
        "status": status,
        "q": query[:50] if query else None,
        "r": response[:50] if response else None
    }
    logger.info(f"Analytics: {log_data}")

async def get_analytics() -> Dict:
    """Consolidate database stats into dashboard format."""
    try:
        stats = await get_call_stats()
        total_calls = stats.get("total_calls", 0)
        total_convs = stats.get("total_conversations", 0)
        
        return {
            "total_calls": total_calls,
            "total_convs": total_convs,
            "languages": stats.get("languages", {}),
            "avg_conv_per_call": round(total_convs / max(total_calls, 1), 2),
            "updated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Analytics Error: {e}")
        return {"error": "Stats unavailable"}
