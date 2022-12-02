import subprocess
import time
import json
from eth_utils import keccak
from binascii import hexlify, unhexlify

id_count = 0
signer = "node2"

class Contract():
    def __init__(self, contract, args):
        subprocess.run("cd contracts && ./solc " + contract + " --bin -o . --overwrite --abi --pretty-json", shell=True)

        self.signer_addr = send_ipc_request("eth_coinbase", [])['result']

        binary = "0x"
        with open("./contracts/" + contract[:-4] + ".bin", "r") as f:
            binary += str(f.read())

        self.abi = []
        with open("./contracts/" + contract[:-4] + ".abi", "r") as f:
            self.abi = json.loads(f.read())


        constructor_abi = self._get_constructor_abi()
        binary += self._encode_args(constructor_abi, args)

        gas_est = send_ipc_request("eth_estimateGas", [{"from": self.signer_addr, "data": binary}])
        self.contract_addr = send_ipc_request("eth_sendTransaction", [{"from": self.signer_addr, "gas": gas_est['result'], "data": binary}])['result']['contractAddress']


    def call(self, method_name, args):
        encoded_method_sig = self._encode_method_sig(method_name)
        method_abi = self._get_method_abi(method_name)
        encoded_args = self._encode_args(method_abi, args)
        call_data = "0x" + encoded_method_sig + encoded_args

        call_result = send_ipc_request("eth_call", [{"to": self.contract_addr, "data": call_data},  "latest"])
        return self._decode_returns(method_abi, call_result['result'])

    def _encode_method_sig(self, method_name):
        method_abi = self._get_method_abi(method_name)

        method_sig = method_name + '('
        for inp in method_abi['inputs']:
            method_sig += inp['type'] + ','
        if method_sig[-1] == ',': #trim last comma
            method_sig = method_sig[:-1]
        method_sig += ')'

        return str(keccak(text=method_sig).hex())[0:8]

    def _get_method_abi(self, method_name):
        for method in self.abi:
            if method['type'] == 'function' and method['name'] == method_name:
                return method

    def _get_constructor_abi(self):
        for method in self.abi:
            if method['type'] == 'constructor':
                return method

    def _encode_args(self, method_abi, args):
        dynamic_data = ""
        ret = ""

        for i in range(len(args)):
            typee = method_abi['inputs'][i]['type']
            arg = args[i]

            if typee == 'string':
                ret += encode_uint256((len(args) - i) * 32 + len(dynamic_data))
                dynamic_data += encode_string(arg)
            elif typee == 'uint256':
                ret += encode_uint256(arg)
            elif typee == 'bytes32':
                ret += encode_bytes32(arg)
            else:
                print("Unsupported encoding type")

        return ret + dynamic_data

    def _decode_returns(self, method_abi, returns):
        return_list = []
        returns = returns[2:] #trim 0x

        for i in range(len(method_abi['outputs'])):
            typee = method_abi['outputs'][i]['type']
            offset = i * 64

            if typee == 'string':
                byte_offset = decode_uint256(returns[offset: offset + 64])
                string_start = offset + byte_offset * 2
                return_list.append(decode_string(returns[string_start:]))
            elif typee == 'uint256':
                return_list.append(decode_uint256(returns[offset: offset + 64]))
            elif typee == 'bytes32':
                return_list.append(decode_bytes32(returns[offset: offset + 64]))
            elif typee == 'address':
                return_list.append(decode_address(returns[offset: offset + 64]))
            else:
                print("Unsupported decoding type")

        return return_list


def encode_uint256(uint):
    s = hex(uint)[2:]
    return "0" * (64 - len(s)) + s

def decode_uint256(string):
    return int("0x" + string, 0)

def encode_string(string):
    ret = encode_uint256(len(string))
    hex_string = hexlify(string.encode()).decode()
    ret += hex_string + "0" * (64 - len(hex_string))
    return ret

def encode_bytes32(string):
    hex_string = hexlify(string.encode()).decode()
    return hex_string + "0" * (64 - len(hex_string))

def decode_bytes32(string):
    term_idx = 0
    for i in range(0, len(string), 2):
        if string[i] == '0' and string[i+1] == '0':
            term_idx = i
            break
    return unhexlify(string[:term_idx]).decode('utf-8')


def decode_string(string):
    length = decode_uint256(string[:64])
    return unhexlify(string[64: 64 + length * 2]).decode('utf-8')

def decode_address(string):
    return "0x" + string[26:66]


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

    return json.loads(output[1]) #index 0 is the error that kicks us out of the geth.ipc - probably should find a nicer way to exiting ;)

