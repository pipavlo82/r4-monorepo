const { expect } = require("chai");
const fs = require("fs");
const path = require("path");

describe("R4VRFVerifier", function () {
  it("verifies ECDSA (v,r,s) equals signer", async function () {
    const data = JSON.parse(
      fs.readFileSync(path.resolve(__dirname, "../../out_dual_ecdsa.json"), "utf8")
    );

    // Контракт приймає вже ГОТОВИЙ msg_hash (SHA-256), без префіксу!
    const msgHash = data.msg_hash; // bytes32 hex, "0x..."
    const v = data.v;              // 27/28 або 0/1 — контракт нормалізує
    const r = data.r;
    const s = data.s;
    const signer = data.signer_addr;

    const Verifier = await ethers.getContractFactory("R4VRFVerifier");
    const verifier = await Verifier.deploy();
    await verifier.waitForDeployment();

    const ok = await verifier.verify(msgHash, v, r, s, signer);
    expect(ok).to.equal(true);
  });
});
