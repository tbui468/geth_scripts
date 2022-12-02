from deploy_contract import *


contract = Contract("Ballot.sol", ["bird", 242, "turtle"])
r = contract.call("name", [])
print(r)
r = contract.call("short", [])
print(r)
r = contract.call("chairperson", [])
print(r)

r = contract.call("all", [])
print(r)
