//SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

contract Ballot {

    struct Proposal {
        bytes32 name;
        uint votes;
    }

    event VotingRightGranted(bytes32 msg, address addr);
    event Test(bytes32 msg, address addr);

    Proposal[] public proposals;
    mapping(address=>bool) private addressVoted;
    mapping(address=>bool) private addressHasVotingRight;
    address private immutable owner;

    constructor (bytes32[] memory _props) {
        for (uint i = 0; i < _props.length; i++) {
            proposals.push(Proposal(_props[i], 0));
        }
        owner = msg.sender;
    }

    function grantVotingRight(address _address) public {
        require(owner == msg.sender);
        addressHasVotingRight[_address] = true;
        emit VotingRightGranted("Voting right granted to:", _address);
    }

    function vote(uint _propIdx) public {
        require(addressHasVotingRight[msg.sender] == true);
        require(addressVoted[msg.sender] == false);
        proposals[_propIdx].votes++;
        addressVoted[msg.sender] = true;
        emit Test("Address voted", msg.sender);
    }
}
