from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from modules.utils import get_env_variable


def analyze_invoice_with_sdk(public_url):
    """
    Analyze invoice using Azure SDK.
    """
    endpoint = get_env_variable("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    key = get_env_variable("AZURE_DOCUMENT_INTELLIGENCE_KEY")
    client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    poller = client.begin_analyze_document_from_url("prebuilt-document", public_url)
    return poller.result()


def extract_invoice_insights(analysis_result):
    """
    Extracts detailed insights from the analyzed invoice, separating standard fields, custom fields,
    tables, images, and barcodes.
    """
    insights = {
        "standard_fields": {},
        "custom_fields": {},
        "tables": [],
        "images": [],
        "barcodes": []
    }

    # Extract standard fields from keyValuePairs
    if hasattr(analysis_result, "key_value_pairs"):
        for pair in analysis_result.key_value_pairs:
            key = pair.key.content if pair.key else "No key"
            value = pair.value.content if pair.value else "No value"
            confidence = pair.confidence if pair.confidence else 0

            insights["standard_fields"][key] = {
                "value": value,
                "confidence": confidence,
                "bounding_box": pair.key.bounding_regions[0].polygon if pair.key and pair.key.bounding_regions else None
            }

    # Extract custom fields from documents
    if hasattr(analysis_result, "documents"):
        for document in analysis_result.documents:
            if hasattr(document, "fields"):
                for field_name, field in document.fields.items():
                    field_value = field.value_string if hasattr(field, "value_string") else field.content
                    field_confidence = field.confidence if hasattr(field, "confidence") else 0

                    insights["custom_fields"][field_name] = {
                        "value": field_value,
                        "confidence": field_confidence,
                        "bounding_box": field.bounding_regions[0].polygon if field.bounding_regions else None
                    }

    # Extract tables
    if hasattr(analysis_result, "tables"):
        for table in analysis_result.tables:
            table_data = []
            num_columns = max(cell.column_index for cell in table.cells) + 1

            for row_index in range(table.row_count):
                row_data = [""] * num_columns
                for cell in table.cells:
                    if cell.row_index == row_index:
                        row_data[cell.column_index] = cell.content
                table_data.append(row_data)

            insights["tables"].append({
                "row_count": table.row_count,
                "column_count": table.column_count,
                "data": table_data
            })

    # Extract images (figures)
    if hasattr(analysis_result, "figures"):
        for figure in analysis_result.figures:
            insights["images"].append({
                "caption": figure.caption if hasattr(figure, "caption") else "No caption",
                "bounding_box": figure.bounding_regions[0].polygon if figure.bounding_regions else None
            })

    # Extract barcodes
    if hasattr(analysis_result, "barcodes"):
        for barcode in analysis_result.barcodes:
            insights["barcodes"].append({
                "type": barcode.kind if hasattr(barcode, "kind") else "Unknown",
                "value": barcode.value if hasattr(barcode, "value") else "No value",
                "confidence": barcode.confidence if hasattr(barcode, "confidence") else 0
            })

    return insights
