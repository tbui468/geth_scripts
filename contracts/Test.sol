// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

contract Test {
    string public name = "default";
    uint public immutable N;
    uint public s = 42;
    address public immutable chairperson;
    bytes32 public short = "hmmm";
    uint[] public arr;

    Proposal public p = Proposal("test", 42);
    Proposal[] public props;

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
        props.push(Proposal("bird", 42));
        props.push(Proposal("dog", 12));
        props.push(Proposal("cat", 13));
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

    function get_arr() public view returns (uint, uint[] memory, uint) {
        return (42, arr, 255);
    }

    function get_props() public view returns (Proposal[] memory) {
        return props;
    }

    function get_two_structs() public view returns (Proposal memory p1, Proposal memory p2) {
        return (props[0], props[1]);
    }

    function get_prim_struct() public view returns (uint, Proposal memory p1) {
        return (42, props[0]);
    }

    function append_nums(uint[] memory _nums) public {
        for (uint i; i < _nums.length; i++) {
            arr.push(_nums[i]);
        }
    }
}
