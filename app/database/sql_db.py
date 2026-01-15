"""SQL database for tracking conversations and analytics."""
import logging
from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
Base = declarative_base()

class Call(Base):
    __tablename__ = "calls"
    id = Column(Integer, primary_key=True)
    call_sid = Column(String(100), unique=True, index=True)
    caller_id = Column(String(20), index=True)
    call_status = Column(String(20))
    language = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True)

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    call_sid = Column(String(100), index=True)
    caller_id = Column(String(20), index=True)
    user_query = Column(Text)
    ai_response = Column(Text)
    language = Column(String(20))
    intent = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

_engine = None
_session_maker = None

async def init_database():
    """Initialize SQLite database with aiosqlite."""
    global _engine, _session_maker
    try:
        url = settings.database_url
        if url.startswith("sqlite:///") and "aiosqlite" not in url:
            url = url.replace("sqlite:///", "sqlite+aiosqlite:///")
        
        _engine = create_async_engine(url)
        _session_maker = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
        
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        logger.error(f"DB Init Error: {e}")
        raise

def get_session() -> AsyncSession:
    if not _session_maker:
        raise RuntimeError("DB not initialized")
    return _session_maker()

async def save_conversation(caller_id, call_sid, user_query, ai_response, language, intent=None):
    try:
        async with get_session() as session:
            conv = Conversation(
                call_sid=call_sid, caller_id=caller_id,
                user_query=user_query, ai_response=ai_response,
                language=language, intent=intent
            )
            session.add(conv)
            await session.commit()
    except Exception as e:
        logger.error(f"Error saving conversation: {e}")

async def get_call_stats() -> Dict:
    try:
        async with get_session() as session:
            total_calls = await session.scalar(select(func.count()).select_from(Call))
            total_convs = await session.scalar(select(func.count()).select_from(Conversation))
            
            lang_stmt = select(Conversation.language, func.count(Conversation.id)).group_by(Conversation.language)
            lang_result = await session.execute(lang_stmt)
            
            return {
                "total_calls": total_calls or 0,
                "total_conversations": total_convs or 0,
                "languages": {row[0]: row[1] for row in lang_result}
            }
    except Exception as e:
        logger.error(f"Stats Error: {e}")
        return {"total_calls": 0, "total_conversations": 0, "languages": {}}
