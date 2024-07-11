## PDF Invoice Data Extractor

This Python script extracts structured data from PDF invoices using image processing and natural language processing techniques.

## Features

- Converts PDF files to images
- Extracts text from images using OCR (Optical Character Recognition)
- Processes extracted text using a large language model to identify specific invoice data points
- Outputs structured data in JSON format

## Prerequisites

- Python 3.7+
- Tesseract OCR engine installed (Download and install tesseract-ocr-w64-setup)

## Installation

1. Clone this repository or download the script.
2. Install the required Python packages:

```bash
pip install python-dotenv pytesseract Pillow pypdfium2 streamlit pandas openai
```

Ensure Tesseract OCR is installed and the path is correctly set in the script.

## Usage

Place your PDF invoice in the same directory as the script or provide the full path.
Run the script:

bash
```bash
python script_name.py
```
The script will process the PDF and output the extracted data in JSON format.

## Configuration

Modify the default_data_points variable to customize the information you want to extract from the invoice.
Ensure the openai.api_base is set to your local LM Studio server address.

## How it works

1. The PDF is converted to images using pypdfium2.
2. Text is extracted from the images using Tesseract OCR.
3. The extracted text is processed by a large language model (using LM Studio) to identify specific invoice data points.
4. The structured data is returned in JSON format.
