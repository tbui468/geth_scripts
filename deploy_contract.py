import subprocess
import time
import json
from eth_utils import keccak

id_count = 0
signer = "node2"

#Could make a send_request_and_wait function that loops until a receipt is received

def send_ipc_request(method, params):
    global id_count, signer
    id_count += 1

    param_string = "["
    for i in range(len(params)):
        if isinstance(params[i], dict):
            param_string += json.dumps(params[i])
        else:
            param_string += "\"" + params[i] + "\""

        if i != len(params) - 1:
            param_string += ","

    param_string += "]"


    p = subprocess.Popen('echo \'{"jsonrpc":"2.0","method":"' + method + '","params":' + param_string + ',"id":' + str(id_count) + '}e\' | nc -U ./' + signer + '/geth.ipc', shell=True, stdout=subprocess.PIPE)
    output = str(p.stdout.read()).split('\\n')
    return json.loads(output[1])

#test input

#compile contract
subprocess.run("cd contracts && ./solc HelloWorld.sol --bin -o . --overwrite --abi", shell=True)

coinbase = send_ipc_request("eth_coinbase", [])
balance = send_ipc_request("eth_getBalance", [coinbase['result'], "latest"])
gas_price = send_ipc_request("eth_gasPrice", [])
print(coinbase)
print(balance)
print(gas_price)

binary = "0x"
with open("./contracts/HelloWorld.bin", "r") as f:
    binary += str(f.read())

gas_est = send_ipc_request("eth_estimateGas", [{"from": coinbase['result'], "data": binary}])
print(gas_est)


trans_hash = send_ipc_request("eth_sendTransaction", [{"from": coinbase['result'], "gas": gas_est['result'], "data": binary}])
print(trans_hash)

while True:
    trans_receipt = send_ipc_request("eth_getTransactionReceipt", [trans_hash['result']])
    if trans_receipt['result'] != None:
        print(trans_receipt)
        break

data = "0x" + str(keccak(text='setN(uint256)').hex())[0:8]
data += "0" * 62 + "01"
gas_est = send_ipc_request("eth_estimateGas", [{"from": coinbase['result'], "to": trans_receipt['result']['contractAddress'], "data": data}])
print(gas_est)


call_hash = send_ipc_request("eth_sendTransaction", [{"from": coinbase['result'], "gas": gas_est['result'], "to": trans_receipt['result']['contractAddress'], "data": data}])
print(call_hash)

while True:
    call_receipt = send_ipc_request("eth_getTransactionReceipt", [call_hash['result']])
    if call_receipt['result'] != None:
        print(call_receipt)
        break

"""
data = "0x" + str(keccak(text='n()').hex())[0:8]
call_result = send_ipc_request("eth_call", '[{"to": "' + trans_receipt['result']['contractAddress'] +  '", "data": "' + data + '"},  "latest"]')
print(call_result)
"""

#Use ABI to encode the payload
#Send a transaction with the payload and check result (use ABI to decode)
