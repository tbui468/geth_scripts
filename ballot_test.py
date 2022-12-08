from deploy_contract import *
import asyncio

async def main():
    s1 = Signer("node1")
    s2 = Signer("node2")
    s3 = Signer("node3")

    c = await s1.deploy("Ballot.sol", [["cat", "dog", "bird"], 30])

    results = await asyncio.gather(s1.call(c, "grantVotingRight", [await s2.get_address()]), s1.call(c, "grantVotingRight", [await s3.get_address()]))
    for r in results:
        print(r)

    results = await asyncio.gather(s2.call(c, "vote", [0]), s3.call(c, "vote", [1]))
    for r in results:
        print(r)

    results = await asyncio.gather(s1.call(c, "proposals", [0]), s1.call(c, "proposals", [1]), s1.call(c, "proposals", [2]))
    for r in results:
        print(r)

    await asyncio.sleep(20)

    print(await s1.call(c, "winner", []))
    print(await s1.call(c, "breakTie", [1]))
    print(await s2.call(c, "winner", []))

asyncio.run(main())

