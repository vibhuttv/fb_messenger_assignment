"""
Cassandra client for the Messenger application.
This provides a connection to the Cassandra database.
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from cassandra.cluster import Cluster, Session
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement, dict_factory
from cassandra.policies import DCAwareRoundRobinPolicy

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class CassandraClient:
    """Singleton Cassandra client for the application."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CassandraClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the Cassandra connection."""
        if self._initialized:
            return

        self.host = os.getenv("CASSANDRA_HOST", "localhost")
        self.port = int(os.getenv("CASSANDRA_PORT", "9042"))
        self.keyspace = os.getenv("CASSANDRA_KEYSPACE", "messenger")
        self.local_dc = os.getenv("CASSANDRA_LOCAL_DC", "datacenter1")

        self.cluster = None
        self.session = None

        logger.info("Connecting to Cassandra...")
        self.connect()

        self._initialized = True

    def connect(self) -> None:
        """Connect to the Cassandra cluster."""
        try:
            # Optional: Use auth if credentials are provided
            auth_provider = None
            username = os.getenv("CASSANDRA_USERNAME")
            password = os.getenv("CASSANDRA_PASSWORD")
            if username and password:
                auth_provider = PlainTextAuthProvider(username=username, password=password)

            self.cluster = Cluster(
                [self.host],
                port=self.port,
                auth_provider=auth_provider,
                load_balancing_policy=DCAwareRoundRobinPolicy(local_dc=self.local_dc),
                protocol_version=5  # Avoid protocol downgrade warnings
            )

            # First connect without a keyspace to create it if needed
            system_session = self.cluster.connect()
            system_session.execute(f"""
                CREATE KEYSPACE IF NOT EXISTS {self.keyspace}
                WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': 1 }}
            """)

            self.session = self.cluster.connect(self.keyspace)
            self.session.row_factory = dict_factory

            logger.info(f"Connected to Cassandra at {self.host}:{self.port}, keyspace: {self.keyspace}")

        except Exception as e:
            logger.error(f"Failed to connect to Cassandra: {str(e)}")
            raise

    def close(self) -> None:
        """Close the Cassandra connection."""
        if self.cluster:
            self.cluster.shutdown()
            logger.info("Cassandra connection closed")

    def execute(self, query: str, params: dict = None) -> List[Dict[str, Any]]:
        """
        Execute a CQL query.

        Args:
            query: The CQL query string
            params: The parameters for the query

        Returns:
            List of rows as dictionaries
        """
        if not self.session:
            self.connect()

        try:
            statement = SimpleStatement(query)
            result = self.session.execute(statement, params or {})
            return list(result)
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise

    def execute_async(self, query: str, params: dict = None):
        """
        Execute a CQL query asynchronously.

        Args:
            query: The CQL query string
            params: The parameters for the query

        Returns:
            Async result object
        """
        if not self.session:
            self.connect()

        try:
            statement = SimpleStatement(query)
            return self.session.execute_async(statement, params or {})
        except Exception as e:
            logger.error(f"Async query execution failed: {str(e)}")
            raise

    def get_session(self) -> Session:
        """Get the Cassandra session."""
        if not self.session:
            self.connect()
        return self.session


# Create a global instance
cassandra_client = CassandraClient()
