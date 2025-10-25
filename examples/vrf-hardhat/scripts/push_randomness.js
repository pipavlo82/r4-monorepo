process.env.HARDHAT_DISABLE_TELEMETRY = "1";

const hre = require("hardhat");
const { execFileSync } = require("node:child_process");
const { createHash }   = require("node:crypto");
const path             = require("node:path");

function sha256(buf) { return createHash("sha256").update(buf).digest(); }
function hex(buf)    { return Buffer.from(buf).toString("hex"); }

async function main() {
  const consumerAddr = process.env.CONSUMER_ADDR;
  if (!consumerAddr) throw new Error("Set CONSUMER_ADDR in .env");

  const root  = path.resolve(__dirname, "..", "..");
  const r4cat = process.env.R4CAT || path.join(root, "bin", "r4cat");

  // переконатись, що бінарник існує
  execFileSync("bash", ["-lc", `test -x "${r4cat}"`]);

  // 32 байти випадковості
  const rand = execFileSync(r4cat, ["-n", "32"]);

  // Спрощено і «по рядках», щоб не було плутанини з дужками:
  const roundId = "0x" + hex(sha256(rand));
  const ts      = Math.floor(Date.now() / 1000).toString();
  const proof   = sha256(Buffer.concat([rand, Buffer.from(ts)]));

  console.log("roundId   :", roundId);
  console.log("randomness:", rand.toString("hex"));
  console.log("proof     :", proof.toString("hex"));

  const consumer = await hre.ethers.getContractAt("ConsumerDemo", consumerAddr);
  const tx = await consumer.fulfillRandomness(roundId, rand, proof);
  const rcpt = await tx.wait();
  console.log("tx hash   :", rcpt.hash);
}

main()
  .then(() => process.exit(0))
  .catch(e => { console.error(e); process.exit(1); });
