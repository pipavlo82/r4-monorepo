const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("R4VRFVerifierCanonical", function () {
  it("verifies live randomness from the R4 node exactly", async function () {
    // This is from your curl:
    // "signer_addr": "0xd78F471F7fe1C85A6Abc41309D56980BDfE5e30F"
    const signerAddr = "0xd78F471F7fe1C85A6Abc41309D56980BDfE5e30F";

    // Deploy canonical verifier with signerAddr in constructor
    const Canon = await ethers.getContractFactory("R4VRFVerifierCanonical");
    const vrf = await Canon.deploy(signerAddr);
    // ethers v6 => no vrf.deployed() call

    // Paste direct values from /random_pq?sig=ecdsa:
    //
    // {
    //   "random": 3318794722,
    //   "timestamp": "2025-10-28T03:14:13Z",
    //   "v": 28,
    //   "r": "0x8b40c944cca0eed4a7065c2564331b24889604f69043995359e31b4a914905b8",
    //   "s": "0xd19ce9fa6452595fcbb9e1060d528d366b9c9b40b62cc5749e91989a609ef8f1"
    // }

    const randomNumber = 3318794722n;
    const timestampIso = "2025-10-28T03:14:13Z";

    const v = 28;
    const r = "0x8b40c944cca0eed4a7065c2564331b24889604f69043995359e31b4a914905b8";
    const s = "0xd19ce9fa6452595fcbb9e1060d528d366b9c9b40b62cc5749e91989a609ef8f1";

    // contract recomputes sha256(random||timestamp) onchain, ecrecover()s it,
    // and checks that the signer matches signerAddr
    const ok = await vrf.verify(randomNumber, timestampIso, v, r, s);
    expect(ok).to.equal(true);

    // bonus sanity: recoveredSigner() should literally equal signerAddr
    const recovered = await vrf.recoveredSigner(randomNumber, timestampIso, v, r, s);
    expect(recovered).to.equal(signerAddr);
  });
});
