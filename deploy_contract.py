import subprocess
import json

#compile contract
subprocess.run("cd contracts && ./solc HelloWorld.sol --bin -o . --overwrite", shell=True)


#get gas estimate
p = subprocess.Popen('echo \'{"jsonrpc":"2.0","method":"eth_coinbase","params":[],"id":1}e\' | nc -U ./node1/geth.ipc', shell=True, stdout=subprocess.PIPE)
output = str(p.stdout.read())
output = output.split('\\n')
print(output[1])


p = subprocess.Popen('echo \'{"jsonrpc":"2.0","method":"eth_getBalance","params":["' + json.loads(output[1])['result'] + '", "latest"],"id":2}e\' | nc -U ./node1/geth.ipc', shell=True, stdout=subprocess.PIPE)
output = str(p.stdout.read())
output = output.split('\\n')
print(output[1])

#deploy contract

#check interface of contract (eg, test it)
