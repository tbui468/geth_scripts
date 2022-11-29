import subprocess
import time
import json
from eth_utils import keccak
from binascii import hexlify

id_count = 0
signer = "node2"

def encode_uint256(uint):
    s = hex(uint)[2:]
    return "0" * (64 - len(s)) + s


def encode_string(string):
    ret = encode_uint256(len(string))
    hex_string = hexlify(string.encode()).decode()
    ret += hex_string + "0" * (64 - len(hex_string))
    return ret

def encode_args(args):
    dynamic_data = ""
    ret = ""

    for i in range(len(args)):
        if isinstance(args[i], str):
            dynamic_data += encode_string(args[i])
            ret += encode_uint256(i * 32)
        elif isinstance(args[i], int):
            ret += encode_uint256(args[i])

    return ret + dynamic_data

def encode_method_call(method_sig, args):
    data = "0x" + str(keccak(text=method_sig).hex())[0:8]

    data += encode_args(args)

    return data

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

    #if a transaction is sent, get receipt of returned hash
    if method == "eth_sendTransaction":
        while True:
            temp = send_ipc_request("eth_getTransactionReceipt", [json.loads(output[1])['result']])
            if temp['result'] != None:
                return temp
            id_count -= 1 #don't increment id while waiting for transaction to show up

    return json.loads(output[1])


def deploy_contract(contract, args):
    subprocess.run("cd contracts && ./solc " + contract + " --bin -o . --overwrite --abi", shell=True)

    signer_addr = send_ipc_request("eth_coinbase", [])['result']
    #balance = send_ipc_request("eth_getBalance", [coinbase_addr, "latest"])
    #gas_price = send_ipc_request("eth_gasPrice", [])


    binary = "0x"
    with open("./contracts/" + contract[:-4] + ".bin", "r") as f:
        binary += str(f.read())

    binary += encode_args(args)

    gas_est = send_ipc_request("eth_estimateGas", [{"from": signer_addr, "data": binary}])
    contract_addr = send_ipc_request("eth_sendTransaction", [{"from": signer_addr, "gas": gas_est['result'], "data": binary}])['result']['contractAddress']
    return signer_addr, contract_addr

