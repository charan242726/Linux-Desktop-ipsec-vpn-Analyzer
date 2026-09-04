import { network } from "hardhat";

const { viem } = await network.create();

const registry = await viem.deployContract("VpnAssessmentRegistry");

console.log("VpnAssessmentRegistry deployed.");
console.log(`Contract address: ${registry.address}`);
