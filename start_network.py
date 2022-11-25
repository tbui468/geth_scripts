import subprocess
import time
import stop_network

stop_network.stop_all()

#clean out old chain data
subprocess.run("rm -r node1/geth", shell=True)
subprocess.run("rm -r node2/geth", shell=True)
subprocess.run("rm -r miner1/geth", shell=True)

#set up nodes
subprocess.run("geth init --datadir node1 genesis.json", shell=True)
subprocess.run("geth init --datadir node2 genesis.json", shell=True)
subprocess.run("geth init --datadir miner1 genesis.json", shell=True)

#start bootstrap node
subprocess.run("bootnode -nodekey boot.key -addr :30305 &", shell=True)

pid = -1

while True:
    time.sleep(0.1)
    p = subprocess.Popen("fuser 30305/udp", shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    output = p.stdout.read()
    if len(str(output)) > 3: #not sure why no pid length is 3 instead of 0
        l = str(output).split()
        pid = l[1][:-1]
        break


#start other nodes in background
#keep node1 account locked and set --http flag to use with Metamask (port 8545)
subprocess.run("geth --datadir node1 --port 30306 --authrpc.port 30307 --bootnodes enode://cb8f896cfba8ee5530de9ac7db42c07a61e4f2dc4cb25595fa4371886a19de193bee1fba7ae7a5b9f97198389527231aba8ed58c43b074dc5a04590b51b641ca@127.0.0.1:0?discport=30305 --networkid 1 &", shell=True)

subprocess.run("geth --datadir node2 --port 30308 --authrpc.port 30309 --bootnodes enode://cb8f896cfba8ee5530de9ac7db42c07a61e4f2dc4cb25595fa4371886a19de193bee1fba7ae7a5b9f97198389527231aba8ed58c43b074dc5a04590b51b641ca@127.0.0.1:0?discport=30305 --networkid 1 --unlock 0x9482fe26D589a41008561a853f9bf02982d46CD0 --password node2/password.txt &", shell=True)

subprocess.run("geth --datadir miner1 --port 30310 --authrpc.port 30311 --bootnodes enode://cb8f896cfba8ee5530de9ac7db42c07a61e4f2dc4cb25595fa4371886a19de193bee1fba7ae7a5b9f97198389527231aba8ed58c43b074dc5a04590b51b641ca@127.0.0.1:0?discport=30305 --networkid 1 --unlock 0x729DdedDb1f0388c0e15dc6A5427990259708674 --password miner1/password.txt --miner.threads=1 &", shell=True)
