// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./R4VRFVerifier.sol";

/// @title Демолотеpея, що приймає randomness + підпис і визначає переможця
contract LotteryR4 {
    error NoPlayers();
    error InvalidRandomnessSignature();

    R4VRFVerifier public immutable verifier;
    address public immutable trustedSigner;

    address[] public players;
    address public lastWinner;

    constructor(address _trustedSigner, address _verifier) {
        trustedSigner = _trustedSigner;
        verifier = R4VRFVerifier(_verifier);
    }

    function join() external {
        players.push(msg.sender);
    }

    function playersCount() external view returns (uint256) {
        return players.length;
    }

    /// @notice Переможець = keccak256(randomness) % N (повністю детерміновано)
    function drawWinner(bytes32 randomness, bytes calldata signature) external {
        if (players.length == 0) revert NoPlayers();
        bool ok = verifier.verify(randomness, signature, trustedSigner);
        if (!ok) revert InvalidRandomnessSignature();

        uint256 idx = uint256(keccak256(abi.encodePacked(randomness))) % players.length;
        lastWinner = players[idx];
    }
}
