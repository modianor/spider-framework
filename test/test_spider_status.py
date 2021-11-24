import requests
import json

data = {'run': True}
# data = {'run': False}
response = requests.get('http://localhost:8888', params=data)
print(response.text)
