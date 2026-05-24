import requests

API_URL = "https://cloud.flowiseai.com/api/v1/prediction/e3f1f56e-555e-4908-8e7d-f5363fea723c"

def query(payload):
    response = requests.post(API_URL, json=payload)
    return response.json()
    
output = query({
    "question": "Give me the recipe for brownie",
})

print(output["text"])