import boto3
from botocore.exceptions import ClientError
from summarization.pdf_extract import *
import json
import time

def create_prompt(text):
    prompt = f"Summarize all useful information for a financial analyst. Be exhaustive and concise by avoiding unnecessary words. NO SENTENCES. Do not introduce your answer" + "\n\n" + text
    return prompt

def call_model(prompt, client, model_id):
    conversation = [
        {
            "role": "user",
            "content": [{"text": prompt}],
        }
    ]
    
    try:
        # Send the message to the model, using a basic inference configuration.
        response = client.converse(
            modelId=model_id,
            messages=conversation,
            inferenceConfig={"maxTokens":128,"temperature":0},
        )

        # Extract and print the response text.
        response_text = response["output"]["message"]["content"][0]["text"]

    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        return ""
    
    return response_text
    

def summarize_text(text, verbose=False):
    
    size_paragraph = 3000
    summary = ""
    
    for i in range(0, len(text), size_paragraph):
        print(f"Processing paragraph {i//size_paragraph + 1} / {len(text)//size_paragraph + 1} ...") if verbose else None
        paragraph = text[i:i+size_paragraph]
        user_message = create_prompt(paragraph)
        
        client = boto3.client("bedrock-runtime", region_name="us-west-2")
        
        model_id = "meta.llama3-1-70b-instruct-v1:0"
        
        response_text = call_model(user_message, client, model_id)
        
        summary += response_text
        
        time.sleep(1)
        
    return summary


if __name__ == "__main__":
    pdf_processed_path = "pdf/processed/processed_2020-annuel-10Q-FR-FINAL.txt"
    pdf_processed = ""
    pdf_filename_without_ext = os.path.splitext(os.path.basename(pdf_processed_path))[0]
    
    with open(pdf_processed_path, "r") as f:
        pdf_processed = f.read()
    
    summarized_text = summarize_text(pdf_processed)
    

    