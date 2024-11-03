import boto3
from botocore.exceptions import ClientError
from pdf_extract import *
import json

def create_prompt(text):
    prompt = f"Summarize all useful information for a financial analyst. Be exhaustive and concise by avoiding unnecessary words. NO SENTENCES. Do not introduce your answer" + "\n\n" + text
    return prompt

def summarize_text(text):
    user_message = create_prompt(text)
    
    client = boto3.client("bedrock-runtime", region_name="us-west-2")
    
    model_id = "anthropic.claude-3-opus-20240229-v1:0"
    
    conversation = [
        {
            "role": "user",
            "content": [{"text": user_message}],
        }
    ]
    
    try:
        # Send the message to the model, using a basic inference configuration.
        response = client.converse(
            modelId="anthropic.claude-3-opus-20240229-v1:0",
            messages=conversation,
            inferenceConfig={"maxTokens":4096,"temperature":0},
            additionalModelRequestFields={"top_k":250}
        )

        # Extract and print the response text.
        response_text = response["output"]["message"]["content"][0]["text"]

    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        exit(1)
    
    return response_text


if __name__ == "__main__":
    pdf_processed_path = "pdf\processed\processed_2020-annuel-10Q-FR-FINAL"
    pdf_processed = ""
    pdf_filename_without_ext = os.path.splitext(os.path.basename(pdf_processed_path))[0]
    
    with open(pdf_processed_path, "r") as f:
        pdf_processed = f.read()
    
    

    