import { readFileSync } from "fs";
import { ethers } from "ethers";

const N    = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141n;
const HALF = N >> 1n;

function normalizeSigVRS(v, r, s) {
  let vv = Number(v), rr = r, ss = s;
  let sB = BigInt(ss);
  if (sB > HALF) {
    sB = N - sB;
    ss = "0x" + sB.toString(16).padStart(64, "0");
    vv = (vv === 27 || vv === 28) ? (vv === 27 ? 28 : 27) : (vv ^ 1);
  }
  return { v: vv, r: rr, s: ss };
}

const j = JSON.parse(readFileSync(process.argv[2] || "/tmp/vrf.json", "utf8"));
const { v, r, s } = normalizeSigVRS(j.v, j.r, j.s);
const sig = ethers.Signature.from({ v, r, s });
const recovered = ethers.recoverAddress(j.msg_hash, sig);

console.log(JSON.stringify({
  expected: j.signer_addr,
  recovered,
  ok: recovered.toLowerCase() === j.signer_addr.toLowerCase()
}, null, 2));
