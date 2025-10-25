// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IVerifier {
    function verify(bytes32 roundId, bytes calldata randomness, bytes calldata proof)
        external view returns (bool);
}

contract MockVerifier is IVerifier {
    function verify(bytes32, bytes calldata randomness, bytes calldata) external pure returns (bool) {
        return randomness.length == 32;
    }
}

contract ConsumerDemo {
    address public owner;
    address public verifier;
    mapping(bytes32 => bytes32) public ticket;

    event RandomnessFulfilled(bytes32 indexed roundId, bytes randomness, bytes proof, bytes32 ticket);

    constructor(address _verifier) {
        owner = msg.sender;
        verifier = _verifier;
    }
    function setVerifier(address _v) external {
        require(msg.sender == owner, "only owner");
        verifier = _v;
    }
    function fulfillRandomness(bytes32 roundId, bytes calldata randomness, bytes calldata proof) external {
        require(IVerifier(verifier).verify(roundId, randomness, proof), "verify fail");
        bytes32 t = keccak256(abi.encodePacked(randomness, msg.sender));
        ticket[roundId] = t;
        emit RandomnessFulfilled(roundId, randomness, proof, t);
    }
}
