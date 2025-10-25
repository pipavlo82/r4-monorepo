require("dotenv").config();
require("@nomicfoundation/hardhat-toolbox");

const { SEPOLIA_RPC_URL, PRIVATE_KEY } = process.env;

const networks = {
  localhost: { url: "http://127.0.0.1:8545" },
};

if (SEPOLIA_RPC_URL && PRIVATE_KEY && /^0x[0-9a-fA-F]{64}$/.test(PRIVATE_KEY)) {
  networks.sepolia = { url: SEPOLIA_RPC_URL, accounts: [PRIVATE_KEY] };
}

module.exports = { solidity: "0.8.24", networks };
