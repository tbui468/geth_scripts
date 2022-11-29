// SPDX-License-Identifier: MIT

pragma solidity ^0.8.17;

contract HelloWorld {
    string public s = "Hello world";
    uint256 public n = 42;

    function add(uint _a, uint _b) public pure returns (uint256) {
        return _a + _b;
    }

    function setN(uint _n) public pure returns (uint256) {
        uint256 t = _n;
        return t;
    }

    function setS(string calldata _s) public {
        s = _s;
    }
}
