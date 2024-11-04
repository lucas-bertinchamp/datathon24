import pymupdf4llm
import os
import sys
import nltk
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

def extract_text_from_pdf(pdf_path):
    md_text = pymupdf4llm.to_markdown(pdf_path)
    return md_text

def process_text(text):
    
    # remove stopwords
    stopwords = set(nltk.corpus.stopwords.words("english")).union(set(nltk.corpus.stopwords.words("french")))
    
    words = text.split(" ")
    words = [word for word in words if word.lower() not in stopwords]
    
    # Remove punctuation
    words = [word for word in words if word.isalnum()]
    
    # Remove line breaks
    words = [word for word in words if word != "\n"]
    
    return " ".join(words)

def create_prompt(pdf_name, pdf_text):
    prompt = f"Summarize all useful information for a financial analyst. Be exhaustive and concise by avoiding unnecessary words. No need to do sentences. No introduction sentences, just summarize. Here the text extracted from the PDF file called: {pdf_name}." + "\n\n" + pdf_text
    return prompt


if __name__ == "__main__":
    pdf_path = "pdf/reports/Consommation de Base/Métro/2020-annuel-10Q-FR-FINAL.pdf"
    pdf_name = os.path.basename(pdf_path)
    pdf_name_without_ext = os.path.splitext(pdf_name)[0]
    
    md_text = extract_text_from_pdf(pdf_path)
    md_text_processed = process_text(md_text)

    utils.save_file("pdf/processed", f"processed_{pdf_name_without_ext}.txt", md_text_processed)