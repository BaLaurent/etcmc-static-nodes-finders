import json
import json
import time
import requests


if __name__ == '__main__':
    # Load the data
    arrNodes = []
    countryCode = input("Enter the country code: ")
    response = requests.get('https://api.etcnodes.org/peers')
    peers = response.json()
    for peer in peers:
        try:
            last_seen = peer['contact']["last"]["unix"]
            if (time.time() - last_seen) < 300:
                if "ETCMC" in peer["name"]:
                    if peer["ip_info"]["countryCode"] == countryCode:
                        arrNodes.append(peer["enode"])
        except Exception as e:
            print(f"Something went wrong : {e}")
    with open("static-nodes.json", "w") as f:
        json.dump(arrNodes, f, indent=4)
    print(f"Found {len(arrNodes)} nodes.")
