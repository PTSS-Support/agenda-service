from azure.data.tables import TableServiceClient
from azure.data.tables.aio import TableClient
from src.settings import settings
from src.exceptions.exception_handler import logger


class AgendaRepository:
    def __init__(self):
        self.table_name = settings.AZURE_STORAGE_TABLE_NAME
        self.table_service_client = TableServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )
        self.table_client = TableClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING,
            self.table_name
        )
        self.ensure_table_exists(self)

    async def ensure_table_exists(self):
        try:
            self.table_service_client.create_table_if_not_exists(self.table_name)
            logger.info(f"Table {self.table_name} ensured.")
        except Exception as e:
            logger.error(f"Error checking or creating table: {e}")
            raise

    async def query_entities(self, filter_query: str):
        return self.table_client.query_entities(filter_query)

    async def create_entity(self, entity: dict):
        return await self.table_client.create_entity(entity=entity)

    async def update_entity(self, entity: dict):
        try:
            await self.table_client.update_entity(mode='replace', entity=entity)
        except Exception as e:
            logger.error(f"Error updating entity: {e}")
            raise

    async def delete_entity(self, partition_key: str, row_key: str):
        try:
            logger.info(f"Attempting to delete entity with PartitionKey={partition_key}, RowKey={row_key}")
            await self.table_client.delete_entity(
                partition_key=str(partition_key),
                row_key=str(row_key)
            )
            logger.info(f"Successfully deleted entity with PartitionKey={partition_key}, RowKey={row_key}")
        except Exception as e:
            logger.error(f"Error deleting entity with PartitionKey={partition_key}, RowKey={row_key}: {e}")
            raise
