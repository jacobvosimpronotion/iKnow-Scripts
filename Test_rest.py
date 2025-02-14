import requests
from requests.auth import HTTPBasicAuth

url = "https://tno.pna-web.com/tno/services/knowledgedomain?json"
username = input("Enter your username: ")
password = input("Enter your password: ")

try:
    response = requests.get(url, auth=HTTPBasicAuth(username, password))
    response.raise_for_status()  # Raise an error for bad status codes
    data = response.json()  # Parse the JSON data
    for domain in data.get('knowledgeDomains', []):
        print(domain.get('name'))  # Print the Name of each KnowledgeDomain
except requests.exceptions.RequestException as e:
    print(f"Error connecting to the REST service: {e}")