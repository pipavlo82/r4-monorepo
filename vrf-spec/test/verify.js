const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("R4VRFVerifier", function () {
  it("verifies a valid signature from the signer", async function () {
    const [signer] = await ethers.getSigners();
    const Ver = await ethers.getContractFactory("R4VRFVerifier");
    const ver = await Ver.deploy();

    // 32-байтовий randomness
    const randomness = ethers.toBeHex(123n, 32);
    // signMessage робить EIP-191 над саме 32 байтами
    const sig = await signer.signMessage(ethers.getBytes(randomness));

    expect(await ver.verify(randomness, sig, signer.address)).to.equal(true);
  });

  it("emits event on submitRandom()", async function () {
    const [signer, any] = await ethers.getSigners();
    const Ver = await ethers.getContractFactory("R4VRFVerifier");
    const ver = await Ver.deploy();

    const randomness = ethers.toBeHex(456n, 32);
    const sig = await signer.signMessage(ethers.getBytes(randomness));

    await expect(ver.connect(any).submitRandom(randomness, sig, signer.address))
      .to.emit(ver, "RandomnessVerified")
      .withArgs(any.address, randomness);
  });
});
