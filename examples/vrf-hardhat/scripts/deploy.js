const hre = require("hardhat");
async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deployer:", deployer.address);

  const Verifier = await hre.ethers.getContractFactory("MockVerifier");
  const verifier = await Verifier.deploy();
  await verifier.waitForDeployment();
  const verifierAddr = await verifier.getAddress();
  console.log("MockVerifier:", verifierAddr);

  const Consumer = await hre.ethers.getContractFactory("ConsumerDemo");
  const consumer = await Consumer.deploy(verifierAddr);
  await consumer.waitForDeployment();
  const consumerAddr = await consumer.getAddress();
  console.log("ConsumerDemo:", consumerAddr);
}
main().catch((e)=>{ console.error(e); process.exit(1); });
