from pdf_extract import *
from summarize_text import *
import os
import pathlib

def summarization_pdf(pdf_path):
    pdf_name = os.path.basename(pdf_path)
    pdf_name_without_ext = os.path.splitext(pdf_name)[0]
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File {pdf_path} not found")
    
    if not os.path.exists(f"pdf/processed/processed_{pdf_name_without_ext}"):
        md_text = extract_text_from_pdf(pdf_path)
        md_text_processed = process_text(md_text)
        pathlib.Path(f"pdf/processed/processed_{pdf_name_without_ext}").write_bytes(md_text_processed.encode())
        
    if not os.path.exists(f"pdf/summarized/summarized_{pdf_name_without_ext}"):
        with open(f"pdf/processed/processed_{pdf_name_without_ext}", "r") as f:
            pdf_processed = f.read()
        summarized_text = summarize_text(pdf_processed)
        pathlib.Path(f"pdf/summaries/summarized_{pdf_name_without_ext}").write_bytes(summarized_text.encode())
        
if __name__ == "__main__":
    pdf_path = "pdf/reports/Consommation de Base/Métro/2020-annuel-10Q-FR-FINAL.pdf"
    summarization_pdf(pdf_path)