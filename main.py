import json
import requests
from ping3 import ping
import time

if __name__ == '__main__':
    # Load the data
    arrNodes = []
    pingThresh = int(input("Enter the ping threshold (ms):"))
    maxPeerAmt = int(input("Enter the number of peers you want:"))
    countryCode = input("If you want to filter by country code enter it (leave empty for only ping) :")
    response = requests.get('https://api.etcnodes.org/peers')
    peers = response.json()
    arrPings = []
    arrIps = []
    arrEnodeIps = {}
    for peer in peers:
        try:
            if len(arrNodes) >= maxPeerAmt:
                break
            if countryCode != "":
                if peer["ip_info"]["countryCode"] != countryCode.upper():
                    print(f"skipped {peer['network']['localAddress']}")
                    continue
            last_seen = peer['contact']["last"]["unix"]
            peerIp = peer["network"]["localAddress"].split(":")[0]
            if (time.time() - last_seen) < 300:
                if "ETCMC" in peer["name"]:
                    peerPing = ping(peerIp)
                    if peerPing != None:
                        if peerPing < pingThresh:
                            if peer["enode"] not in arrNodes:
                                arrNodes.append(peer["enode"])
        except Exception as e:
            print(f"Something went wrong : {e}")
    with open("static-nodes.json", "w") as f:
        json.dump(arrNodes, f, indent=4)
    print(f"Found {len(arrNodes)} nodes.")
