require("dotenv").config();
async function main() {
  const hre = require("hardhat");
  const { CONSUMER_ADDR } = process.env;
  const round = process.env.ROUND;
  if (!CONSUMER_ADDR) throw new Error("Missing CONSUMER_ADDR in .env");
  if (!round) throw new Error("Set ROUND env var (export ROUND=0x...)");

  const consumer = await hre.ethers.getContractAt("ConsumerDemo", CONSUMER_ADDR);
  const t = await consumer.ticket(round);
  console.log("ticket(roundId):", t);
}
main().catch((e)=>{ console.error(e); process.exit(1); });
