"""Data loading utilities for populating the vector database."""
import uuid
import logging
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)

async def load_all_documents(vector_db):
    """Load documents from data/raw_pdfs into the vector DB."""
    try:
        data_dir = Path("data/raw_pdfs")
        if not data_dir.exists() or not list(data_dir.glob("*.pdf")):
            logger.warning("No PDFs found, seeding with sample data.")
            await create_sample_data(vector_db)
            return
        
        for pdf_file in data_dir.glob("*.pdf"):
            await load_pdf_document(pdf_file, vector_db)
    except Exception as e:
        logger.error(f"Load failed: {e}")

async def load_pdf_document(pdf_path: Path, vector_db):
    try:
        import fitz
        doc = fitz.open(pdf_path)
        text = "".join([page.get_text() for page in doc])
        doc.close()
        
        chunks = chunk_text(text)
        category = determine_category(pdf_path.name)
        
        docs, metas, ids = [], [], []
        for i, chunk in enumerate(chunks):
            docs.append(chunk)
            metas.append({"source": pdf_path.name, "category": category})
            ids.append(f"{pdf_path.stem}_{i}_{uuid.uuid4().hex[:6]}")
            
        await vector_db.add_documents(docs, metas, ids)
    except Exception as e:
        logger.error(f"PDF error {pdf_path}: {e}")

def chunk_text(text, size=1000, overlap=200):
    chunks, start = [], 0
    while start < len(text):
        end = start + size
        if end < len(text):
            idx = max(text[start:end].rfind('.'), text[start:end].rfind('।'))
            if idx > size * 0.7: end = start + idx + 1
        chunks.append(text[start:end].strip())
        start = end - overlap
    return chunks

def determine_category(name):
    name = name.lower()
    if any(k in name for k in ['scheme', 'yojana', 'kusum']): return 'scheme'
    if any(k in name for k in ['health', 'medical']): return 'health'
    if any(k in name for k in ['agriculture', 'krishi']): return 'agriculture'
    if any(k in name for k in ['market', 'price']): return 'market'
    if any(k in name for k in ['civic', 'document']): return 'civic'
    return 'general'

async def create_sample_data(vector_db):
    """Seed DB with initial knowledge base context."""
    samples = [
        {
            "content": "PM-KUSUM Yojana: Subsidy for solar pumps. 60% subsidy, 10% farmer share. Apply at KVK.",
            "metadata": {"source": "sample_scheme.pdf", "category": "scheme"}
        },
        {
            "content": "Health Guide: Rural emergency call 108. Follow basic hygiene for common cold.",
            "metadata": {"source": "sample_health.pdf", "category": "health"}
        },
        {
            "content": "Agriculture: Rice varieties for CG include Swarna and Mahamaya. Sowing in June-July.",
            "metadata": {"source": "sample_agri.pdf", "category": "agriculture"}
        }
    ]
    docs = [s["content"] for s in samples]
    metas = [s["metadata"] for s in samples]
    ids = [f"sample_{i}_{uuid.uuid4().hex[:6]}" for i in range(len(samples))]
    await vector_db.add_documents(docs, metas, ids)
