from flask import Flask, request, render_template, redirect, url_for, flash
from modules.azure_blob import upload_blob_with_sdk, generate_blob_url
from modules.document_intelligence import analyze_invoice_with_sdk, extract_invoice_insights
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Para mensagens flash

UPLOAD_FOLDER = "resources"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Garante que a pasta de uploads existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part in the request.")
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            flash("No selected file.")
            return redirect(request.url)

        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)

        try:
            # Passo 1: Upload do arquivo para o Azure Blob Storage
            upload_blob_with_sdk(file_path)

            # Passo 2: Gerar URL do Blob
            blob_url = generate_blob_url(file.filename)

            # Passo 3: Analisar o documento com Azure Document Intelligence
            analysis_result = analyze_invoice_with_sdk(blob_url)

            # Passo 4: Extrair insights do resultado
            insights = extract_invoice_insights(analysis_result)

            # Passo 5: Renderizar os resultados na página de resultados
            return render_template("results.html", insights=insights)

        except Exception as e:
            flash(f"Error processing file: {e}")
            return redirect(request.url)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
