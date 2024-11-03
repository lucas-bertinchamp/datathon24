import boto3
from botocore.exceptions import ClientError
import json
import nltk

def preprocess_text(text):
    
    # remove stopwords
    stopwords = set(nltk.corpus.stopwords.words("english")).union(set(nltk.corpus.stopwords.words("french")))
    
    words = text.split(" ")
    words = [word for word in words if word.lower() not in stopwords]
    
    # Remove punctuation
    words = [word for word in words if word.isalnum()]
    
    # Remove line breaks
    words = [word for word in words if word != "\n"]
    
    return " ".join(words)

def create_prompt(text, context=None):
    prompt = f"""Give a sentiment analysis of the following text. Be concise and precise. 
                Remove unnecessary words. Do not introduce your answer. No sentences. Use financial terms for analysis.
                Don't give 'Note' to explain your answer.""" + "\n\n" + text
    if context:
        prompt += "\n\n" + """Use this context as a basis concerning the company : """ + "\n" +  context
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
            inferenceConfig={"maxTokens":1024,"temperature":0},
        )

        # Extract and print the response text.
        response_text = response["output"]["message"]["content"][0]["text"]

    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        exit(1)
    
    return response_text

def stmt_analysis(client, text, context=None):
    
    model_id = "meta.llama3-8b-instruct-v1:0"
    
    preprocess = preprocess_text(text)
    prompt = create_prompt(preprocess, context)
    response_text = call_model(prompt, client, model_id)
    return response_text

if __name__ == "__main__":
    client = boto3.client("bedrock-runtime", region_name="us-west-2")
    text = "The company is a leader in the energy sector. It has a strong presence in the market and has a solid financial position."
    context = "The company is a leader in the energy sector."
    response = stmt_analysis(client, text, context)
    print(response)