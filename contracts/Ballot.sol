// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

contract Ballot {
    string public name = "default";
    uint public immutable N;
    uint public s = 42;
    address public immutable chairperson;
    bytes32 public short = "hmmm";

    constructor(string memory _name, uint _N, bytes32 _short) {
        name = _name;
        N = _N;
        chairperson = msg.sender;
        short = _short;
    }

    function all() public view returns(string memory, uint, uint, bytes32) {
        return (name, s, N, short);
    }
}
