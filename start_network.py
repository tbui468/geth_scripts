import subprocess
import time
import stop_network

stop_network.stop_all()

#clean out old chain data
subprocess.run("rm -r node0/geth", shell=True)
subprocess.run("rm -r node1/geth", shell=True)
subprocess.run("rm -r node2/geth", shell=True)
subprocess.run("rm -r node3/geth", shell=True)
subprocess.run("rm -r node4/geth", shell=True)
subprocess.run("rm -r node5/geth", shell=True)
subprocess.run("rm -r node6/geth", shell=True)
subprocess.run("rm -r node7/geth", shell=True)
subprocess.run("rm -r node8/geth", shell=True)
subprocess.run("rm -r node9/geth", shell=True)

#set up nodes
subprocess.run("geth init --datadir node0 genesis.json", shell=True)
subprocess.run("geth init --datadir node1 genesis.json", shell=True)
subprocess.run("geth init --datadir node2 genesis.json", shell=True)
subprocess.run("geth init --datadir node3 genesis.json", shell=True)
subprocess.run("geth init --datadir node4 genesis.json", shell=True)
subprocess.run("geth init --datadir node5 genesis.json", shell=True)
subprocess.run("geth init --datadir node6 genesis.json", shell=True)
subprocess.run("geth init --datadir node7 genesis.json", shell=True)
subprocess.run("geth init --datadir node8 genesis.json", shell=True)
subprocess.run("geth init --datadir node9 genesis.json", shell=True)

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
boot_id = "enode://cb8f896cfba8ee5530de9ac7db42c07a61e4f2dc4cb25595fa4371886a19de193bee1fba7ae7a5b9f97198389527231aba8ed58c43b074dc5a04590b51b641ca@127.0.0.1:0?discport=30305"
def start_node(name, port, authrpc_port, account, http, mine):
    command = "geth --datadir " + name + " --port " + port + " --authrpc.port " + authrpc_port
    if http:
        command += " --http "
    command += " --bootnodes " + boot_id + " --networkid 1 "
    if mine:
        #command += " --mine --miner.threads=1 "
        command += " --mine "
    if not http:
        command += " --unlock " + account + " --password " + name + "/password.txt"
    command += " &"
    subprocess.run(command, shell=True)

#keep node1 account locked and set --http flag to use with Metamask (port 8545)
start_node("node0", "30306", "30307", "0x7Af80e614E7BfdD635f94cddbB9e80e269E6070a", False, False)
start_node("node1", "30308", "30309", "0xD8b3A2eBa89Bc06A2bDBDFa41da277Ac2ace4B7B", False, False)
start_node("node2", "30310", "30311", "0x9482fe26D589a41008561a853f9bf02982d46CD0", False, False)
start_node("node3", "30312", "30313", "0x729DdedDb1f0388c0e15dc6A5427990259708674", False, False)
start_node("node4", "30314", "30315", "0x58BC03D864625fd85252c8056D597CB1a670208E", False, False)
start_node("node5", "30316", "30317", "0x0a8AfbC6F05D1091186f6963211Fc6E90d3C0467", False, False)
start_node("node6", "30318", "30319", "0xd3138Bf958DAe29c8b6F9C53e1fd7893fec4E17a", False, False)
start_node("node7", "30320", "30321", "0x8FfCB4286A874D3249cb2B14b5B31AaAcFD90ba9", False, False)
start_node("node8", "30322", "30323", "0x56029194867199Bf7e5e5BaF60B43CFc84135991", False, False)
start_node("node9", "30324", "30325", "0x7cfCa091bF7c7D62D1F13921394ABD53F366a144", False, True)

