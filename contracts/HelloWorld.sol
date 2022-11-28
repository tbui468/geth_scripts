// SPDX-License-Identifier: MIT

pragma solidity ^0.8.17;

contract HelloWorld {
    uint256 public s = 42;
    function get() public view returns (uint256) {
        return s;
    }
}
