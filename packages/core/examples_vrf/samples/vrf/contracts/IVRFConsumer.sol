// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IVRFConsumer {
    function fulfillRandomness(bytes32 roundId, bytes calldata randomness, bytes calldata proof) external;
}
