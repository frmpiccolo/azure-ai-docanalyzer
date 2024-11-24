import pytest
from unittest.mock import patch, MagicMock, ANY
from modules.azure_blob import upload_blob_with_sdk, upload_blob_with_http, generate_blob_url

@patch("modules.azure_blob.BlobServiceClient")
def test_upload_blob_with_sdk(mock_blob_service_client):
    """
    Test that `upload_blob_with_sdk` uploads a file successfully using Azure SDK.
    """
    mock_blob_client = MagicMock()
    mock_blob_service_client.return_value.get_blob_client.return_value = mock_blob_client

    with patch("os.path.exists", return_value=True):
        upload_blob_with_sdk("./resources/Invoice1.pdf")

    mock_blob_client.upload_blob.assert_called_once_with(
        ANY, overwrite=True
    )
    print("Upload blob with SDK test passed!")


@patch("modules.azure_blob.requests.put")
def test_upload_blob_with_http(mock_put):
    """
    Test that `upload_blob_with_http` uploads a file successfully using HTTP.
    """
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_put.return_value = mock_response

    with patch("os.path.exists", return_value=True):
        upload_blob_with_http("./resources/Invoice1.pdf")

    assert mock_put.call_count == 2  # First for creating the container, second for uploading
    print('Pass."')

@patch("modules.azure_blob.BlobServiceClient")
def test_generate_blob_url(mock_blob_service_client):
    """
    Test that `generate_blob_url` generates the correct URL for a blob.
    """
    with patch("os.path.basename", return_value="Invoice1.pdf"):
        blob_url = generate_blob_url("./resources/Invoice1.pdf")

    assert "Invoice1.pdf" in blob_url
    print("Generate blob URL test passed!")


