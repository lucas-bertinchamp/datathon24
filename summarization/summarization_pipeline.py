import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from summarization.pdf_extract import *
from summarization.summarize_text import *

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
        utils.save_file("pdf/processed", f"processed_{pdf_name_without_ext}.txt", md_text_processed)
    
    if not os.path.exists(f"pdf/summaries/summarized_{pdf_name_without_ext}.txt"):
        print(f"Summarizing text from {pdf_name} ...") if verbose else None
        with open(f"pdf/processed/processed_{pdf_name_without_ext}.txt", "r") as f:
            pdf_processed = f.read()
        try:
            summarized_text = summarize_text(pdf_processed, verbose=verbose)
            if len(summarized_text) == 0:
                print(f"Error in summarizing text. Process continues ...") if verbose else None
                return ""
            utils.save_file("pdf/summaries", f"summarized_{pdf_name_without_ext}.txt", summarized_text)
        except Exception as e:
            print(f"Error in summarizing text") if verbose else None
            return ""
        
    with open(f"pdf/summaries/summarized_{pdf_name_without_ext}.txt", "r") as f:
        summarized_text = f.read()
        
    return summarized_text
        
if __name__ == "__main__":
    pdf_path = "pdf/reports/Consommation de Base/Métro/Rapport-annuel-2019-francais.pdf"
    summarization_pdf(pdf_path, verbose=True)