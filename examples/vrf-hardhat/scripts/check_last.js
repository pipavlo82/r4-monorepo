const hre = require("hardhat");

(async () => {
  const bn = await hre.ethers.provider.getBlockNumber();
  console.log("latest block:", bn);

  const addr = process.env.CONSUMER_ADDR;
  if (!addr) throw new Error("CONSUMER_ADDR missing in .env");
  const c = await hre.ethers.getContractAt("ConsumerDemo", addr);

  // знайдемо останні події RandomnessFulfilled за ~50 блоків
  const logs = await c.queryFilter(c.filters.RandomnessFulfilled(), Math.max(0, bn - 50), bn);
  if (logs.length === 0) {
    console.log("No RandomnessFulfilled events in last 50 blocks.");
    return;
  }

  const last = logs[logs.length - 1];
  const { roundId, ticket } = last.args;
  console.log("last roundId :", roundId);
  console.log("ticket       :", ticket);

  // продемонструємо читання мапи ticket(roundId)
  const stored = await c.ticket(roundId);
  console.log("ticket(roundId) from contract:", stored);
})();
