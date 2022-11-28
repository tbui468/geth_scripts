import subprocess
import time
import json
from eth_utils import keccak

def send_ipc_request(method, params, id_, node):
    p = subprocess.Popen('echo \'{"jsonrpc":"2.0","method":"' + method + '","params":' + params + ',"id":' + id_ + '}e\' | nc -U ./' + node + '/geth.ipc', shell=True, stdout=subprocess.PIPE)
    output = str(p.stdout.read()).split('\\n')
    return json.loads(output[1])

#compile contract
subprocess.run("cd contracts && ./solc HelloWorld.sol --bin -o . --overwrite --abi", shell=True)

coinbase = send_ipc_request("eth_coinbase", "[]", "1", "node2")
balance = send_ipc_request("eth_getBalance", '["' + coinbase['result'] + '", "latest"]', "2", "node2")
gas_price = send_ipc_request("eth_gasPrice", '[]', "3", "node2")
print(coinbase)
print(balance)
print(gas_price)


binary = ""
with open("./contracts/HelloWorld.bin", "r") as f:
    binary = str(f.read())

print(binary)

gas_est = send_ipc_request("eth_estimateGas", '[{"from": "' + coinbase['result'] + '", "data": "0x' + binary + '"}]', "4", "node2")
print(gas_est)


trans_hash = send_ipc_request("eth_sendTransaction", '[{"from": "' + coinbase['result'] + '", "gas": "' + gas_est['result'] + '", "data": "0x' + binary + '"}]', "5", "node2")
print(trans_hash)

while True:
    trans_receipt = send_ipc_request("eth_getTransactionReceipt", '["' + trans_hash['result'] + '"]', "7", "node2")
    if trans_receipt['result'] != None:
        print(trans_receipt)
        break


data = "0x" + str(keccak(text='get()').hex())[0:8]
print(data)


"""
call_hash = send_ipc_request("eth_sendTransaction", '[{"from": "' + coinbase['result'] + '", "to": "' + trans_receipt['result']['contractAddress'] +  '", "data": "' + data + '"}]', "8", "node2")
print(call_hash)

while True:
    call_receipt = send_ipc_request("eth_getTransactionReceipt", '["' + call_hash['result'] + '"]', "9", "node2")
    if call_receipt['result'] != None:
        print(call_receipt)
        break
"""

call_result = send_ipc_request("eth_call", '[{"to": "' + trans_receipt['result']['contractAddress'] +  '", "data": "' + data + '"},  "latest"]', "8", "node2")
print(call_result)

#Use ABI to encode the payload
#Send a transaction with the payload and check result (use ABI to decode)
