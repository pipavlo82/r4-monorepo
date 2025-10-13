require("dotenv").config();
async function main() {
  const hre = require("hardhat");
  const c = await hre.ethers.getContractAt("ConsumerDemo", process.env.CONSUMER_ADDR);
  const ev = await c.queryFilter("RandomnessFulfilled", 0, "latest");
  if (!ev.length) throw new Error("No events yet");
  const rid = ev.at(-1).args.roundId;
  console.log("last roundId:", rid);
  const t = await c.ticket(rid);
  console.log("ticket(roundId):", t);
}
main().catch(e=>{ console.error(e); process.exit(1); });
