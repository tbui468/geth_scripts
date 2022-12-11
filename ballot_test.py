from deploy_contract import *
import asyncio


async def grant_voting_rights(filename, s):
    c = await s[0].deploy(filename, [["cat", "dog", "bird"], 30])

    addrs = await asyncio.gather(s[1].get_address(), s[2].get_address())

    await asyncio.gather(s[0].call(c, "grantVotingRight", [addrs[0]]))
    await asyncio.gather(s[1].call(c, "vote", [0]), s[2].call(c, "vote", [1]))
    #await asyncio.sleep(25)
    result = await s[0].call(c, "winner", [])
    if result[0] == 'cat':
        print("Voting Right: Passed")
    else:
        print("Voting Right: Failed")

async def break_ties(filename, s):
    c = await s[0].deploy(filename, [["cat", "dog", "bird"], 30])

    addrs = await asyncio.gather(s[1].get_address(), s[2].get_address())

    await asyncio.gather(s[0].call(c, "grantVotingRight", [addrs[0]]), s[0].call(c, "grantVotingRight", [addrs[1]]))
    await asyncio.gather(s[1].call(c, "vote", [0]), s[2].call(c, "vote", [1]))
    #await asyncio.sleep(25)
    await s[0].call(c, "breakTie", [1])
    result = await s[1].call(c, "winner", [])
    if result[0] == 'dog':
        print("Tie Breaking: Passed")
    else:
        print("Tie Breaking: Failed")

async def main():
    s0 = Signer("node1")
    s1 = Signer("node2")
    s2 = Signer("node3")

    filename = "Ballot.sol"
    await compile_contract(filename)

    await asyncio.gather(grant_voting_rights(filename, [s0, s1, s2]), break_ties(filename, [s0, s1, s2]))

asyncio.run(main())

