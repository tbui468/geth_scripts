import asyncio
import json
from eth_utils import keccak
from binascii import hexlify, unhexlify

id_count = 0

class Signer():
    def __init__(self, name):
        self.name = name #either node0, node1, etc
        self.addr = None

    async def deploy(self, sol_file, args):
        c = Contract(sol_file, args)
        await c.deploy(self.name)
        return c

    async def call(self, contract, method, args):
        return await contract.call(method, args, self.name)

    async def call_raw(self, contract, method, args):
        return await contract.call_raw(method, args, self.name)

    async def get_address(self):
        if self.addr != None:
            return self.addr
        r = await send_ipc_request("eth_coinbase", [], self.name)
        self.addr = r['result']
        return self.addr

async def compile_contract(name):
    command = "cd contracts && ./solc " + name + " --bin -o . --overwrite --abi --pretty-json"
    await asyncio.create_subprocess_shell(command)

class Contract():
    def __init__(self, contract, args):
        self.contract = contract
        self.args = args

    async def deploy(self, name):
        signer_addr = await send_ipc_request("eth_coinbase", [], name)
        signer_addr = signer_addr['result']

        binary = "0x"
        with open("./contracts/" + self.contract[:-4] + ".bin", "r") as f:
            binary += str(f.read())

        self.abi = []
        with open("./contracts/" + self.contract[:-4] + ".abi", "r") as f:
            self.abi = json.loads(f.read())


        constructor_abi = self._get_constructor_abi()
        binary += self._encode_args(constructor_abi, self.args)

        gas_est = await send_ipc_request("eth_estimateGas", [{"from": signer_addr, "data": binary}], name)
        self.contract_addr = await send_ipc_request("eth_sendTransaction", [{"from": signer_addr, "gas": gas_est['result'], "data": binary}], name)
        self.contract_addr = self.contract_addr['result']['contractAddress']

    async def call_raw(self, method_name, args, name):
        signer_addr = await send_ipc_request("eth_coinbase", [], name)
        signer_addr = signer_addr['result']
        encoded_method_sig = self._encode_method_sig(method_name)
        method_abi = self._get_method_abi(method_name)
        encoded_args = self._encode_args(method_abi, args)
        call_data = "0x" + encoded_method_sig + encoded_args

        if self.__is_pure(method_name) or self.__is_view(method_name):
            return await send_ipc_request("eth_call", [{"to": self.contract_addr, "data": call_data},  "latest"], name)
        else:
            gas_est = await send_ipc_request("eth_estimateGas", [{"from": signer_addr, "to": self.contract_addr, "data": call_data}], name)
            if 'error' in gas_est:
                return gas_est
            return await send_ipc_request("eth_sendTransaction", [{"from": signer_addr, "to": self.contract_addr, "gas": gas_est['result'], "data": call_data}], name)

    async def call(self, method_name, args, name):
        call_result = await self.call_raw(method_name, args, name)
        if 'result' in call_result and not isinstance(call_result['result'], dict): #read
            return self._decode_returns(self._get_method_abi(method_name), call_result['result'])
        elif 'result' in call_result and len(call_result['result']['logs']) != 0: #write with event
            logs = call_result['result']['logs']
            returns = []
            for l in logs:
                returns.append(self._decode_returns(self._get_event_abi(l['topics'][0]), l['data']))
            return returns
        elif 'error' in call_result:
            return call_result
        else: #write with no event emitted
            return []

    def __is_pure(self, method_name):
        return self._get_method_abi(method_name)['stateMutability'] == 'pure'

    def __is_view(self, method_name):
        return self._get_method_abi(method_name)['stateMutability'] == 'view'

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

    def _get_event_abi(self, event_hash):
        for method in self.abi:
            if method['type'] == 'event':
                sig = method['name'] + '('
                for p in method['inputs']:
                    sig += p['type'] + ','
                if sig[-1] == ',':
                    sig = sig[:-1]
                sig += ')'
                h = '0x' + str(keccak(text=sig).hex())
                if h == event_hash:
                    return method

        return None

    def _get_constructor_abi(self):
        for method in self.abi:
            if method['type'] == 'constructor':
                return method

    def _encode_args(self, method_abi, args):
        dynamic_data = ""
        ret = ""

        #TODO: this breaks if any of the arguments is a tuple/struct
        #need to change offset by more than 64 bytes if argument is tuple
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
            elif typee == 'address':
                ret += encode_address(arg)
            elif typee == 'bytes32[]':
                ret += encode_uint256((len(args) - i) * 32 + len(dynamic_data))
                dynamic_data += encode_uint256(len(arg))
                for a in arg:
                    dynamic_data += encode_bytes32(a)
            else:
                print("Unsupported encoding type")

        return ret + dynamic_data

    def _decode_returns(self, method_abi, returns):
        return_list = []
        returns = returns[2:] #trim 0x

        key = 'outputs' if method_abi['type'] == 'function' else 'inputs'

        i = 0
        for r in method_abi[key]:
            typee = r['type']
            offset = i * 64

            if typee == 'string':
                byte_offset = decode_uint256(returns[offset: offset + 64])
                return_list.append(decode_string(returns[byte_offset * 2:]))
            elif typee == 'uint256':
                return_list.append(decode_uint256(returns[offset: offset + 64]))
            elif typee == 'bytes32':
                return_list.append(decode_bytes32(returns[offset: offset + 64]))
            elif typee == 'address':
                return_list.append(decode_address(returns[offset: offset + 64]))
            elif typee == 'uint256[]':
                arr = []
                byte_offset = decode_uint256(returns[offset: offset + 64])
                count = decode_uint256(returns[byte_offset * 2: byte_offset * 2 + 64])
                for j in range(1, count + 1):
                    element_offset = j * 64
                    arr.append(decode_uint256(returns[byte_offset * 2 + element_offset: byte_offset * 2 + element_offset + 64]))
                return_list.append(arr)
            elif typee == 'tuple':
                elements = []
                for c in r['components']:
                    tuple_offset = offset + len(elements) * 64
                    if c['type'] == 'uint256':
                        elements.append(decode_uint256(returns[tuple_offset: tuple_offset + 64]))
                    elif c['type'] == 'bytes32':
                        elements.append(decode_bytes32(returns[tuple_offset: tuple_offset + 64]))
            
                return_list.append(tuple(elements))
            elif typee == 'tuple[]':
                byte_offset = decode_uint256(returns[offset: offset + 64])
                count = decode_uint256(returns[byte_offset * 2: byte_offset * 2 + 64])
                arr = []
                for j in range(0, count):
                    elements = []
                    for c in r['components']:
                        tuple_offset = byte_offset * 2 + 64 + len(elements) * 64 + len(r['components']) * 64 * j
                        if c['type'] == 'uint256':
                            elements.append(decode_uint256(returns[tuple_offset: tuple_offset + 64]))
                        elif c['type'] == 'bytes32':
                            elements.append(decode_bytes32(returns[tuple_offset: tuple_offset + 64]))
                    arr.append(tuple(elements))
                return_list.append(arr)
            else:
                print("Unsupported decoding type")

            if typee == 'tuple':
                i += len(r['components'])
            else:
                i += 1

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

def encode_address(string):
    string = string[2:]
    return "0" * 24 + string

def decode_address(string):
    return "0x" + string[24:64]

async def send_ipc_request(method, params, name):
    global id_count
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


    command = 'echo \'{"jsonrpc":"2.0","method":"' + method + '","params":' + param_string + ',"id":' + str(id_count) + '}\' | nc -U -q 1 ./' + name + '/geth.ipc'
    proc = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE)

    stdout, _ = await proc.communicate()

    output = stdout.decode()

    #if a transaction is sent, get receipt of returned hash
    if method == "eth_sendTransaction":
        while True:
            if "error" in json.loads(output):
                return json.loads(output)
            temp = await send_ipc_request("eth_getTransactionReceipt", [json.loads(output)['result']], name)
            if temp['result'] != None:
                return temp
            id_count -= 1 #don't increment id while waiting for transaction to show up

    return json.loads(output)

