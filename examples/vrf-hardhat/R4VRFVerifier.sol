// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title R4VRFVerifier
/// @notice Verifies that a randomness sample from the R4PQ node
///         was actually signed by the trusted R4 signer using ECDSA(secp256k1).
///
/// @dev Workflow:
///  1. Off-chain you call the R4PQ node `/random_pq?sig=ecdsa`
///     You get JSON like:
///       {
///         "random": 2642708918,
///         "timestamp": "2025-10-28T02:34:49Z",
///         "signature_type": "ECDSA(secp256k1)",
///         "sig_b64": "...",
///         "pubkey_b64": "...",
///         "hash_alg": "SHA-256",
///         "pq_mode": false
///       }
///
///  2. Off-chain you:
///     - base64-decode sig_b64 → 65-byte {r(32)|s(32)|v(1)} or {r|s} and compute v
///     - compute messageHash = sha256( abi.encodePacked(random, timestamp) )
///     - recover signer = ecrecover(messageHash, v, r, s)
///     - ensure signer == R4_SIGNER_ADDRESS
///
///  3. On-chain, you can store the same tuple (random, timestamp, v, r, s)
///     and call verify(...) to prove it's legit.
///
/// @notice This contract does NOT generate randomness. It only verifies
///         that the randomness + timestamp were signed by the known R4 node.
///         Dilithium / PQ will be a different path (can't ecrecover PQ).
contract R4VRFVerifier {
    /// @dev The Ethereum-style address that represents the trusted R4 signer.
    /// This MUST be computed off-chain from the R4 node's public key.
    /// You hardcode it here after onboarding the node.
    address public immutable R4_SIGNER_ADDRESS;

    constructor(address _signer) {
        require(_signer != address(0), "bad signer");
        R4_SIGNER_ADDRESS = _signer;
    }

    /// @notice Verifies that (`randomNumber`,`timestampIso`) was signed
    ///         by R4_SIGNER_ADDRESS using ECDSA(secp256k1).
    ///
    /// @param randomNumber The `random` field from /random_pq (uint32 in your API, but we accept uint256)
    /// @param timestampIso The `timestamp` field from /random_pq (ISO8601 string, e.g. "2025-10-28T02:34:49Z")
    /// @param v ECDSA recovery id (27/28 or 0/1 normalized to 27/28)
    /// @param r ECDSA signature R
    /// @param s ECDSA signature S
    ///
    /// @return valid true if signature matches and signer is trusted
    function verify(
        uint256 randomNumber,
        string memory timestampIso,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) public view returns (bool valid) {
        // 1. Rebuild the exact message payload that was signed.
        // The backend says it uses SHA-256.
        // Solidity has sha256(...) which returns bytes32.
        bytes32 msgHash = sha256(
            abi.encodePacked(
                randomNumber,
                timestampIso
            )
        );

        // 2. Recover signer with ecrecover.
        // NOTE: ecrecover in Ethereum expects the "Ethereum Signed Message" prefix
        // if you're doing personal_sign-style hashing.
        //
        // IMPORTANT:
        // We are NOT doing the prefix here. We assume the backend signed the raw 32-byte sha256 hash.
        // So the backend MUST sign EXACTLY sha256(abi.encodePacked(random, timestamp))
        // with no "\x19Ethereum Signed Message:\n32" prefix.
        //
        // If your signer *does* prepend that Ethereum prefix, then you must mirror that here.
        address recovered = ecrecover(msgHash, v, r, s);

        // 3. Compare.
        return (recovered == R4_SIGNER_ADDRESS);
    }

    /// @notice Convenience helper: returns the recovered signer address
    ///         for inspection / debugging / for off-chain tooling.
    function recoveredSigner(
        uint256 randomNumber,
        string memory timestampIso,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) public pure returns (address) {
        bytes32 msgHash = sha256(
            abi.encodePacked(
                randomNumber,
                timestampIso
            )
        );
        return ecrecover(msgHash, v, r, s);
    }
}
