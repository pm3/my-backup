# Secure Azure Backup System

A secure and efficient backup solution that stores files in Azure Blob Storage with encryption and deduplication.

## Features

- **Secure Encryption**: Files are encrypted using AES-256 encryption before being stored
- **Key Management**: Encryption keys are stored in Azure but are password-protected
- **Deduplication**: Identical files are stored only once, saving storage space
- **Archive Tier**: Files are automatically moved to archive tier for long-term storage
- **Incremental Backup**: Only changed files are uploaded, saving bandwidth and time

## Security

The system implements multiple layers of security:
- All files are encrypted using AES-256 encryption
- Encryption keys are stored in Azure but are password-protected
- Even if someone gains access to Azure storage, they cannot access the files without the password
- Each backup operation requires authentication

## How It Works

1. Files are scanned and hashed to identify unique content
2. Each file is encrypted using AES-256 encryption
3. Encrypted content is stored in Azure Blob Storage
4. File metadata (including hashes and modification dates) is stored separately
5. During backup, only changed files are uploaded
6. Identical files are stored only once (deduplication)
7. Files are automatically moved to archive tier for cost-effective long-term storage

## Usage

### Backup

```bash
python backup.py --account <azure_account> --accesskey <azure_key> --password <encryption_password> --partition <partition_key> <directory>
```

Example:
```bash
python backup.py --account mystorage --accesskey abc123 --password mysecret --partition user1 /home/user/documents
```

### Restore

```bash
python restore.py --account <azure_account> --accesskey <azure_key> --password <encryption_password> --partition <partition_key> <destination_directory>
```

Example:
```bash
python restore.py --account mystorage --accesskey abc123 --password mysecret --partition user1 /home/user/restored
```

### Change Password

```bash
python change_password.py --account <azure_account> --accesskey <azure_key> --old-password <current_password> --new-password <new_password> --partition <partition_key>
```

Example:
```bash
python change_password.py --account mystorage --accesskey abc123 --old-password oldsecret --new-password newsecret --partition user1
```

## Storage Architecture

- **Blob Storage**: Used for storing encrypted file content
- **Table Storage**: Used for storing file metadata and encryption keys
- **Archive Tier**: Files are automatically moved to archive tier for long-term storage
- **Deduplication**: Identical files are stored only once, referenced by their hash

## Requirements

- Python 3.6 or higher
- Azure Storage Account
- Azure Storage Access Key
- Required Python packages (install via pip):
  - azure-storage-blob
  - azure-storage-table
  - cryptography

## Installation

1. Clone the repository
2. Install required packages:
```bash
pip install -r requirements.txt
```
3. Configure your Azure Storage account credentials

## Notes

- The system is designed for long-term archival storage
- Files in archive tier have higher retrieval latency but lower storage costs
- Always keep your encryption password safe - if lost, data cannot be recovered
- Regular backups are recommended to ensure data safety 