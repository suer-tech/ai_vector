import json
import requests

def interact_stream(data_text):

    url = 'https://api.jina.ai/v1/embeddings'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer jina_473497b432084ea68b0688760f562e225uUVngjk0JJECPrbPGWC8NhyGXrZ'
    }

    data = {
        "model": "jina-embeddings-v3",
        "task": "text-matching",
        "late_chunking": False,
        "dimensions": "512",
        "embedding_type": "float",
        "input": [data_text]
    }

    response = requests.post(url, headers=headers, json=data)
    resp_json = response.json()
    emb = resp_json['data'][0]['embedding']
    print('')
    print(emb)
    return emb

