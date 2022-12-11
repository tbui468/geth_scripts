//SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

contract Ballot {

    struct Voter {
        bool voted;
        bool hasVotingRight;
        uint weight;
        uint votedPropIdx;
    }

    struct Proposal {
        bytes32 name;
        uint votes;
    }

    event VoteGranted(bytes32 msg, address addr);
    event Voted(bytes32 msg, address addr);
    event TieBroken(bytes32 msg);

    Proposal[] public proposals;
    mapping(address=>Voter) private voters;
    address private immutable organizer;
    uint public immutable voteEndTime;

    constructor (bytes32[] memory _props, uint _duration) {
        for (uint i = 0; i < _props.length; i++) {
            proposals.push(Proposal(_props[i], 0));
        }
        organizer = msg.sender;
        voteEndTime = block.timestamp + _duration;
    }

    modifier inTimeFrame() {
        //require(block.timestamp < voteEndTime);
        _;
    }

    function delegate(address _delegatee) public inTimeFrame {
        Voter storage delegator = voters[msg.sender];
        Voter storage delegatee = voters[_delegatee];

        require(delegator.hasVotingRight);
        require(!delegator.voted);
        require(delegatee.hasVotingRight);

        if (delegatee.voted) {
            proposals[delegatee.votedPropIdx].votes += delegator.weight;
        } else {
            delegatee.weight += delegator.weight;
        }
    }
    
    function breakTie(uint _propIdx) public inTimeFrame {
        require(organizer == msg.sender);
        uint mostIdx = 0;
        for (uint i = 1; i < proposals.length; i++) {
            if (proposals[i].votes > proposals[mostIdx].votes) {
                mostIdx = i; 
            }
        }

        uint highestVotes = proposals[mostIdx].votes;
        require(proposals[_propIdx].votes == highestVotes);
        proposals[_propIdx].votes++;
        emit TieBroken("Organizer broke tie");
    }

    function winner() public view returns (bytes32) {
        //require(block.timestamp >= voteEndTime);
        uint mostIdx = 0;
        for (uint i = 1; i < proposals.length; i++) {
            if (proposals[i].votes > proposals[mostIdx].votes) {
                mostIdx = i; 
            }
        }

        uint highestVotes = proposals[mostIdx].votes;
        for (uint i = 0; i < proposals.length; i++) {
            if (i == mostIdx) continue;
            require(proposals[i].votes != highestVotes);
        }

        return proposals[mostIdx].name;
    }

    function grantVotingRight(address _address) public inTimeFrame {
        require(organizer == msg.sender);
        voters[_address] = Voter(false, true, 1, 0);
        emit VoteGranted("Voting right granted to:", _address);
    }

    function vote(uint _propIdx) public inTimeFrame {
        Voter storage voter = voters[msg.sender];
        require(voter.hasVotingRight);
        require(!voter.voted);
        proposals[_propIdx].votes += voter.weight;
        voter.votedPropIdx = _propIdx;
        voter.voted = true;
        emit Voted("Address voted", msg.sender);
    }
}
