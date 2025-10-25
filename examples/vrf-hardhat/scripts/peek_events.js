require("dotenv").config();
async function main() {
  const hre = require("hardhat");
  const c = await hre.ethers.getContractAt("ConsumerDemo", process.env.CONSUMER_ADDR);
  const ev = await c.queryFilter("RandomnessFulfilled", 0, "latest");
  for (const e of ev.slice(-5)) {
    const { roundId, randomness, proof, ticket } = e.args;
    console.log({ roundId, ticket, tx: e.transactionHash });
  }
}
main().catch(e=>{ console.error(e); process.exit(1); });
