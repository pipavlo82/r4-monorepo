// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @notice Canonical verifier for R4 randomness feed (/random_pq?sig=ecdsa).
/// It validates that randomness+timestamp were signed by the R4 node.
///
/// Node returns JSON:
/// {
///   "random": 3318794722,
///   "timestamp": "2025-10-28T03:14:13Z",
///   "v": 28,
///   "r": "0x8b40c944cca0eed4a7065c2564331b24889604f69043995359e31b4a914905b8",
///   "s": "0xd19ce9fa6452595fcbb9e1060d528d366b9c9b40b62cc5749e91989a609ef8f1",
///   "signer_addr": "0xd78F471F7fe1C85A6Abc41309D56980BDfE5e30F"
/// }
///
/// The node signs sha256( randomNumber || timestampIso ) where:
/// - randomNumber encoded as uint256 big-endian
/// - timestampIso encoded as the ASCII bytes of the string.
///
/// We reproduce that same hash, ecrecover, and compare address.
contract R4VRFVerifierCanonical {
    address public immutable R4_SIGNER_ADDRESS;

    constructor(address _signer) {
        require(_signer != address(0), "bad signer");
        R4_SIGNER_ADDRESS = _signer;
    }

    function verify(
        uint256 randomNumber,
        string memory timestampIso,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) public view returns (bool) {
        bytes32 msgHash = sha256(
            abi.encodePacked(
                randomNumber,
                timestampIso
            )
        );
        address recovered = ecrecover(msgHash, v, r, s);
        return (recovered == R4_SIGNER_ADDRESS);
    }

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
