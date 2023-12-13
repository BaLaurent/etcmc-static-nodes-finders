import json
import requests
from ping3 import ping
import time
import shutil
import os

if __name__ == '__main__':
    # Load the data
    arrNodes = []
    scoreThresh = int(input("Enter the score threshold:"))
    responseNodesAllJson = requests.get('https://github.com/etclabscore/discv4-dns-lists/blob/etccore/snap.classic.blockd.info/nodes.all.json')
    nodes = json.loads("".join(responseNodesAllJson.json()["payload"]["blob"]["rawLines"]))
    with open("nodes.all.json","w") as file:
        json.dump(nodes,file,indent=4)
    arrScoreOver = []
    for node in nodes:
        try:
            if nodes[node]["score"] >= scoreThresh:
                arrScoreOver.append(node)
        except:
            pass
    with open("config.json","r") as fileConfig:
        config = json.load(fileConfig)
    pingThresh = int(input("Enter the ping threshold (ms):"))
    maxPeerAmt = int(input("Enter the number of peers you want:"))
    countryCode = input("If you want to filter by country code enter it (leave empty for only ping) :")
    if config["batEdited"] == False:
        installPath = ""
        while installPath == "":
            installPath = input("Enter the path to the etcnodes folder (leave empty for default):")
            if installPath == "":
                installPath = config["installPath"]
            else:
                config["installPath"] = installPath
        with open("START_GETH_FAST_NODE.bat") as f:
            lines = f.readlines()
        configPathInBat = False
        currentPath = os.path.abspath(os.getcwd())
        for i in range(0,len(lines)):
            if "set CONFIG_PATH=" in lines[i]:
                lines[i] = f"set CONFIG_PATH={currentPath}\config.toml\n"
                configPathInBat = True
        if not configPathInBat:
            with open("START_GETH_FAST_NODE.bat","a") as f:
                f.write(f'set CONFIG_PATH={currentPath}\config.toml\n:: Check if the configuration file exists\nif not exist "!CONFIG_PATH!" (\n	echo Configuration file not found at !CONFIG_PATH!.\n	echo Please make sure the file exists and try again.\n	pause\n	exit /b\n)\n:: Start the Ethereum Classic Geth node with the specified configurations\ngeth --classic ^\n--config "!CONFIG_PATH!" ^\n--cache 1024 ^\n--metrics ^\n--identity "ETCMCgethNode" ^\nconsole')
        else:
            with open("START_GETH_FAST_NODE.bat","w") as f:
                f.writelines(lines)
        shutil.copyfile("./START_GETH_FAST_NODE.bat", f"{installPath}\START_GETH_FAST_NODE.bat")
        config["batEdited"] = True
        with open("config.json","w") as file:
            json.dump(config,file)
    response = requests.get('https://api.etcnodes.org/peers')
    peers = response.json()
    for peer in peers:
        try:
            if len(arrNodes) >= maxPeerAmt:
                break
            if peer["id"] in arrScoreOver:
                if countryCode != "":
                    if peer["ip_info"]["countryCode"] != countryCode.upper():
                        print(f"skipped {peer['network']['localAddress']}")
                        continue
                last_seen = peer['contact']["last"]["unix"]
                peerIp = peer["network"]["localAddress"].split(":")[0]
                peerPort = peer["network"]["localAddress"].split(":")[1]
                if peerPort[:2] == "30":
                    if peer["network"]["inbound"] == True:
                        if (time.time() - last_seen) < 300:
                            if peer["protocols"]["eth"]["version"] == 67 and peer["protocols"]["eth"]["forkId"]["hash"] == "0x7fd1bb25":
                                peerPing = ping(peerIp)
                                if peerPing != None:
                                    if peerPing < pingThresh:
                                        if peer["enode"] not in arrNodes:
                                            arrNodes.append(peer["enode"])
        except Exception as e:
            print(f"Something went wrong : {e}")
    strNodes = '",\n"'.join(arrNodes)
    with open("original_config.toml","r") as file:
        data = file.readlines()
        for i, line in enumerate(data):
            if "#NODELIST" in line:
                data[i] = line.replace("#NODELIST",f'[\n"{strNodes}"\n]\n#{len(arrNodes)} nodes\n')
    with open("config.toml","w") as file:
        file.writelines(data)
    print(f"Found {len(arrNodes)} nodes.")
