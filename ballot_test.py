from deploy_contract import *
import asyncio


async def grant_voting_rights(c, signers):
    s1 = signers[0]
    s2 = signers[1]
    s3 = signers[2]

    addrs = await asyncio.gather(s2.get_address(), s3.get_address())

    await asyncio.gather(s1.call(c, "grantVotingRight", [addrs[0]]))
    await asyncio.gather(s2.call(c, "vote", [0]), s3.call(c, "vote", [1]))
    await asyncio.sleep(25)
    result = await s1.call(c, "winner", [])
    if result[0] == 'cat':
        print("Voting Right: Passed")
    else:
        print("Voting Right: Failed")

async def break_ties(c, signers):
    s1 = signers[0]
    s2 = signers[1]
    s3 = signers[2]

    addrs = await asyncio.gather(s2.get_address(), s3.get_address())

    await asyncio.gather(s1.call(c, "grantVotingRight", [addrs[0]]), s1.call(c, "grantVotingRight", [addrs[1]]))
    await asyncio.gather(s2.call(c, "vote", [0]), s3.call(c, "vote", [1]))
    await asyncio.sleep(25)
    await s1.call(c, "breakTie", [1])
    result = await s2.call(c, "winner", [])
    if result[0] == 'dog':
        print("Tie Breaking: Passed")
    else:
        print("Tie Breaking: Failed")

async def main():
    s1 = Signer("node1")
    s2 = Signer("node2")
    s3 = Signer("node3")
    await compile_contract("Ballot.sol")

    c1, c2 = await asyncio.gather(s1.deploy("Ballot.sol", [["cat", "dog", "bird"], 30]), s1.deploy("Ballot.sol", [["cat", "dog", "bird"], 30]))

    await asyncio.gather(grant_voting_rights(c1, [s1, s2, s3]), break_ties(c2, [s1, s2, s3]))

asyncio.run(main())

