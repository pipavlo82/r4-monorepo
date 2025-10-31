const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("LotteryR4", function () {
  it("picks a deterministic fair winner using verified randomness", async function () {
    const [signer, a, b, c] = await ethers.getSigners();

    const Ver = await ethers.getContractFactory("R4VRFVerifier");
    const ver = await Ver.deploy();

    const Lot = await ethers.getContractFactory("LotteryR4");
    const lot = await Lot.deploy(signer.address, await ver.getAddress());

    // три гравці
    await lot.connect(a).join();
    await lot.connect(b).join();
    await lot.connect(c).join();

    // randomness (32 байти) + EIP-191 підпис від trustedSigner
    const randomness = ethers.toBeHex(987654321n, 32);
    const sig = await signer.signMessage(ethers.getBytes(randomness));

    await lot.drawWinner(randomness, sig);

    const winner = await lot.lastWinner();
    // очікуємо конкретного переможця — інваріант детермінований randomness-ом.
    const idx = Number(ethers.toBigInt(ethers.keccak256(randomness)) % 3n);
    const addrs = [a.address, b.address, c.address];
    expect(winner).to.equal(addrs[idx]);
  });

  it("reverts if signature is invalid", async function () {
    const [signer, attacker] = await ethers.getSigners();

    const Ver = await ethers.getContractFactory("R4VRFVerifier");
    const ver = await Ver.deploy();

    const Lot = await ethers.getContractFactory("LotteryR4");
    const lot = await Lot.deploy(signer.address, await ver.getAddress());

    await lot.connect(attacker).join(); // має бути хоч один гравець

    const randomness = ethers.toBeHex(111222333n, 32);

    // НЕправильний підпис — підписує не trustedSigner
    const badSig = await attacker.signMessage(ethers.getBytes(randomness));

    await expect(lot.drawWinner(randomness, badSig))
      .to.be.revertedWithCustomError(lot, "InvalidRandomnessSignature");
  });
});
