// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title MockVerifier - placeholder (NOT a real VRF!)
/// Accepts (roundId, randomness, proof), checks basic sizes, emits event.
contract MockVerifier {
    event Verified(bytes32 indexed roundId, bytes randomness, bytes proof);

    function verify(bytes32 roundId, bytes calldata randomness, bytes calldata proof) external returns (bool) {
        require(randomness.length == 32, "bad randomness");
        require(proof.length >= 32, "bad proof");
        emit Verified(roundId, randomness, proof);
        return true;
    }
}
