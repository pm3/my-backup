


import argparse
import os

import backup


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Backup files to Azure Storage with encryption')
    parser.add_argument('root', help='Root directory to backup')
    parser.add_argument('--account', required=True, help='Azure Storage account name')
    parser.add_argument('--accesskey', required=True, help='Azure Storage account key')
    parser.add_argument('--password', required=True, help='Encryption password')
    args = parser.parse_args()

    #list directories in root directory
    directories = [d for d in os.listdir(args.root) if os.path.isdir(os.path.join(args.root, d))]

    for directory in directories:
        print(f"Backing up {directory}")
        backup(os.path.join(args.root, directory), args.account, args.accesskey, args.password, directory)
