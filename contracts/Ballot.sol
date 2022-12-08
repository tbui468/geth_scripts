//SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

contract Ballot {

    struct Proposal {
        bytes32 name;
        uint votes;
    }

    event VoteGranted(bytes32 msg, address addr);
    event Voted(bytes32 msg, address addr);

    Proposal[] public proposals;
    mapping(address=>bool) private addressVoted;
    mapping(address=>bool) private addressHasVotingRight;
    address private immutable organizer;
    uint public immutable voteEndTime;

    constructor (bytes32[] memory _props, uint _duration) {
        for (uint i = 0; i < _props.length; i++) {
            proposals.push(Proposal(_props[i], 0));
        }
        organizer = msg.sender;
        voteEndTime = block.timestamp + _duration;
    }

    function grantVotingRight(address _address) public {
        require(organizer == msg.sender);
        require(block.timestamp < voteEndTime);
        addressHasVotingRight[_address] = true;
        emit VoteGranted("Voting right granted to:", _address);
    }

    function vote(uint _propIdx) public {
        require(addressHasVotingRight[msg.sender] == true);
        require(addressVoted[msg.sender] == false);
        require(block.timestamp < voteEndTime);
        proposals[_propIdx].votes++;
        addressVoted[msg.sender] = true;
        emit Voted("Address voted", msg.sender);
    }
}
