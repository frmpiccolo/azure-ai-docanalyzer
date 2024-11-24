from azure.storage.fileshare import ShareServiceClient, generate_file_sas, FileSasPermissions
from datetime import datetime, timedelta, timezone
from modules.utils import get_env_variable
import os
import requests


def upload_file_with_sdk(file_path):
    """
    Uploads a file to Azure File Share using the Azure SDK.
    """
    account_name = get_env_variable("AZURE_STORAGE_ACCOUNT_NAME")
    account_key = get_env_variable("AZURE_STORAGE_ACCOUNT_KEY")
    share_name = get_env_variable("AZURE_STORAGE_SHARE_NAME")

    # Ensure the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Create the ShareServiceClient
    share_service_client = ShareServiceClient(
        account_url=f"https://{account_name}.file.core.windows.net",
        credential=account_key
    )
    share_client = share_service_client.get_share_client(share_name)

    # Ensure the share exists
    try:
        share_client.get_share_properties()
    except Exception:
        share_client.create_share()

    # Upload the file
    file_client = share_client.get_file_client(os.path.basename(file_path))
    with open(file_path, "rb") as file_data:
        file_client.upload_file(file_data)
    print(f"File '{os.path.basename(file_path)}' uploaded successfully to share '{share_name}'.")


def upload_file_with_http(file_path):
    """
    Uploads a file to Azure File Share using HTTP requests.
    """
    account_name = get_env_variable("AZURE_STORAGE_ACCOUNT_NAME")
    account_key = get_env_variable("AZURE_STORAGE_ACCOUNT_KEY")
    share_name = get_env_variable("AZURE_STORAGE_SHARE_NAME")

    # Ensure the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Step 1: Create the share if it does not exist
    share_url = f"https://{account_name}.file.core.windows.net/{share_name}?restype=share"
    current_time_utc = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    headers = {
        "x-ms-version": "2020-02-10",
        "x-ms-date": current_time_utc,
    }
    headers["Authorization"] = _generate_authorization_header(account_name, account_key, share_url, "PUT", headers)

    response = requests.put(share_url, headers=headers)
    if response.status_code not in [201, 409]:  # 201 = Created, 409 = Conflict (already exists)
        raise Exception(f"Error creating share: {response.text}")

    # Step 2: Create the file in the Azure File Share
    file_name = os.path.basename(file_path)
    file_url = f"https://{account_name}.file.core.windows.net/{share_name}/{file_name}"
    file_size = os.path.getsize(file_path)

    create_file_headers = {
        "x-ms-version": "2020-02-10",
        "x-ms-date": current_time_utc,
        "Content-Type": "application/octet-stream",
        "x-ms-content-length": str(file_size),
        "x-ms-type": "file",  # Required for file creation
        "x-ms-file-permission": "inherit",  # Inherit permissions from the parent directory
        "x-ms-file-attributes": "None",  # Default value
        "x-ms-file-creation-time": "now",  # Creation time
        "x-ms-file-last-write-time": "now",  # Last write time
    }
    create_file_headers["Authorization"] = _generate_authorization_header(account_name, account_key, file_url, "PUT", create_file_headers)

    response = requests.put(file_url, headers=create_file_headers)
    if response.status_code != 201:
        raise Exception(f"Error creating file: {response.text}")

    # Step 3: Upload the file contents in a single request
    upload_headers = {
        "x-ms-version": "2020-02-10",
        "x-ms-date": current_time_utc,
        "Content-Type": "application/octet-stream",
        "Content-Length": str(file_size),
        "x-ms-write": "update",  # Required for writing ranges
        "x-ms-range": f"bytes=0-{file_size - 1}",  # Specify the range
    }
    upload_headers["Authorization"] = _generate_authorization_header(
        account_name, account_key, f"{file_url}?comp=range", "PUT", upload_headers
    )

    with open(file_path, "rb") as file_data:
        response = requests.put(f"{file_url}?comp=range", headers=upload_headers, data=file_data)
        if response.status_code not in [201, 202]:  # 201 = Created, 202 = Accepted
            raise Exception(f"Error uploading file contents: {response.text}")

    print(f"File '{file_name}' uploaded successfully to share '{share_name}'.")


def _generate_authorization_header(account_name, account_key, url, method, headers=None):
    """
    Generates the Authorization header for HTTP requests to Azure File Share.
    """
    import hmac
    import hashlib
    import base64
    from urllib.parse import urlparse, parse_qs

    if headers is None:
        headers = {}

    # Parse the URL
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)

    # Build the string-to-sign
    string_to_sign = f"{method}\n"  # HTTP method
    string_to_sign += "\n"  # Content-Encoding
    string_to_sign += "\n"  # Content-Language
    string_to_sign += f"{headers.get('Content-Length', '')}\n"  # Content-Length
    string_to_sign += "\n"  # Content-MD5
    string_to_sign += f"{headers.get('Content-Type', '')}\n"  # Content-Type
    string_to_sign += "\n"  # Date (use x-ms-date instead)
    string_to_sign += "\n"  # If-Modified-Since
    string_to_sign += "\n"  # If-Match
    string_to_sign += "\n"  # If-None-Match
    string_to_sign += "\n"  # If-Unmodified-Since
    string_to_sign += "\n"  # Range

    # Canonicalized headers
    x_ms_headers = {k.lower(): v.strip() for k, v in headers.items() if k.lower().startswith("x-ms-")}
    canonicalized_headers = "".join(f"{k}:{v}\n" for k, v in sorted(x_ms_headers.items()))
    string_to_sign += canonicalized_headers

    # Canonicalized resource
    canonicalized_resource = f"/{account_name}{parsed_url.path}"
    if query:
        canonicalized_resource += "\n" + "\n".join(f"{k}:{','.join(query[k])}" for k in sorted(query))
    string_to_sign += canonicalized_resource

    # Compute the HMAC-SHA256 signature
    signed_hmac_sha256 = hmac.new(
        base64.b64decode(account_key),
        string_to_sign.encode("utf-8"),
        hashlib.sha256
    )
    signature = base64.b64encode(signed_hmac_sha256.digest()).decode()

    return f"SharedKey {account_name}:{signature}"


def generate_file_url(file_path):
    """
    Generates a SAS URL for a file in Azure File Share using the SDK.
    """
    account_name = get_env_variable("AZURE_STORAGE_ACCOUNT_NAME")
    account_key = get_env_variable("AZURE_STORAGE_ACCOUNT_KEY")
    share_name = get_env_variable("AZURE_STORAGE_SHARE_NAME")

    # Extract the file name from the provided file path
    filename = os.path.basename(file_path)  # Get only the file name
    file_segments = filename.split(os.sep)  # Split file name into segments (if necessary for Azure File Share)

    # Configure start and expiry times in UTC
    start_time = datetime.now(timezone.utc) - timedelta(hours=24)  # Start 24 hours earlier
    expiry_time = datetime.now(timezone.utc) + timedelta(hours=24)  # Expire in 24 hours

    # Generate the SAS token using the SDK
    sas_token = generate_file_sas(
        account_name=account_name,
        share_name=share_name,
        file_path=file_segments,  # Use the segments to build the file path for Azure File Share
        account_key=account_key,
        permission=FileSasPermissions(read=True),  # Grant read permission
        start=start_time,
        expiry=expiry_time
    )

    # Construct the public URL with the SAS token
    file_url = f"https://{account_name}.file.core.windows.net/{share_name}/{filename}?{sas_token}"
    print(f"Generated SAS URL: {file_url}")
    return file_url

