from deploy_contract import *

c = Contract("Ballot.sol", [["prop1", "prop2", "prop2"]])

print(c.call("proposals", [0]))
print(c.call("proposals", [1]))
print(c.call("proposals", [2]))
