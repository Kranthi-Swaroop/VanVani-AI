"""Initialize database and load sample data."""
import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.database.sql_db import init_database
from app.database.vector_db import VectorDatabase
from app.database.load_data import create_sample_data

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Initialize all databases and load data."""
    try:
        logger.info("Starting database initialization...")
        
        # Initialize SQL database
        logger.info("Initializing SQL database...")
        await init_database()
        logger.info("✓ SQL database initialized")
        
        # Initialize vector database
        logger.info("Initializing vector database...")
        vector_db = VectorDatabase()
        logger.info("✓ Vector database initialized")
        
        # Load sample data
        logger.info("Loading sample knowledge base data...")
        await create_sample_data(vector_db)
        logger.info("✓ Sample data loaded")
        
        # Show stats
        count = vector_db.count_documents()
        logger.info(f"✓ Total documents in knowledge base: {count}")
        
        logger.info("\n" + "="*50)
        logger.info("Database initialization complete!")
        logger.info("="*50)
        logger.info("\nYou can now run the application with:")
        logger.info("  uvicorn app.main:app --reload\n")
        
    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
