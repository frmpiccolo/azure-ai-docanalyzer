import pytest
from unittest.mock import patch, MagicMock, ANY
from azure.ai.formrecognizer import AnalyzeResult
from modules.document_intelligence import analyze_invoice_with_sdk, extract_invoice_insights
from modules.azure_blob import upload_blob_with_sdk, generate_blob_url

@patch("modules.document_intelligence.DocumentAnalysisClient")
@patch("modules.azure_blob.BlobServiceClient")
def test_analyze_invoice_with_sdk(mock_blob_service_client, mock_document_client):
    """
    Test the full pipeline:
    1. Upload file to Azure Blob Storage
    2. Generate Blob URL
    3. Analyze document using Azure Document Intelligence SDK
    """
    # Mock Blob Service
    mock_blob_client = MagicMock()
    mock_blob_service_client.return_value.get_blob_client.return_value = mock_blob_client

    # Mock Document Analysis Client
    mock_client_instance = mock_document_client.return_value
    mock_client_instance.begin_analyze_document_from_url.return_value.result.return_value = AnalyzeResult()

    # Step 1: Upload file to blob
    file_path = "./resources/Invoice1.pdf"
    with patch("os.path.exists", return_value=True):
        upload_blob_with_sdk(file_path)

    # Step 2: Generate Blob URL
    mock_blob_client.upload_blob.assert_called_once_with(ANY, overwrite=True)
    blob_url = generate_blob_url(file_path)

    # Step 3: Analyze the document
    result = analyze_invoice_with_sdk(blob_url)
    assert result is not None
    mock_client_instance.begin_analyze_document_from_url.assert_called_once_with("prebuilt-document", blob_url)
    print("Analyze Invoice with SDK test passed!")


def test_extract_invoice_insights():
    """
    Test the `extract_invoice_insights` function with a mock analysis result.
    """
    mock_analysis_result = MagicMock()
    mock_analysis_result.key_value_pairs = [
        MagicMock(key=MagicMock(content="Key1"), value=MagicMock(content="Value1"), confidence=0.9),
        MagicMock(key=MagicMock(content="Key2"), value=MagicMock(content="Value2"), confidence=0.8),
    ]
    mock_analysis_result.documents = []
    mock_analysis_result.tables = []

    insights = extract_invoice_insights(mock_analysis_result)
    assert "standard_fields" in insights
    assert insights["standard_fields"]["Key1"]["value"] == "Value1"
    assert insights["standard_fields"]["Key2"]["confidence"] == 0.8
    print("Extract Invoice Insights test passed!")
