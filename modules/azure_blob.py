from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta, timezone
from modules.utils import get_env_variable
import os
import requests


def upload_blob_with_sdk(file_path):
    """Uploads a file to Azure Blob Storage using the Azure SDK."""
    account_name = get_env_variable("AZURE_STORAGE_ACCOUNT_NAME")
    account_key = get_env_variable("AZURE_STORAGE_ACCOUNT_KEY")
    container_name = get_env_variable("AZURE_STORAGE_BLOB_CONTAINER_NAME")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    blob_service_client = BlobServiceClient(
        account_url=f"https://{account_name}.blob.core.windows.net",
        credential=account_key
    )

    container_client = blob_service_client.get_container_client(container_name)
    if not container_client.exists():
        container_client.create_container(public_access="blob")  # Make the container public

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=os.path.basename(file_path))

    with open(file_path, "rb") as file_data:
        blob_client.upload_blob(file_data, overwrite=True)
    print(f"File uploaded successfully to container '{container_name}'.")


def upload_blob_with_http(file_path):
    """Uploads a file to Azure Blob Storage using HTTP requests."""
    account_name = get_env_variable("AZURE_STORAGE_ACCOUNT_NAME")
    account_key = get_env_variable("AZURE_STORAGE_ACCOUNT_KEY")
    container_name = get_env_variable("AZURE_STORAGE_BLOB_CONTAINER_NAME")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Create or ensure the container is public
    container_url = f"https://{account_name}.blob.core.windows.net/{container_name}?restype=container"
    headers = {
        "x-ms-version": "2020-08-04",
        "x-ms-date": datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT"),  # UTC
        "x-ms-blob-public-access": "blob",
    }
    headers["Authorization"] = _generate_authorization_header(account_name, account_key, container_url, "PUT", headers)
    response = requests.put(container_url, headers=headers)
    if response.status_code not in [201, 409]:
        response.raise_for_status()

    # Upload the file
    blob_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{os.path.basename(file_path)}"
    file_size = os.path.getsize(file_path)
    headers = {
        "x-ms-version": "2020-08-04",
        "x-ms-date": datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT"),  # UTC
        "x-ms-blob-type": "BlockBlob",
        "Content-Length": str(file_size),
    }
    headers["Authorization"] = _generate_authorization_header(account_name, account_key, blob_url, "PUT", headers)

    with open(file_path, "rb") as file_data:
        response = requests.put(blob_url, headers=headers, data=file_data)
        response.raise_for_status()

    print(f"File '{os.path.basename(file_path)}' uploaded successfully to container '{container_name}'.")


def generate_blob_url(blob_name):
    """
    Generates a SAS URL for a blob using BlobServiceClient.
    """
    account_name = get_env_variable("AZURE_STORAGE_ACCOUNT_NAME")
    account_key = get_env_variable("AZURE_STORAGE_ACCOUNT_KEY")
    container_name = get_env_variable("AZURE_STORAGE_BLOB_CONTAINER_NAME")

    filename = os.path.basename(blob_name)

    # Configure start and expiry times
    start_time = datetime.now(timezone.utc) - timedelta(hours=10)  # Start slightly earlier to avoid discrepancies
    expiry_time = datetime.now(timezone.utc) + timedelta(hours=10)  # Expiry (e.g., 10 hours)

    # Generate the SAS token
    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=filename,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),  # Read-only
        start=start_time,
        expiry=expiry_time,
        resource="b"  # Specify that it's a blob
    )

    blob_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{filename}?{sas_token}"
    print(f"Long-Term SAS URL: {blob_url}")
    return blob_url


def _generate_authorization_header(account_name, account_key, url, method, headers=None):
    """
    Generates the Authorization header manually for HTTP requests to Azure Blob Storage.
    """
    import hmac
    import hashlib
    import base64
    from urllib.parse import urlparse, parse_qs

    if headers is None:
        headers = {}

    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)

    # Build the string-to-sign
    string_to_sign = f"{method}\n"
    string_to_sign += "\n"  # Content-Encoding
    string_to_sign += "\n"  # Content-Language
    string_to_sign += f"{headers.get('Content-Length', '')}\n"
    string_to_sign += "\n"  # Content-MD5
    string_to_sign += f"{headers.get('Content-Type', '')}\n"
    string_to_sign += "\n"
    string_to_sign += "\n"  # If-Modified-Since
    string_to_sign += "\n"  # If-Match
    string_to_sign += "\n"  # If-None-Match
    string_to_sign += "\n"  # If-Unmodified-Since
    string_to_sign += "\n"  # Range

    # Canonicalized headers
    x_ms_headers = {k.lower(): v for k, v in headers.items() if k.lower().startswith("x-ms-")}
    canonicalized_headers = "".join([f"{k}:{v}\n" for k, v in sorted(x_ms_headers.items())])
    string_to_sign += canonicalized_headers

    # Canonicalized resource
    canonicalized_resource = f"/{account_name}{parsed_url.path}"
    if query:
        canonicalized_resource += "\n" + "\n".join(
            f"{k}:{','.join(query[k])}" for k in sorted(query)
        )
    string_to_sign += canonicalized_resource

    # Sign the string
    signed_hmac_sha256 = hmac.new(
        base64.b64decode(account_key),
        string_to_sign.encode("utf-8"),
        hashlib.sha256
    )
    signature = base64.b64encode(signed_hmac_sha256.digest()).decode()
    return f"SharedKey {account_name}:{signature}"
