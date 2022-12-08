from deploy_contract import *


async def grant_rights(contract, granter, grantee):
    return await granter.call(contract, "grantVotingRight", [await grantee.get_address()])

async def vote(contract, voter, args):
    return await voter.call(contract, "vote", args)

async def voteCount(contract, org, args):
    return await org.call(contract, "proposals", args)

async def main():
    s1 = Signer("node1")
    s2 = Signer("node2")
    s3 = Signer("node3")

    c = await s1.deploy("Ballot.sol", [["cat", "dog", "bird"], 60])

    results = await asyncio.gather(grant_rights(c, s1, s2), grant_rights(c, s1, s3))
    for r in results:
        print(r)

    results = await asyncio.gather(vote(c, s2, [0]), vote(c, s3, [1]))
    for r in results:
        print(r)

    results = await asyncio.gather(voteCount(c, s1, [0]), voteCount(c, s1, [1]), voteCount(c, s1, [2]))
    for r in results:
        print(r)

asyncio.run(main())

