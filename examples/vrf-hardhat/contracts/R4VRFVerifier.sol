// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract R4VRFVerifier {
    function verify(
        bytes32 msgHash,
        uint8 v,
        bytes32 r,
        bytes32 s,
        address signer
    ) public pure returns (bool) {
        uint8 vv = v;
        // ecrecover очікує 27/28; якщо подано 0/1 — додаємо 27
        if (vv < 27) {
            vv += 27;
        } else if (vv > 28) {
            return false; // неприйнятний v
        }
        address rec = ecrecover(msgHash, vv, r, s);
        return rec == signer;
    }
}
