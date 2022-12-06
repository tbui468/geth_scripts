//SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

contract Ballot {

    struct Proposal {
        bytes32 name;
        uint votes;
    }

    Proposal[] public proposals;
    mapping(address=>bool) public addressVoted;

    constructor (bytes32[] memory _props) {
        for (uint i = 0; i < _props.length; i++) {
            proposals.push(Proposal(_props[i], 0));
        }
    }

    function grantVotingRight(address _address) public {

    }


    function vote(uint _propIdx) public {
        //require that use hasn't voted yet
        //  need a way to track who has voted
    }
}
