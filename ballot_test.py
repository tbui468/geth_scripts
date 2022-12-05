from deploy_contract import *


contract = Contract("Ballot.sol", ["bird", 242, "turtle"])
r = contract.read("name", [])
print(r)
r = contract.read("short", [])
print(r)
r = contract.read("chairperson", [])
print(r)

r = contract.read("all", [])
print(r)

print(contract.write("append_num", [15]))
print(contract.write("append_num_with_event", [20]))
print(contract.read("return_strings", []))


print(contract.read("arr", [0]))
print(contract.read("arr", [1]))
