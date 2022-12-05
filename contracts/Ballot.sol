// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

contract Ballot {
    string public name = "default";
    uint public immutable N;
    uint public s = 42;
    address public immutable chairperson;
    bytes32 public short = "hmmm";
    uint[] public arr;

    Proposal public p = Proposal("test", 42);

    struct Proposal {
        bytes32 name;
        uint voteCount;
    }

    event AppendedNum(string message, string message2);
    event AppendedNum2(uint n, string message);

    constructor(string memory _name, uint _N, bytes32 _short) {
        name = _name;
        N = _N;
        chairperson = msg.sender;
        short = _short;
    }

    function all() public view returns(string memory, uint, uint, bytes32) {
        return (name, s, N, short);
    }

    function append_num(uint _num) public {
        arr.push(_num);
    }

    function append_num_with_event(uint _num) public {
        arr.push(_num);
        emit AppendedNum("event", "emitted");
        emit AppendedNum2(42, "emitted");
        emit AppendedNum2(23, "asdf");
    }

    function return_strings() public pure returns (string memory, string memory) {
        return ("dog", "cat");
    }

    function append_nums(uint[] memory _nums) public {
        for (uint i; i < _nums.length; i++) {
            arr.push(_nums[i]);
        }
    }
}
