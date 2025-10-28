const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("R4VRFVerifier", function () {
  it("verifies live randomness from your R4 node", async function () {
    //
    // 1. signer address comes from curl /random_pq?sig=ecdsa
    //
    const signerAddr = "0xd78F471F7fe1C85A6Abc41309D56980BDfE5e30F";

    // 2. deploy the NEW canonical verifier with that signer addr
    const Verifier = await ethers.getContractFactory("R4VRFVerifier");
    const vrf = await Verifier.deploy(signerAddr);
    // ethers v6: no await vrf.deployed()

    // 3. paste live signed sample from node:
    const randomNumber = 3318794722n;
    const timestampIso = "2025-10-28T03:14:13Z";

    const v = 28;
    const r = "0x8b40c944cca0eed4a7065c2564331b24889604f69043995359e31b4a914905b8";
    const s = "0xd19ce9fa6452595fcbb9e1060d528d366b9c9b40b62cc5749e91989a609ef8f1";

    // 4. call verify() which recomputes sha256(random||timestamp)
    const ok = await vrf.verify(randomNumber, timestampIso, v, r, s);

    expect(ok).to.equal(true);

    // 5. sanity: recoveredSigner() MUST equal signerAddr
    const recovered = await vrf.recoveredSigner(randomNumber, timestampIso, v, r, s);
    expect(recovered).to.equal(signerAddr);
  });
});
