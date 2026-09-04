import hardhatViem from "@nomicfoundation/hardhat-viem";
import { defineConfig } from "hardhat/config";

export default defineConfig({
  plugins: [hardhatViem],

  solidity: {
    version: "0.8.20",
  },

  networks: {
    hardhatOp: {
      type: "edr-simulated",
      chainType: "l1",
    },

    localhost: {
      type: "http",
      chainType: "l1",
      url: "http://127.0.0.1:8545",
    },
  },
});
