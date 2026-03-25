from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

engine_test = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture()
def client():
    from app.infra.database.session import Base, get_db
    from app.main import app

    Base.metadata.create_all(bind=engine_test)

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    mock_scheduler = MagicMock()
    mock_scheduler.get_jobs.return_value = [MagicMock(trigger="interval[6:00:00]")]

    with (
        patch("app.main.create_tables"),
        patch("app.main.create_scheduler", return_value=mock_scheduler),
    ):
        with TestClient(app) as test_client:
            yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine_test)
