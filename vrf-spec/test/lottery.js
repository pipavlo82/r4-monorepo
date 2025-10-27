const { expect } = require("chai");
const { ethers } = require("hardhat");

// helper: produce randomness + signature like Re4ctoR would
async function generateSignedRandomness(signerWallet, seedText = "demo-seed") {
  // randomness is just keccak256("demo-seed") for reproducibility here
  const randomness = ethers.keccak256(ethers.toUtf8Bytes(seedText));

  // off-chain node behavior:
  // sign keccak256(randomness) using Ethereum personal_sign semantics
  const msgHash = ethers.keccak256(
    ethers.AbiCoder.defaultAbiCoder().encode(["bytes32"], [randomness])
  );

  const signature = await signerWallet.signMessage(ethers.getBytes(msgHash));

  return { randomness, signature };
}

describe("LotteryR4", function () {
  it("picks a deterministic fair winner using verified randomness", async function () {
    const [re4Node, playerA, playerB, playerC] = await ethers.getSigners();

    // 1. Deploy verifier (R4VRFVerifier)
    const VerifierFactory = await ethers.getContractFactory("R4VRFVerifier");
    const verifier = await VerifierFactory.deploy();
    await verifier.waitForDeployment();

    // 2. Deploy lottery with reference to verifier + trusted signer
    const LotteryFactory = await ethers.getContractFactory("LotteryR4");
    const lottery = await LotteryFactory.deploy(
      await verifier.getAddress(),
      await re4Node.getAddress() // trustedSigner = our "Re4ctoR node"
    );
    await lottery.waitForDeployment();

    // 3. players join the lottery
    await lottery.connect(playerA).enterLottery();
    await lottery.connect(playerB).enterLottery();
    await lottery.connect(playerC).enterLottery();

    // sanity check
    expect(await lottery.playerCount()).to.equal(3);
    expect(await lottery.getPlayer(0)).to.equal(await playerA.getAddress());
    expect(await lottery.getPlayer(1)).to.equal(await playerB.getAddress());
    expect(await lottery.getPlayer(2)).to.equal(await playerC.getAddress());

    // 4. generate randomness + signature exactly like re4Node would
    const { randomness, signature } = await generateSignedRandomness(re4Node, "seed-123");

    // 5. call drawWinner with that randomness + signature
    const tx = await lottery.drawWinner(randomness, signature);

    // 6. expect WinnerSelected event with correct index
    const receipt = await tx.wait();
    const ev = receipt.logs
      .map(log => {
        try { return lottery.interface.parseLog(log); } catch { return null; }
      })
      .filter(x => x && x.name === "WinnerSelected")[0];

    expect(ev).to.not.equal(undefined);

    // winnerIndex = uint256(randomness) % players.length
    const computedIndex =
      BigInt(randomness) % BigInt(3); // 3 players

    // event args: (winner, index, randomness)
    const winnerEmitted = ev.args[0];
    const idxEmitted = ev.args[1];
    const randomnessEmitted = ev.args[2];

    // check index math matches contract logic
    expect(idxEmitted).to.equal(computedIndex);

    // check randomness passed through
    expect(randomnessEmitted).to.equal(randomness);

    // check that winner is actually players[idx]
    const expectedWinner = await lottery.getPlayer(Number(computedIndex));
    expect(winnerEmitted).to.equal(expectedWinner);
  });

  it("reverts if signature is invalid", async function () {
    const [re4Node, attacker, p1] = await ethers.getSigners();

    // Deploy verifier
    const VerifierFactory = await ethers.getContractFactory("R4VRFVerifier");
    const verifier = await VerifierFactory.deploy();
    await verifier.waitForDeployment();

    // Deploy lottery (trustedSigner = re4Node)
    const LotteryFactory = await ethers.getContractFactory("LotteryR4");
    const lottery = await LotteryFactory.deploy(
      await verifier.getAddress(),
      await re4Node.getAddress()
    );
    await lottery.waitForDeployment();

    // player joins
    await lottery.connect(p1).enterLottery();

    // attacker forges randomness+sig but signs with WRONG key
    const { randomness, signature } = await generateSignedRandomness(attacker, "fake-seed");

    // should revert because signature doesn't match trustedSigner
    await expect(
      lottery.drawWinner(randomness, signature)
    ).to.be.revertedWith("invalid randomness signature");
  });
});
