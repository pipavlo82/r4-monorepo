// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./R4VRFVerifier.sol";

/// @title LotteryR4
/// @notice Minimal provably-fair lottery that uses Re4ctoR randomness.
/// @dev Flow:
///  1. Off-chain Re4ctoR node generates randomness (bytes32) and signature.
///  2. This contract (via R4VRFVerifier) checks that signature really came from trusted signer.
///  3. We pick a winner index based on that randomness.
///  4. We emit an event so the draw is public / auditable.
///
/// This is *not* custody/payout logic. It's the fairness core.
///
/// SECURITY NOTE:
/// - This demo assumes players are known and stored in contract state.
/// - Production version would include anti-sybil rules, entry fees, etc.
contract LotteryR4 {
    R4VRFVerifier public verifier;
    address public trustedSigner; // address of the Re4ctoR signer we trust
    address[] public players;

    event PlayerEntered(address indexed player);
    event WinnerSelected(address indexed winner, uint256 indexed index, bytes32 randomness);

    constructor(address _verifier, address _trustedSigner) {
        verifier = R4VRFVerifier(_verifier);
        trustedSigner = _trustedSigner;
    }

    /// @notice Add a player to the lottery pool.
    /// @dev demo only; no payment checks etc.
    function enterLottery() external {
        players.push(msg.sender);
        emit PlayerEntered(msg.sender);
    }

    /// @notice How many players currently in pool.
    function playerCount() external view returns (uint256) {
        return players.length;
    }

    /// @notice Returns player address by index.
    function getPlayer(uint256 idx) external view returns (address) {
        return players[idx];
    }

    /// @notice Draw winner using off-chain randomness from Re4ctoR.
    /// @param randomness 32-byte randomness provided by Re4ctoR.
    /// @param signature Signature over `randomness` from trustedSigner.
    ///
    /// Requirements:
    /// - At least 1 player must have joined.
    /// - Signature must be valid (checked via verifier.verify()).
    ///
    /// Emits WinnerSelected(winnerAddress, winnerIndex, randomness)
    function drawWinner(bytes32 randomness, bytes calldata signature) external {
        require(players.length > 0, "no players");

        // 1. Verify that randomness was signed by trustedSigner via Re4ctoR VRF verifier
        bool ok = verifier.verify(randomness, signature, trustedSigner);
        require(ok, "invalid randomness signature");

        // 2. Compute deterministic winner index
        //    cast randomness -> uint256, mod player count
        uint256 winnerIndex = uint256(randomness) % players.length;
        address winner = players[winnerIndex];

        // 3. Emit event for auditability / off-chain payout logic
        emit WinnerSelected(winner, winnerIndex, randomness);

        // 4. OPTIONAL (not doing in MVP):
        //    - transfer prize
        //    - reset pool / remove winner
        //    - etc.
    }
}
