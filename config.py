import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_USERNAME = os.getenv("DB_USERNAME", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_DATABASE", "invoiceDB")

DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_database_exists():
    """Create database if it doesn't exist"""
    # Connect to default postgres database to create our database
    temp_url = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
    temp_engine = create_engine(temp_url, isolation_level="AUTOCOMMIT")
    
    try:
        with temp_engine.connect() as conn:
            # Check if database exists
            result = conn.execute(
                text("SELECT datname FROM pg_database WHERE datname = :dbname"),
                {"dbname": DB_NAME}
            )
            exists = result.fetchone() is not None
            
            if not exists:
                print(f"Database '{DB_NAME}' not found. Creating...")
                conn.execute(text(f'CREATE DATABASE "{DB_NAME}"'))
                print(f"Database '{DB_NAME}' created successfully")
            else:
                print(f"Database '{DB_NAME}' already exists")
    except Exception as e:
        print(f"Error checking/creating database: {e}")
        raise
    finally:
        temp_engine.dispose()


def ensure_tables_exist():
    """Check if tables exist and run migrations if needed"""
    from sqlalchemy import inspect
    from models.database import Base
    import subprocess
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    required_tables = ["invoices", "invoice_lines"]
    tables_exist = all(table in tables for table in required_tables)
    
    if not tables_exist:
        print("Required tables not found. Running migrations...")
        try:
            # Run alembic migrations
            subprocess.run(["alembic", "upgrade", "head"], check=True)
            print("Migrations completed successfully")
        except subprocess.CalledProcessError as e:
            print(f"Migration failed: {e}")
            # Fallback to create_all if migrations fail
            print("Falling back to Base.metadata.create_all()")
            Base.metadata.create_all(bind=engine)
    else:
        print("All required tables exist in invoiceDB")


def initialize_database():
    """Initialize database: create DB, and ensure tables exist"""
    try:
        # Step 1: Ensure database exists
        ensure_database_exists()
        
        # Step 2: Ensure tables exist
        ensure_tables_exist()
        
        print("Database initialization completed successfully")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise

