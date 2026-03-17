"""
azure_config.py — Central configuration for all Azure services.
Provides client instances and helper functions for Blob Storage,
Azure OpenAI, and Azure Communication Services.
Data Lake has been removed — all storage uses Azure Blob Storage.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ─────────────────────────────────────────────
# Azure Blob Storage
# ─────────────────────────────────────────────
def get_blob_service_client():
    """Return a BlobServiceClient using the storage connection string."""
    try:
        from azure.storage.blob import BlobServiceClient
        conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
        if not conn_str:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING is not set in .env")
        return BlobServiceClient.from_connection_string(conn_str)
    except ImportError:
        raise RuntimeError("azure-storage-blob package not installed. Run: pip install azure-storage-blob")
    except Exception as e:
        raise RuntimeError(f"Failed to create BlobServiceClient: {e}")


def upload_to_blob(container_name: str, blob_name: str, data: bytes | str) -> bool:
    """
    Upload data (bytes or string) to Azure Blob Storage.
    Returns True on success, False on failure.
    """
    try:
        client = get_blob_service_client()
        # Ensure container exists
        container_client = client.get_container_client(container_name)
        try:
            container_client.create_container()
        except Exception:
            pass  # Container already exists
        blob_client = client.get_blob_client(container=container_name, blob=blob_name)
        if isinstance(data, str):
            data = data.encode("utf-8")
        blob_client.upload_blob(data, overwrite=True)
        return True
    except Exception as e:
        print(f"[upload_to_blob] Error uploading to {container_name}/{blob_name}: {e}")
        return False


def download_from_blob(container_name: str, blob_name: str) -> bytes | None:
    """
    Download data from Azure Blob Storage.
    Returns bytes on success, None on failure.
    """
    try:
        client = get_blob_service_client()
        blob_client = client.get_blob_client(container=container_name, blob=blob_name)
        downloader = blob_client.download_blob()
        return downloader.readall()
    except Exception as e:
        print(f"[download_from_blob] Error downloading from {container_name}/{blob_name}: {e}")
        return None


def list_blobs(container_name: str, prefix: str = "") -> list[str]:
    """
    List all blob names in a container with optional prefix.
    Returns a list of blob names, empty list on failure.
    """
    try:
        client = get_blob_service_client()
        container_client = client.get_container_client(container_name)
        blobs = []
        for blob in container_client.list_blobs(name_starts_with=prefix):
            blobs.append(blob.name)
        return blobs
    except Exception as e:
        print(f"[list_blobs] Error listing blobs in {container_name} with prefix '{prefix}': {e}")
        return []


# Data Lake Gen2 removed — all storage uses Blob Storage via blob_helper.py


# ─────────────────────────────────────────────
# Azure OpenAI
# ─────────────────────────────────────────────
def get_openai_client():
    """Return an AzureOpenAI client configured from environment variables."""
    try:
        from openai import AzureOpenAI
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        key = os.getenv("AZURE_OPENAI_KEY", "")
        if not endpoint or not key:
            raise ValueError("AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY must be set in .env")
        return AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=key,
            api_version="2024-02-15-preview",
        )
    except ImportError:
        raise RuntimeError("openai package not installed. Run: pip install openai")
    except Exception as e:
        raise RuntimeError(f"Failed to create AzureOpenAI client: {e}")


def get_deployment_name() -> str:
    """Return the Azure OpenAI deployment name from environment."""
    return os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")


# ─────────────────────────────────────────────
# Azure Communication Services — Email
# ─────────────────────────────────────────────
def get_email_client():
    """Return an EmailClient configured from environment variables."""
    try:
        from azure.communication.email import EmailClient
        conn_str = os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING", "")
        if not conn_str:
            raise ValueError("AZURE_COMMUNICATION_CONNECTION_STRING is not set in .env")
        return EmailClient.from_connection_string(conn_str)
    except ImportError:
        raise RuntimeError("azure-communication-email package not installed. Run: pip install azure-communication-email")
    except Exception as e:
        raise RuntimeError(f"Failed to create EmailClient: {e}")


def get_sender_email() -> str:
    """Return configured sender email address."""
    return os.getenv("SENDER_EMAIL", "donotreply@yourdomain.azurecomm.net")
