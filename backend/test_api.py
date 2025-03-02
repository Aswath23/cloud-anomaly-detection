import requests

url = url = "http://127.0.0.1:8000/predict"

# Replace '...' with actual 42 numerical values
data = {
    "features": [
        0.1, 0.5, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9, 1.0,
        0.2, 0.3, 0.1, 0.5, 0.6, 0.9, 0.7, 0.8, 0.4, 0.3,
        0.5, 0.2, 0.1, 0.7, 0.9, 0.8, 0.6, 0.4, 0.3, 0.2,
        0.1, 0.5, 0.9, 0.7, 0.8, 0.6, 0.4, 0.3, 0.2, 0.1,
        0.5, 0.9
    ]
}

response = requests.post(url, json=data)
print(response.json())
