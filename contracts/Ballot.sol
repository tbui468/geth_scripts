// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

contract Ballot {
    string public name = "test";
    uint public s = 0;

    constructor(string memory _name) {
        name = _name;
    }
}
