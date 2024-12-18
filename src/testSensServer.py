import requests

IP = "localhost"
END_POINT_HANDSHAKE = "handshake"
END_POINT_SENSE = "sense"

URL_HANDSHAKE = f"http://{IP}:8080/{END_POINT_HANDSHAKE}"
URL_SENSE = f"http://{IP}:8080/{END_POINT_SENSE}"

# Handshake
response = requests.post(URL_HANDSHAKE, json={}).json()["message"]
print(response)

# Sense
response = requests.post(URL_SENSE, json={"drone_id": 1}).json()["sense_status"]
print(response)