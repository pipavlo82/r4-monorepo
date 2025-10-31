// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {ECDSA} from "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import {MessageHashUtils} from "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";

/// @title Re4ctoR VRF Verifier (MVP)
/// @notice Minimal on-chain verifier for randomness signed off-chain.
contract R4VRFVerifier {
    error InvalidRandomnessSignature();

    event RandomnessVerified(address indexed sender, bytes32 randomness);

    /// @notice Verify EIP-191 signature (Eth Signed Message) over 32-byte message = randomness.
    function verify(bytes32 randomness, bytes calldata signature, address signer) public pure returns (bool) {
        // OZ v5: MessageHashUtils
        bytes32 ethHash = MessageHashUtils.toEthSignedMessageHash(randomness);
        address who = ECDSA.recover(ethHash, signature);
        return who == signer;
    }

    /// @notice Verify raw ECDSA(secp256k1) over keccak256(randomness) (без ETH-префікса).
    function verifyRaw(bytes32 randomness, bytes calldata signature, address signer) public pure returns (bool) {
        bytes32 digest = keccak256(abi.encodePacked(randomness));
        address who = ECDSA.recover(digest, signature);
        return who == signer;
    }

    /// @notice Submit randomness with EIP-191 signature. Reverts, якщо підпис не валідний.
    function submitRandom(bytes32 randomness, bytes calldata signature, address signer) external {
        if (!verify(randomness, signature, signer)) revert InvalidRandomnessSignature();
        emit RandomnessVerified(msg.sender, randomness);
    }
}
