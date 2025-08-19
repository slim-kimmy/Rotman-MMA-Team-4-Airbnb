import requests

url = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer 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"
}

data = {
    "model": "meta-llama/llama-4-scout-17b-16e-instruct",
    "messages": [
        {
            "role": "user",
            "content": "Explain the importance of fast language models"
        }
    ]
}

response = requests.post(url, headers=headers, json=data)

print(response.json())
