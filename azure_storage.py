import os
from azure.storage.blob import BlobServiceClient
from azure.data.tables import TableServiceClient
from typing import Dict, List, Optional

from encryption import decrypt_key, decrypt_stream_to_file, encrypt_key, encrypt_stream_from_file

class AzureStorageManager:
    def __init__(self, account_name: str, accesskey: str, partition_key: str):
        self.account_name = account_name
        self.partition_key = partition_key
        connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={accesskey};EndpointSuffix=core.windows.net"
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.table_service_client = TableServiceClient.from_connection_string(connection_string)
        
        # Ensure containers and tables exist
        self.container_client = self.blob_service_client.get_container_client("files")
        
        self.table_client = self.table_service_client.get_table_client("filemetadata2")
        
        # Create encryption key table if it doesn't exist
        self.key_table_client = self.table_service_client.get_table_client("encryptionkeys")

    # ===== Encryption keys =====
    def load_encryption_key(self, key_name: str) -> Optional[Dict]:
        """Load the encryption key from the table."""
        try:
            entity = self.key_table_client.get_entity(partition_key="keys", row_key=key_name)
            return entity
        except:
            return None

    def store_encryption_key(self, key_name: str, key_row: Dict):
        """Store the encryption key information."""
        entity = {
            "PartitionKey": "keys",
            "RowKey": key_name,
            **key_row
        }
        self.key_table_client.upsert_entity(entity)

    def load_or_create_key(self, key_name: str, password: str) -> bytes:
        """Load the encryption key from the table. If it doesn't exist, create a new one and store it."""
        key_row = self.load_encryption_key(key_name)
        if key_row is None:
            aes_key = os.urandom(32)  # 256-bit key
            key_row = encrypt_key(aes_key, password)
            self.store_encryption_key(key_name, key_row)
        return decrypt_key(key_row, password)

    # ===== File metadata =====
    def get_file_metadata(self, filename: str) -> Optional[Dict]:
        """Get file metadata from the table."""
        try:
            return self.table_client.get_entity(partition_key=self.partition_key, row_key=filename.replace("/", "|"))
        except:
            return None

    def list_files(self, prefix: str) -> List[Dict]:
        """List files in table files metadata with the given prefix."""
        if prefix is None or len(prefix) == 0:
            file_list = self.table_client.query_entities(query_filter=f"PartitionKey eq '{self.partition_key}'", results_per_page=1000)
        else:
            prefix = prefix.replace("/", "|")
            start = prefix
            end = prefix[:-1] + chr(ord(prefix[-1]) + 1)  # e.g. 'abc' → 'abd'
            file_list = self.table_client.query_entities(query_filter=f"PartitionKey eq '{self.partition_key}' and RowKey ge '{start}' and RowKey lt '{end}'")
        return file_list

    def update_file_metadata(self, filename: str, metadata: Dict):
        """Update file metadata in the table."""
        entity = {
            "PartitionKey": self.partition_key,
            "RowKey": filename.replace("/", "|"),
            **metadata
        }
        self.table_client.upsert_entity(entity)
    
    # ===== Blob operations =====
    def check_if_blob_exists(self, file_hash: str) -> bool:
        """Check if a blob exists in Azure Storage."""
        blob_client = self.container_client.get_blob_client(file_hash)
        return blob_client.exists()

    def upload_blob(self, file_hash: str, filepath: str, aes_key: bytes):
        print(f"New file: {filepath}")
        encrypted_stream = encrypt_stream_from_file(filepath, aes_key)
        self.container_client.upload_blob(file_hash, encrypted_stream)

    def download_blob(self, file_hash: str, filepath: str, aes_key: bytes):
        """Download a blob from Azure Storage."""
        blob_client = self.container_client.get_blob_client(file_hash)
        decrypt_stream_to_file(blob_client.download_blob(), filepath, aes_key)
