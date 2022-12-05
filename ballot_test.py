from deploy_contract import *


c = Contract("Ballot.sol", ["bird", 242, "turtle"])
print(c.call("name", []))
print(c.call("short", []))
print(c.call("chairperson", []))
print(c.call("all", []))
print(c.call("append_num", [15]))
print(c.call("append_num_with_event", [20]))
print(c.call("return_strings", []))
print(c.call("arr", [0]))
print(c.call("arr", [1]))
