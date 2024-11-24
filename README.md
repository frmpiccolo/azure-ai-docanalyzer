# azure-ai-docanalyzer

## Project Overview

`azure-ai-docanalyzer` is a Python-based application that integrates Azure Blob Storage and Azure Document Intelligence services. It provides functionality to securely upload documents, analyze their content, and extract meaningful insights. The project supports both a console interface and a web interface, making it flexible for various use cases.

---

> ⚠ **Disclaimer**: This project uses Azure services, which may incur costs. Be sure to review Azure's pricing and monitor your resource usage to avoid unexpected charges.

---

## Features

1. **Upload Files to Azure Blob Storage**:
   - Securely store documents using dynamically generated Shared Access Signatures (SAS).
2. **Analyze Documents**:
   - Extract metadata, tables, key-value pairs, and other structured data using Azure Document Intelligence.
3. **Web Interface**:
   - User-friendly web interface for file uploads and analysis.
4. **Extensive Testing**:
   - Comprehensive unit tests for all modules.
5. **Scalable Design**:
   - Structured project with modular components for easy extension and maintenance.

---

## Project Structure

```plaintext
azure-ai-docanalyzer/
├── barcodes/               # Directory for saving barcode images
├── images/                 # Directory for saving extracted images
├── modules/                # Core modules of the application
│   ├── __init__.py
│   ├── azure_blob.py       # Handles Azure Blob Storage operations
│   ├── azure_file.py       # Handles Azure File Share operations
│   ├── document_intelligence.py  # Interacts with Azure Document Intelligence
│   ├── utils.py            # Helper functions and environment variable handling
├── resources/              # Sample PDF files for testing
│   ├── Invoice1.pdf
│   ├── Invoice2.pdf
│   ├── Invoice3.pdf
│   ├── Invoice4.pdf
│   ├── Invoice5.pdf
├── tests/                  # Unit tests for all modules
│   ├── test_azure_blob.py
│   ├── test_azure_file.py
│   ├── test_document_intelligence.py
│   ├── test_utils.py
├── venv/                   # Python virtual environment (ignored in .gitignore)
├── web/                    # Web interface files
│   ├── templates/
│   │   ├── index.html      # Html template for the home page
│   │   ├── results.html    # Html tempalte for the results
│   ├── app.py              # Flask application
├── .env                    # Environment variables file (ignored in .gitignore)
├── .gitignore              # Git ignore file
├── LICENSE                 # License file
├── main.py                 # Entry point for the console application
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
```

---

## Prerequisites

1. **Python**:
   - Install Python 3.8 or higher from [python.org](https://www.python.org/).
2. **Azure Subscription**:
   - An active Azure account to set up Blob Storage and Document Intelligence services.

### Python Version Management

This project uses Python version 3.9.18. If you use **pyenv**, the `.python-version` file will automatically set the correct version for this project. Install pyenv from [pyenv documentation](https://github.com/pyenv/pyenv).

---

## Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/azure-ai-docanalyzer.git
cd azure-ai-docanalyzer
```

### Step 2: Set Up a Virtual Environment
```bash
python -m venv venv
```

### Step 3: Activate the Virtual Environment
- On Windows:
  ```bash
  venv\Scripts\activate
  ```
- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Azure Services Configuration

### 1. Create a Resource Group
- Go to [Azure Portal](https://portal.azure.com/).
- Create a resource group (e.g., `azure-ai-docanalyzer-rg`).

### 2. Set Up Azure Blob Storage
- Create a Storage Account.
- Note the connection string from the **Access keys** section.

### 3. Set Up Azure Document Intelligence
- Create a Form Recognizer resource.
- Note the **Endpoint** and **API Key** from the **Keys and Endpoint** section.

---

## Configuration

1. Create a `.env` file in the root directory:
    ```plaintext
    AZURE_STORAGE_ACCOUNT_NAME=your_storage_account_name
    AZURE_STORAGE_ACCOUNT_KEY=your_storage_account_key
    AZURE_STORAGE_BLOB_CONTAINER_NAME=your_container_name
    AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your_document_intelligence_endpoint
    AZURE_DOCUMENT_INTELLIGENCE_KEY=your_document_intelligence_key
    ```

2. Replace placeholders with your actual Azure resource details.

---

## Usage

### Running in Console Mode
To analyze documents using the console:
```bash
python main.py
```

### Running the Web Interface
To start the Flask-based web interface:
```bash
python web/app.py
```
Access the application at `http://127.0.0.1:5000`.

---

## Running Unit Tests

1. **Install Test Dependencies**:
   Ensure the virtual environment is active, then run:
   ```bash
   pip install pytest
   ```

2. **Run Tests**:
   Use the following command to execute all tests:
   ```bash
   pytest
   ```

---

## Key Features

1. **Document Insights**:
   - Extracts standard fields (key-value pairs), tables, barcodes, and images from documents.
2. **Blob Storage Integration**:
   - Securely uploads and retrieves documents from Azure Blob Storage.
3. **Web and Console Support**:
   - Offers both CLI and GUI interfaces for seamless document analysis.

---

## Known Limitations

- Some features (e.g., `Custom Query Fields`) require the `2024-07-31-preview` API version, which is only available via the Azure AI Document Intelligence Studio.

---

> ⚠ **Disclaimer**: Using Azure services incurs costs. Ensure you monitor your Azure resources and review billing details in the Azure Portal.

---

## License

This project is licensed under the [MIT License](LICENSE).
```