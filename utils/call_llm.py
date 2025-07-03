import os
from openai import OpenAI

def call_llm(prompt):    
    client_kwargs = {
        "api_key": os.environ.get("OPENAI_API_KEY", "your-api-key"),
        "base_url": os.environ.get("OPENAI_URL", "http://localhost:1234/v1")
    }
        
        # Create client with only the supported parameters
    client = OpenAI(**client_kwargs)  
    r = client.chat.completions.create(
        model="meta-llama-3.1-8b-instruct",
        messages=[{"role": "user", "content": prompt}],
        reasoning_effort="medium",
        store=False
    )
    return r.choices[0].message.content

# Example usage
if __name__ == "__main__":
    print(call_llm("Tell me a short joke")) 