import requests
import json
url = "http://localhost:10017/asset/asset_master_list"

# Define the JSON data to be sent in the request body
data ={
"username" : "niraj",
"password" : "1234"
}

# Convert the Python dictionary to JSON format
json_data = json.dumps(data)

# Set the appropriate headers
headers = {
    "Content-Type": "application/json"
}

# Send the POST request with JSON data
response = requests.get(url, data=json_data, headers=headers)
if response.status_code == 200:
    # Print the response content
    print(response.json())
else:
    # Print an error message
    print("Error:", response.status_code)