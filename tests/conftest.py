import pytest
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base


@pytest.fixture(scope="session")
def temp_db_path():
    """Create a temporary database file."""
    fd, path = tempfile.mkstemp()
    yield path
    os.close(fd)
    os.unlink(path)


@pytest.fixture(scope="session")
def test_db_url(temp_db_path):
    """Create a database URL for testing."""
    return f"sqlite:///{temp_db_path}"


@pytest.fixture(scope="session")
def test_engine(test_db_url):
    """Create a SQLAlchemy engine for testing."""
    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db_session(test_engine):
    """Create a SQLAlchemy session for testing."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def test_environment():
    """Set up test environment variables."""
    original_env = os.environ.copy()
    os.environ["API_URL"] = "http://test-api:8000"
    os.environ["DATABASE_URL"] = "sqlite:///./test_ota_jobs.db"
    yield
    os.environ.clear()
    os.environ.update(original_env)
