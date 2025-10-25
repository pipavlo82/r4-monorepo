// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IVRFProvider {
    function requestRandom(bytes32 alpha) external returns (bytes32 requestId);
    function fulfill(bytes32 requestId, bytes calldata proof, bytes32 beta) external;
}

contract VRFConsumer {
    bytes32 public lastBeta;
    event VRFReceived(bytes32 indexed requestId, bytes32 beta);
    function onVRF(bytes32 requestId, bytes32 beta) external {
        lastBeta = beta;
        emit VRFReceived(requestId, beta);
    }
}
