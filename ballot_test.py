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

async def delegate_before_vote(filename, s):
    c = await s[0].deploy(filename, [["cat", "dog", "bird"], 30])

    addrs = await asyncio.gather(s[1].get_address(), s[2].get_address(), s[3].get_address())
    await asyncio.gather(s[0].call(c, "grantVotingRight", [addrs[0]]), s[0].call(c, "grantVotingRight", [addrs[1]]), s[0].call(c, "grantVotingRight", [addrs[2]]))
    await s[1].call(c, "delegate", [addrs[1]])
    await asyncio.gather(s[2].call(c, "vote", [0]), s[3].call(c, "vote", [1]))
    result = await asyncio.gather(s[0].call(c, "proposals", [0]), s[0].call(c, "proposals", [1]))
    if result[0][1] == 2 and result[1][1] == 1:
        print("Delegate Before Vote: Passed")
    else:
        print("Delegate Before Vote: Failed")

async def delegate_after_vote(filename, s):
    c = await s[0].deploy(filename, [["cat", "dog", "bird"], 30])

    addrs = await asyncio.gather(s[1].get_address(), s[2].get_address(), s[3].get_address())
    await asyncio.gather(s[0].call(c, "grantVotingRight", [addrs[0]]), s[0].call(c, "grantVotingRight", [addrs[1]]), s[0].call(c, "grantVotingRight", [addrs[2]]))
    await asyncio.gather(s[2].call(c, "vote", [0]), s[3].call(c, "vote", [1]))
    await s[1].call(c, "delegate", [addrs[1]])
    result = await asyncio.gather(s[0].call(c, "proposals", [0]), s[0].call(c, "proposals", [1]))
    if result[0][1] == 2 and result[1][1] == 1:
        print("Delegate After Vote: Passed")
    else:
        print("Delegate After Vote: Failed")

async def only_organizer_grants(filename, s):
    c = await s[0].deploy(filename, [["cat", "dog", "bird"], 30])

    addr = await s[1].get_address()
    result = await s[2].call(c, "grantVotingRight", [addr])
    if 'error' in result and result['error']['message'] == 'execution reverted':
        print("Only Organizer Grants Voting Rights: Passed")
    else:
        print("Only Organizer Grants Voting Rights: Failed")

async def cant_delegate_to_self(filename, s):
    c = await s[0].deploy(filename, [["cat", "dog", "bird"], 30])

    addr = await s[1].get_address()
    await s[0].call(c, "grantVotingRight", [addr])
    result = await s[1].call(c, "delegate", [addr])
    if 'error' in result and result['error']['message'] == "execution reverted: Can't delegate to self":
        print("Can't delegate to self: Passed")
    else:
        print("Can't delegate to self: Failed")

async def disallow_circular_delegation_short(filename, s):
    c = await s[0].deploy(filename, [["cat", "dog", "bird"], 30])

    addrs = await asyncio.gather(s[1].get_address(), s[2].get_address())
    await asyncio.gather(s[0].call(c, "grantVotingRight", [addrs[0]]), s[0].call(c, "grantVotingRight", [addrs[1]]))
    await s[1].call(c, "delegate", [addrs[1]])
    result = await s[2].call(c, "delegate", [addrs[0]])
    if 'error' in result and result['error']['message'] == "execution reverted: Circular delegation":
        print("Short circular delegation: Passed")
    else:
        print("Short circular delegation: Failed")

async def disallow_circular_delegation_long(filename, s):
    c = await s[6].deploy(filename, [["cat", "dog", "bird"], 30])
    addrs = await asyncio.gather(s[0].get_address(), s[1].get_address(), s[2].get_address())
    await asyncio.gather(s[6].call(c, "grantVotingRight", [addrs[0]]), s[6].call(c, "grantVotingRight", [addrs[1]]), s[6].call(c, "grantVotingRight", [addrs[2]]))
    await s[2].call(c, "delegate", [addrs[0]])
    await s[1].call(c, "delegate", [addrs[2]])
    result = await s[0].call(c, "delegate", [addrs[1]])
    if 'error' in result and result['error']['message'] == "execution reverted: Circular delegation":
        print("Long circular delegation: Passed")
    else:
        print("Long circular delegation: Failed")

async def main():
    s0 = Signer("node0")
    s1 = Signer("node1")
    s2 = Signer("node2")
    s3 = Signer("node3")
    s4 = Signer("node4")
    s5 = Signer("node5")
    s6 = Signer("node6")
    s7 = Signer("node7")
    s8 = Signer("node8")

    signers = [s0, s1, s2, s3, s4, s5, s6, s7, s8]

    filename = "Ballot.sol"
    await compile_contract(filename)

    await asyncio.gather(grant_voting_rights(filename, signers), break_ties(filename, signers), delegate_before_vote(filename, signers), delegate_after_vote(filename, signers), only_organizer_grants(filename, signers), cant_delegate_to_self(filename, signers), disallow_circular_delegation_short(filename, signers), disallow_circular_delegation_long(filename, signers))

asyncio.run(main())

