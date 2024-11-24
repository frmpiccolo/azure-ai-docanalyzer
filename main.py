from modules.azure_blob import upload_blob_with_sdk, generate_blob_url
from modules.document_intelligence import analyze_invoice_with_sdk, extract_invoice_insights
from tabulate import tabulate
import os


def print_section(title, data):
    """
    Helper function to print a section of the results in a clear format.
    """
    print(f"\n{'=' * 140}\n{title}\n{'=' * 140}")
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for sub_key, sub_value in value.items():
                    print(f"  - {sub_key}: {sub_value}")
            else:
                print(f"{key}: {value}")
    elif isinstance(data, list):
        for index, item in enumerate(data, start=1):
            if isinstance(item, list):  # If it's a list of lists (table rows)
                print(tabulate(item, tablefmt="grid"))
            elif isinstance(item, dict):  # If it's a dictionary (e.g., table metadata)
                print(f"Item {index}: {item}")
            else:
                print(f"{index}: {item}")
    else:
        print(data)


def save_barcode(barcode_data, output_dir="barcodes"):
    """
    Save barcode as an image if available.
    """
    try:
        from barcode import Code128
        from barcode.writer import ImageWriter

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for idx, barcode in enumerate(barcode_data):
            barcode_value = barcode.get("value", "unknown")
            barcode_image = Code128(barcode_value, writer=ImageWriter())
            filename = os.path.join(output_dir, f"barcode_{idx + 1}.png")
            barcode_image.save(filename)
            print(f"Barcode saved: {filename}")
    except ImportError:
        print("Error: Barcode generation requires 'python-barcode'. Install it using 'pip install python-barcode[images]'.")


def save_images(image_data, output_dir="images"):
    """
    Save extracted images to disk.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for idx, image in enumerate(image_data):
        filename = os.path.join(output_dir, f"image_{idx + 1}.png")
        # Placeholder: Save bounding box or dummy data as image
        # In a real application, you'd extract actual image content
        with open(filename, "w") as f:
            f.write(f"Placeholder for image {idx + 1}")
        print(f"Image saved: {filename}")


def print_tables(tables):
    """
    Helper to print tables in a formatted way.
    """
    for idx, table in enumerate(tables, start=1):
        print(f"\nTable {idx}:")
        if isinstance(table, dict) and "data" in table:
            # Assuming "data" contains rows as lists
            rows = table["data"]
            if rows:
                headers = rows[0]  # Use the first row as headers
                body = rows[1:]    # Remaining rows as table body
                print(tabulate(body, headers=headers, tablefmt="grid"))
            else:
                print("No data available in table.")
        else:
            print("Unexpected table format.")


if __name__ == "__main__":
    # Example file
    file_path = "./resources/Invoice2.pdf"

    # Ensure the file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found - {file_path}")
        exit(1)

    # Upload the file to Azure Blob Storage using SDK
    print("\nUploading blob with SDK...")
    upload_blob_with_sdk(file_path)
    blob_url = generate_blob_url(file_path)
    print(f"Blob uploaded successfully. URL: {blob_url}")

    # Analyze the document with Azure SDK
    print("\nAnalyzing document with Azure SDK...")
    analysis_result = analyze_invoice_with_sdk(blob_url)
    insights = extract_invoice_insights(analysis_result)

    # Print organized results
    print_section("File Information", {
        "File Name": os.path.basename(file_path),
        "File URL": blob_url,
        "Document Type": "Invoice"
    })

    print_section("Standard Fields", insights.get("standard_fields", {}))

    # Handle and print tables
    tables = insights.get("tables", [])
    print_tables(tables)

    # Handle and save images
    images = insights.get("images", [])
    save_images(images)

    # Handle and save barcodes
    barcodes = insights.get("barcodes", [])
    save_barcode(barcodes)
    print_section("Barcodes", [f"Saved barcode {idx + 1}" for idx in range(len(barcodes))])

    print("\nThe features below are only available when using apiVersion=2024-07-31.\nThis version is currently in preview and only accessible via Azure AI Document Intelligence Studio.")

    print_section("Custom Query Fields", insights.get("query_fields", {}))
    print_section("Images", [f"Saved image {idx + 1}" for idx in range(len(images))])


    # # Blob operations with HTTP
    # print("\nUploading blob with HTTP...")
    # upload_blob_with_http(file_path)
    # blob_url_http = generate_blob_url(file_path)
    # print(f"Blob URL (HTTP): {blob_url_http}")

    # # Document analysis using Azure HTTP
    # print("\nAnalyzing document with Azure HTTP API...")
    # analysis_result_http = analyze_document_with_sdk(blob_url_http)
    # insights_azure_http = extract_insights(analysis_result_http, "")
    # print("Analysis Result (Azure HTTP):\n", insights_azure_http)

    # # File Share operations with SDK
    # print("\nUploading file to File Share with SDK...")
    # upload_file_with_sdk(file_path)
    # file_url_sdk = generate_file_url(file_path)
    # print(f"File URL (SDK): {file_url_sdk}")

    # # Document analysis using Azure SDK for file share
    # print("\nAnalyzing document from File Share with Azure SDK...")
    # analysis_result_file_sdk = analyze_document_with_sdk(file_url_sdk)
    # insights_file_sdk = extract_insights(analysis_result_file_sdk, "")
    # print("Analysis Result (File Share SDK):\n", insights_file_sdk)

    # # File Share operations with HTTP
    # print("\nUploading file to File Share with HTTP...")
    # upload_file_with_http(file_path)
    # file_url_http = generate_file_url(file_path)
    # print(f"File URL (HTTP): {file_url_http}")

    # # Document analysis using Azure SDK for file share (HTTP)
    # print("\nAnalyzing document from File Share with Azure HTTP...")
    # analysis_result_file_http = analyze_document_with_sdk(file_url_http)
    # insights_file_http = extract_insights(analysis_result_file_http, "")
    # print("Analysis Result (File Share HTTP):\n", insights_file_http)
   
