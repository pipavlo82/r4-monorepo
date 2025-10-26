const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("R4VRFVerifier", function () {
  it("verifies a valid signature from the signer", async () => {
    // Get a test signer (acts as Re4ctoR off-chain signer)
    const [signer, attacker] = await ethers.getSigners();

    // Deploy contract
    const Factory = await ethers.getContractFactory("R4VRFVerifier");
    const vrf = await Factory.deploy();
    await vrf.waitForDeployment();

    // Simulate randomness value returned by Re4ctoR API: 32 bytes
    // We use keccak256("demo") just to have a deterministic bytes32.
    const randomness = ethers.keccak256(ethers.toUtf8Bytes("demo"));

    // Off-chain service would sign keccak256(randomness),
    // then prefix with "\x19Ethereum Signed Message:\n32".
    // In ethers v6, signMessage() does *exactly* that prefixing.
    const msgHash = ethers.keccak256(
      ethers.AbiCoder.defaultAbiCoder().encode(["bytes32"], [randomness])
    );
    const rawSig = await signer.signMessage(ethers.getBytes(msgHash));

    // Ask contract to verify
    const ok = await vrf.verify(randomness, rawSig, await signer.getAddress());
    expect(ok).to.equal(true);

    // sanity check: attacker should fail
    const bad = await vrf.verify(randomness, rawSig, await attacker.getAddress());
    expect(bad).to.equal(false);
  });

  it("emits event on submitRandom()", async () => {
    const [caller] = await ethers.getSigners();

    const Factory = await ethers.getContractFactory("R4VRFVerifier");
    const vrf = await Factory.deploy();
    await vrf.waitForDeployment();

    const randomness = ethers.keccak256(ethers.toUtf8Bytes("demo"));

    await expect(vrf.connect(caller).submitRandom(randomness))
      .to.emit(vrf, "RandomnessVerified")
      .withArgs(await caller.getAddress(), randomness);
  });
});
