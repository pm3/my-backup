#!/usr/bin/env python3
import argparse
import datetime
import os
from typing import Dict
from azure_storage import AzureStorageManager
from encryption import calculate_file_hash
import sys

def backup(directory: str, account: str, accesskey: str, password: str, partition: str):
    
    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory")
        sys.exit(1)
    
    # Initialize storage manager
    storage_manager = AzureStorageManager(account, accesskey, partition)
    # Load encryption key
    aes_key = storage_manager.load_or_create_key("main", password)
    files = storage_manager.list_files("")
    file_map = {file["RowKey"]: file for file in files}
    
    # Process all files in directory
    for root, _, files in os.walk(directory):
        for filename in files:
            try:
                filepath = os.path.join(root, filename)
                filekey = os.path.relpath(filepath, directory)
                file_metadata = file_map.get(filekey.replace("/", "|"))
                process_file(filekey, filepath, file_metadata, aes_key, storage_manager)
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

def process_file(filekey: str, filepath: str, metadata: Dict | None, aes_key: bytes, storage_manager: AzureStorageManager):
    """Process a single file for backup."""
    print(f"Processing {filekey} {filepath}")
    current_hash = calculate_file_hash(filepath)
    modified_date = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
    file_size = os.path.getsize(filepath)
        
    if metadata is None or metadata["Hash"] != current_hash:
        # New file
        if storage_manager.check_if_blob_exists(current_hash):
            print(f"Skipping existing blob: {current_hash}")
        else:
            storage_manager.upload_blob(current_hash, filepath, aes_key)
        storage_manager.update_file_metadata(filekey, {"Hash": current_hash, "ModifiedDate": modified_date, "Size": file_size})
    else:
        # File unchanged
        print(f"Skipping unchanged file: {filekey}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Backup files to Azure Storage with encryption')
    parser.add_argument('directory', help='Directory to backup')
    parser.add_argument('--account', required=True, help='Azure Storage account name')
    parser.add_argument('--accesskey', required=True, help='Azure Storage account key')
    parser.add_argument('--password', required=True, help='Encryption password')
    parser.add_argument('--partition', required=True, help='Partition key')
    args = parser.parse_args()
    backup(args.directory, args.account, args.accesskey, args.password, args.partition)
