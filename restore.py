#!/usr/bin/env python3
import argparse
import os
from azure_storage import AzureStorageManager

def restore(account: str, accesskey: str, password: str, partition: str, directory: str, prefix: str):
    # Create target directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    # Initialize storage manager
    storage_manager = AzureStorageManager(account, accesskey, partition)
    
    # Load encryption key
    aes_key = storage_manager.load_or_create_key("main", password)

    #load all files with the prefix        
    files = storage_manager.list_files(prefix)
    for file in files:
        file_key = file['RowKey'].replace("|", "/")
        file_path = os.path.join(directory, file_key)
        #create the directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        #download the file
        if os.path.exists(file_path) and file['Size'] == os.path.getsize(file_path):
            print(f"Skipping existing file: {file_key}")
        else:
            print(f"Restoring {file_key}")
            storage_manager.download_blob(file['Hash'], file_path, aes_key)
        # try:
        # except Exception as e:
        #     print(f"Error restoring {file['RowKey']}: {str(e)}")
    
    print(f"Restore completed successfully to {directory}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Restore data from Azure backup')
    parser.add_argument('directory', help='Target directory for restored data')
    parser.add_argument('--prefix', default="", help='Prefix of the files to restore')
    parser.add_argument('--account', required=True, help='Azure Storage account name')
    parser.add_argument('--accesskey', required=True, help='Azure Storage access key')
    parser.add_argument('--password', required=True, help='Encryption password')
    parser.add_argument('--partition', required=True, help='Partition to restore from')
    args = parser.parse_args()
    restore(args.account, args.accesskey, args.password, args.partition, args.directory, args.prefix)
