// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title Re4ctoR VRF Verifier (MVP)
/// @notice Minimal on-chain verifier for randomness signed off-chain.
/// @dev Phase 1 = ECDSA. Phase 2 = PQ signatures (Dilithium / Kyber wraps)
contract R4VRFVerifier {
    /// @notice Emitted when randomness is accepted on-chain.
    /// @param sender Who submitted it to the contract
    /// @param randomness 32-byte randomness that was verified
    event RandomnessVerified(address indexed sender, bytes32 randomness);

    /**
     * @notice Verify that `randomness` was signed by `signer`.
     * @dev Off-chain service will sign keccak256(randomness) using its private key.
     *
     * @param randomness The claimed random value (32 bytes from Re4ctoR API)
     * @param signature  65-byte ECDSA signature (r||s||v)
     * @param signer     Expected signer (public address that should have signed)
     *
     * @return ok true if signature is valid and comes from `signer`
     */
    function verify(
        bytes32 randomness,
        bytes calldata signature,
        address signer
    ) public pure returns (bool ok) {
        // 1. hash the message (randomness) exactly as done off-chain
        bytes32 msgHash = keccak256(abi.encodePacked(randomness));

        // 2. prefix as Ethereum signed message ("\x19Ethereum Signed Message:\n32")
        bytes32 ethSigned = ECDSA.toEthSignedMessageHash(msgHash);

        // 3. recover signer
        address recovered = ECDSA.recover(ethSigned, signature);
        return (recovered == signer);
    }

    /**
     * @notice Example "consumer hook".
     * @dev In a real app, game/lottery contract would call this after verify().
     * Right now it's just emitting an event so you can see it on-chain.
     */
    function submitRandom(bytes32 randomness) external {
        emit RandomnessVerified(msg.sender, randomness);
    }
}

/// @dev Minimal ECDSA helper (trimmed from OpenZeppelin ECDSA)
library ECDSA {
    function toEthSignedMessageHash(bytes32 hash) internal pure returns (bytes32) {
        // This mirrors eth_sign / personal_sign
        return keccak256(
            abi.encodePacked("\x19Ethereum Signed Message:\n32", hash)
        );
    }

    function recover(bytes32 hash, bytes calldata signature)
        internal
        pure
        returns (address)
    {
        require(signature.length == 65, "ECDSA: invalid sig length");

        bytes32 r;
        bytes32 s;
        uint8 v;

        // signature layout: r (32) | s (32) | v (1)
        // calldata is tightly packed; use assembly to extract
        assembly {
            r := calldataload(signature.offset)
            s := calldataload(add(signature.offset, 32))
            v := byte(0, calldataload(add(signature.offset, 64)))
        }

        // Normalize v in {27,28}
        if (v < 27) {
            v += 27;
        }
        require(v == 27 || v == 28, "ECDSA: invalid v");

        // Perform ecrecover
        address signer = ecrecover(hash, v, r, s);
        require(signer != address(0), "ECDSA: invalid sig");
        return signer;
    }
}
