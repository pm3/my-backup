#!/usr/bin/env python3
import argparse
from azure_storage import AzureStorageManager
from encryption import decrypt_key, encrypt_key

def change_password(account: str, accesskey: str, old_password: str, new_password: str):

    # Initialize storage manager
    storage_manager = AzureStorageManager(account, accesskey, None)
    
    key_row = storage_manager.load_encryption_key("main")
    if key_row is None:
        print("Key not found")
        return 1
    try:
        aes_key = decrypt_key(key_row, old_password)
    except:
        print("Invalid old password")
        return 1
    storage_manager.store_encryption_key("main", encrypt_key(aes_key, new_password))
    print("Password changed successfully")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Change encryption password for Azure backup')
    parser.add_argument('--account', required=True, help='Azure Storage account name')
    parser.add_argument('--accesskey', required=True, help='Azure Storage access key')
    parser.add_argument('--old-password', required=True, help='Current encryption password')
    parser.add_argument('--new-password', required=True, help='New encryption password')
    args = parser.parse_args()
    change_password(args.account, args.accesskey, args.old_password, args.new_password)
