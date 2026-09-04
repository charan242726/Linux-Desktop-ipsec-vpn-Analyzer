import { network } from "hardhat";

const REPORT_ID = process.env.REPORT_ID;
const REPORT_HASH = process.env.REPORT_HASH;
const CONTRACT_ADDRESS = process.env.VPN_REGISTRY_ADDRESS;

if (!REPORT_ID) {
  throw new Error("REPORT_ID is required");
}

if (!REPORT_HASH) {
  throw new Error("REPORT_HASH is required");
}

if (!CONTRACT_ADDRESS) {
  throw new Error("VPN_REGISTRY_ADDRESS is required");
}

const { viem } = await network.create();

const registry = await viem.getContractAt(
  "VpnAssessmentRegistry",
  CONTRACT_ADDRESS as `0x${string}`,
);

const publicClient = await viem.getPublicClient();
const [account] = await viem.getWalletClients();

const existing = await registry.read.getAssessment([
  REPORT_ID,
]);

const alreadyRegistered = existing[3];

if (!alreadyRegistered) {
  const txHash = await registry.write.registerAssessment(
    [REPORT_ID, REPORT_HASH as `0x${string}`],
    {
      account: account.account,
    },
  );

  await publicClient.waitForTransactionReceipt({
    hash: txHash,
  });
}

const assessment = await registry.read.getAssessment([
  REPORT_ID,
]);

const blockchainHash = assessment[0];
const registeredAt = assessment[1];
const registeredBy = assessment[2];
const exists = assessment[3];

const verified = await registry.read.verifyAssessment([
  REPORT_ID,
  REPORT_HASH as `0x${string}`,
]);

console.log(
  JSON.stringify(
    {
      report_id: REPORT_ID,
      local_hash: REPORT_HASH,
      blockchain_hash: blockchainHash,
      registered_at: registeredAt.toString(),
      registered_by: registeredBy,
      exists,
      verified,
      contract_address: CONTRACT_ADDRESS,
      status: verified ? "BLOCKCHAIN_VERIFIED" : "BLOCKCHAIN_VERIFICATION_FAILED",
    },
    null,
    2,
  ),
);
