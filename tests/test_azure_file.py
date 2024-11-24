import pytest
from unittest.mock import patch, MagicMock
from modules.azure_file import upload_file_with_sdk, upload_file_with_http, generate_file_url


@patch("modules.azure_file.ShareServiceClient")
def test_upload_file_with_sdk(mock_share_service_client):
    """
    Test that `upload_file_with_sdk` uploads a file successfully using Azure SDK.
    """
    mock_file_client = MagicMock()
    mock_share_service_client.return_value.get_share_client.return_value.get_file_client.return_value = mock_file_client

    with patch("os.path.exists", return_value=True):
        upload_file_with_sdk("./resources/Invoice1.pdf")

    mock_file_client.upload_file.assert_called_once()
    print("Upload file with SDK test passed!")


@patch("modules.azure_file.requests.put")
def test_upload_file_with_http(mock_put):
    """
    Test that `upload_file_with_http` uploads a file successfully using HTTP.
    """
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_put.return_value = mock_response

    with patch("os.path.exists", return_value=True):
        upload_file_with_http("./resources/Invoice1.pdf")

    # Ensure the correct number of calls were made
    assert mock_put.call_count == 3  # Create share, create file, upload content

    # Validate each call
    first_call = mock_put.call_args_list[0]
    second_call = mock_put.call_args_list[1]
    third_call = mock_put.call_args_list[2]

    # Check the share creation call
    assert "restype=share" in first_call.args[0]  # First call URL includes share creation
    # Check the file creation call
    assert "Invoice1.pdf" in second_call.args[0]  # Second call URL includes file name
    assert "x-ms-type" in second_call.kwargs["headers"]  # Header for file type creation
    # Check the upload call
    assert "comp=range" in third_call.args[0]  # Third call URL includes range for upload

    print("Upload file with HTTP test passed!")


@patch("modules.azure_file.generate_file_sas")
def test_generate_file_url(mock_generate_file_sas):
    """
    Test that `generate_file_url` generates a valid SAS URL.
    """
    mock_generate_file_sas.return_value = "mock_sas_token"

    with patch("os.path.basename", return_value="Invoice1.pdf"):
        result = generate_file_url("./resources/Invoice1.pdf")

    assert "mock_sas_token" in result
    print("Generate file URL test passed!")
