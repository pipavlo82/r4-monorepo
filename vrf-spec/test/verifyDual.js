const { expect } = require("chai");
const { ethers } = require("hardhat");

// Підпис raw keccak256(randomness): використовуємо ethers v6 SigningKey
function signRawDigestSync(privateKey, digestHex) {
  const { SigningKey, Signature } = ethers;
  const sk = new SigningKey(privateKey);
  const sig = sk.sign(digestHex); // digestHex = 0x + 32 байт
  return Signature.from(sig).serialized; // 0x r s v
}

describe("R4VRFVerifier (raw digest)", function () {
  it("verifies ECDSA(secp256k1) over keccak256(randomness)", async function () {
    const Ver = await ethers.getContractFactory("R4VRFVerifier");
    const ver = await Ver.deploy();

    // генеруємо окремий ключ (офчейн-сервіс)
    const wallet = ethers.Wallet.createRandom();

    const randomness = ethers.toBeHex(123456789n, 32);
    const digest = ethers.keccak256(randomness); // 0x + 32

    const sig = signRawDigestSync(wallet.privateKey, digest);
    const ok = await ver.verifyRaw(randomness, sig, wallet.address);
    expect(ok).to.equal(true);
  });
});
