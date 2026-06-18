import pytest

from utils.config_loader import load_yaml
from utils.data_recovery import DataRecovery
from utils.db_client import DatabaseClient
from utils.http_client import HttpClient
from utils.logger import get_logger
from utils.mock_login_api import MockLoginApiClient
from utils.mysql_client import MySqlClient


# conftest.py is pytest's shared fixture entrypoint. Fixtures defined here can be
# used by any test file under tests/ without importing them explicitly.


# ----------------------------
# Configuration and test data
# ----------------------------


@pytest.fixture(scope="session")
def env_config() -> dict:
    """Load API environment configuration once per test session."""
    return load_yaml("config/develop.yaml")


@pytest.fixture(scope="session")
def test_data() -> dict:
    """Load common user test data once per test session."""
    return load_yaml("data/users.yaml")


@pytest.fixture(scope="session")
def login_data() -> dict:
    """Load login demo users and scenario data once per test session."""
    return load_yaml("data/login_cases.yaml")


@pytest.fixture(scope="session")
def db_config() -> dict:
    """Load SQLite database configuration once per test session."""
    return load_yaml("config/database.yaml")


@pytest.fixture(scope="session")
def mysql_config() -> dict:
    """Load MySQL database configuration once per test session."""
    return load_yaml("config/mysql.yaml")


# ----------------------------
# Shared tools
# ----------------------------


@pytest.fixture(scope="session")
def logger():
    """Provide one shared logger for all tests."""
    return get_logger()


@pytest.fixture(scope="session")
def api_client(env_config: dict) -> HttpClient:
    """Provide a shared HTTP client for real API calls and close it after tests."""
    client = HttpClient(
        base_url=env_config.get("base_url") or env_config["develop_url"],
        timeout=env_config.get("timeout", 10),
    )
    yield client
    client.close()


@pytest.fixture(scope="session")
def login_client(login_data: dict) -> MockLoginApiClient:
    """Provide the local mock login client used by the login demo tests."""
    return MockLoginApiClient(users=login_data["users"])


# ----------------------------
# Database clients
# ----------------------------


@pytest.fixture(scope="session")
def db_client(db_config: dict) -> DatabaseClient:
    """Provide a shared SQLite client and close the connection after tests."""
    client = DatabaseClient(db_config)
    client.connect()
    yield client
    client.close()


@pytest.fixture(scope="session")
def mysql_client(mysql_config: dict) -> MySqlClient:
    """Provide a shared MySQL client and close the connection after tests."""
    client = MySqlClient(mysql_config)
    client.connect()
    yield client
    client.close()


# ----------------------------
# Per-test cleanup
# ----------------------------


@pytest.fixture
def data_recovery(api_client: HttpClient, logger) -> DataRecovery:
    """Collect API cleanup actions during one test and run them after that test."""
    recovery = DataRecovery(api_client=api_client, logger=logger)
    yield recovery
    recovery.run()


@pytest.fixture
def db_data_recovery(db_client: DatabaseClient, logger) -> DataRecovery:
    """Collect SQLite cleanup actions during one test and run them after that test."""
    recovery = DataRecovery(db_client=db_client, logger=logger)
    yield recovery
    recovery.run()


@pytest.fixture
def mysql_data_recovery(mysql_client: MySqlClient, logger) -> DataRecovery:
    """Collect MySQL cleanup actions during one test and run them after that test."""
    recovery = DataRecovery(db_client=mysql_client, logger=logger)
    yield recovery
    recovery.run()
