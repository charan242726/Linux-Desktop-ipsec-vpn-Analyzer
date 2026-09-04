import { network } from "hardhat";
import { keccak256, toHex } from "viem";

const CONTRACT_ADDRESS = "0x5fbdb2315678afecb367f032d93f642f64180aa3";

const REPORT_ID = "REPORT-ASSESS-capture";

const REPORT_HASH =
  "e173e851e06cb7ee8bc2993355acaf2b81a3220237b785b4457cffa87c5c4335";

const { viem } = await network.create();

const registry = await viem.getContractAt(
  "VpnAssessmentRegistry",
  CONTRACT_ADDRESS
);

// Convert the SHA-256 hexadecimal string into bytes32.
const reportHash = `0x${REPORT_HASH}` as `0x${string}`;

const tx = await registry.write.registerAssessment([
  REPORT_ID,
  reportHash,
]);

console.log("Assessment registered.");
console.log(`Report ID: ${REPORT_ID}`);
console.log(`SHA-256: ${REPORT_HASH}`);
console.log(`Transaction hash: ${tx}`);
