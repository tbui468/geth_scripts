from deploy_contract import *

s1 = Signer("node1")
s2 = Signer("node2")
s3 = Signer("node3")

c = s1.deploy("Ballot.sol", [["cat", "dog", "bird"]])
print(s1.call(c, "grantVotingRight", [s2.get_address()]))
print(s1.call(c, "grantVotingRight", [s3.get_address()]))
print(s2.call(c, "vote", [0]))
print(s3.call(c, "vote", [0]))
print(s1.call(c, "proposals", [0]))
print(s1.call(c, "proposals", [1]))
print(s1.call(c, "proposals", [2]))

