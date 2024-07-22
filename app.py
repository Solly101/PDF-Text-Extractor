#from dotenv import load_dotenv
import pytesseract
from PIL import Image
from io import BytesIO
import pypdfium2 as pdfium
from dotenv import load_dotenv
from pytesseract import image_to_string
import streamlit as st
import multiprocessing
from tempfile import NamedTemporaryFile
import pandas as pd
import json
import requests
import multiprocessing
from tempfile import NamedTemporaryFile
import openai
import json
import streamlit as st
import re


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 1. Convert PDF file into images via pypdfium2


def convert_pdf_to_images(file_path, scale=300/72):

    pdf_file = pdfium.PdfDocument(file_path)

    page_indices = [i for i in range(len(pdf_file))]

    renderer = pdf_file.render(
        pdfium.PdfBitmap.to_pil,
        page_indices=page_indices,
        scale=scale,
    )

    final_images = []

    for i, image in zip(page_indices, renderer):

        image_byte_array = BytesIO()
        image.save(image_byte_array, format='jpeg', optimize=True)
        image_byte_array = image_byte_array.getvalue()
        final_images.append(dict({i: image_byte_array}))

    return final_images

# 2. Extract text from images via pytesseract


def extract_text_from_img(list_dict_final_images):

    image_list = [list(data.values())[0] for data in list_dict_final_images]
    image_content = []

    for index, image_bytes in enumerate(image_list):

        image = Image.open(BytesIO(image_bytes))
        raw_text = str(pytesseract.image_to_string(image))
        image_content.append(raw_text)

    return "\n".join(image_content)


def extract_content_from_url(url: str):
    images_list = convert_pdf_to_images(url)
    text_with_pytesseract = extract_text_from_img(images_list)

    return text_with_pytesseract


def extract_and_format_json_content(data):
    # Find the position of the first '{'
    start = data.find('{')
    # Find the position of the last '}'
    end = data.rfind('}')

    # Check if both '{' and '}' were found and in the correct order
    if start != -1 and end != -1 and start < end:
        json_content = data[start:end+1]
        # Add square brackets around the JSON content
        json_content = f'[{json_content}]'
    else:
        json_content = f'["{data}"]'  # If brackets are not found, use the entire string with added square brackets

    return json_content



# 3. Extract structure info from text via Large language model
def extract_structure_data(content: str, data_points):
    # Set up the OpenAI client to communicate with the local server
    openai.api_key = "lm-studio"
    openai.api_base = "http://localhost:1234/v1"

    # Define the prompt template
    template = f"""
    You are an expert admin tasked with extracting specific information from documents.

    {content}

    Above is the content; please try to extract all data points from the content above 
    and export all of them in a JSON arrays format:
    {data_points}


    Now please extract details from the content and export all of them in JSON arrays format, 
    return ONLY the JSON arrays:

    Example of expected format:
       {{
            "item": "book 1",
            "Title": "Introduction to python",
            "Amount": "$6000.00",
            "quantity": "1",
            "tax": "1%"
        }}


    Now, extract the requested details and provide ONLY the raw JSON arrays:
    """
    # Create the request payload
    payload = {
        "model": "lmstudio-ai/TheBloke/stablelm-zephyr-3b-GGUF",
        #"model":"TheBloke/stablelm-zephyr-3b-GGUF",
        "prompt": template,
        "temperature": 0,
    }


    try:
        # Send the request to the local server
        response = openai.Completion.create(**payload)
        # Extract the response text, assuming it's in the correct format
        results = response['choices'][0]['text'].strip()
        
        
    except Exception as e:
        results = f"An error occurred: {str(e)}"

    return results

def main():
    st.set_page_config(page_title="PDF text extractor", page_icon=":bird:")
    st.header("PDF text extractor :bird:")

    default_data_points = """{
        "invoice_item": "what is the item that charged",
        "Amount": "how much does the invoice item cost in total",
        "Company_name": "company that issued the invoice",
        "invoice_date": "when was the invoice issued"
    }"""
    data_points = st.text_area("Data points", value=default_data_points, height=170)

    uploaded_files = st.file_uploader("Upload PDFs", accept_multiple_files=True)

    if uploaded_files is not None and data_points is not None:
        results = []
        for file in uploaded_files:
            with NamedTemporaryFile(delete=False) as f:
                f.write(file.getbuffer())
                file_path_ = f.name
                try:
                    content = extract_content_from_url(file_path_)
                    
                    data = extract_structure_data(content, data_points)
                      # Debug: print extracted structure data
                    print("Raw content Structure Data:",content)
                    #print( "Structure Data by llm:",data)
                    cleaned_data = extract_and_format_json_content(data)

                    print("Cleaned Structure Data:", cleaned_data)
                    try:
                        json_data = json.loads(cleaned_data) 
                        if isinstance(json_data, list):
                            results.extend(json_data)  # Use extend() for lists
                        else:
                            results.append(json_data)  # Wrap the dict in a list
                    except json.JSONDecodeError as e:
                        st.error(f"JSON parsing error for file {file.name}: {e}")
                        print(f"JSON parsing error: {e}")  # Debug: print JSON error
                        continue
                except Exception as e:
                    st.error(f"An error occurred while processing the file {file.name}: {e}")

        if len(results) > 0:
            try:
                df = pd.DataFrame(results)
                st.subheader("Results")
                st.data_editor(df)
            except Exception as e:
                st.error(f"An error occurred while creating the DataFrame: {e}")
                st.write(results)
            

if __name__== '__main__':  

    multiprocessing.freeze_support()
    main()