from summarization.pdf_extract import *
from summarization.summarize_text import *
import os
import pathlib

def summarization_pdf(pdf_path, verbose=False):
    pdf_name = os.path.basename(pdf_path)
    pdf_name_without_ext = os.path.splitext(pdf_name)[0]
    
    if verbose:
        print(f"Processing {pdf_name} ...")
        
    if not os.path.exists(pdf_path):
        print(f"File {pdf_path} not found") if verbose else None
        raise FileNotFoundError(f"File {pdf_path} not found")
    
    if not os.path.exists(f"pdf/processed/processed_{pdf_name_without_ext}.txt"):
        print(f"Extracting text from {pdf_name} ...") if verbose else None
        md_text = extract_text_from_pdf(pdf_path)
        md_text_processed = process_text(md_text)
        pathlib.Path(f"pdf/processed/processed_{pdf_name_without_ext}.txt").write_bytes(md_text_processed.encode())
    
    if not os.path.exists(f"pdf/summaries/summarized_{pdf_name_without_ext}.txt"):
        print(f"Summarizing text from {pdf_name} ...") if verbose else None
        with open(f"pdf/processed/processed_{pdf_name_without_ext}.txt", "r") as f:
            pdf_processed = f.read()
        try:
            summarized_text = summarize_text(pdf_processed)
            process_summary = process_text(summarized_text)
            if len(process_summary) == 0:
                print(f"Error in summarizing text. Process continues ...") if verbose else None
                return ""
            pathlib.Path(f"pdf/summaries/summarized_{pdf_name_without_ext}.txt").write_bytes(process_summary.encode())
        except Exception as e:
            print(f"Error in summarizing text") if verbose else None
            return ""
        
    with open(f"pdf/summaries/summarized_{pdf_name_without_ext}.txt", "r") as f:
        process_summary = f.read()
        
    return process_summary
        
if __name__ == "__main__":
    pdf_path = "pdf/reports/Consommation de Base/Métro/Rapport-annuel-2019-francais.pdf"
    summarization_pdf(pdf_path)