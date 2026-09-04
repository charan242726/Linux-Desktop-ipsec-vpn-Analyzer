import { network } from "hardhat";

const CONTRACT_ADDRESS = "0x5fbdb2315678afecb367f032d93f642f64180aa3";

const REPORT_ID = "REPORT-ASSESS-capture";

const REPORT_HASH =
  "e173e851e06cb7ee8bc2993355acaf2b81a3220237b785b4457cffa87c5c4335";

const { viem } = await network.create();

const registry = await viem.getContractAt(
  "VpnAssessmentRegistry",
  CONTRACT_ADDRESS
);

const reportHash = `0x${REPORT_HASH}` as `0x${string}`;

const verified = await registry.read.verifyAssessment([
  REPORT_ID,
  reportHash,
]);

const assessment = await registry.read.getAssessment([
  REPORT_ID,
]);

console.log("Blockchain Verification");
console.log("========================");
console.log(`Report ID: ${REPORT_ID}`);
console.log(`Local SHA-256: ${REPORT_HASH}`);
console.log(`Blockchain Hash: ${assessment[0]}`);
console.log(`Registered At: ${assessment[1]}`);
console.log(`Registered By: ${assessment[2]}`);
console.log(`Exists: ${assessment[3]}`);
console.log(`VERIFIED: ${verified}`);
