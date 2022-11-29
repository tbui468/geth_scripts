from deploy_contract import *

signer_addr, contract_addr = deploy_contract("HelloWorld.sol", [])

method_data = encode_method_call('setN(uint256)', [255])
gas_est = send_ipc_request("eth_estimateGas", [{"from": signer_addr, "to": contract_addr, "data": method_data}])
call_receipt = send_ipc_request("eth_sendTransaction", [{"from": signer_addr, "gas": gas_est['result'], "to": contract_addr, "data": method_data}])

method_data = encode_method_call('n()', [])
call_result = send_ipc_request("eth_call", [{"to": contract_addr, "data": method_data},  "latest"])
print(call_result)

