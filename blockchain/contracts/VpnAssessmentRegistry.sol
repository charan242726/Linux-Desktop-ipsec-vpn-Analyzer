// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title VpnAssessmentRegistry
 * @notice Stores SHA-256 hashes of VPN security assessment reports.
 *
 * Only the report hash and minimal metadata are stored on-chain.
 * PCAP files and sensitive VPN information remain off-chain.
 */
contract VpnAssessmentRegistry {
    struct Assessment {
        bytes32 reportHash;
        uint256 registeredAt;
        address registeredBy;
        bool exists;
    }

    mapping(string => Assessment) private assessments;

    event AssessmentRegistered(
        string indexed reportId,
        bytes32 indexed reportHash,
        address indexed registeredBy,
        uint256 registeredAt
    );

    function registerAssessment(
        string calldata reportId,
        bytes32 reportHash
    ) external {
        require(bytes(reportId).length > 0, "Report ID required");
        require(reportHash != bytes32(0), "Report hash required");
        require(!assessments[reportId].exists, "Assessment already registered");

        assessments[reportId] = Assessment({
            reportHash: reportHash,
            registeredAt: block.timestamp,
            registeredBy: msg.sender,
            exists: true
        });

        emit AssessmentRegistered(
            reportId,
            reportHash,
            msg.sender,
            block.timestamp
        );
    }

    function verifyAssessment(
        string calldata reportId,
        bytes32 reportHash
    ) external view returns (bool) {
        Assessment memory assessment = assessments[reportId];

        if (!assessment.exists) {
            return false;
        }

        return assessment.reportHash == reportHash;
    }

    function getAssessment(
        string calldata reportId
    )
        external
        view
        returns (
            bytes32 reportHash,
            uint256 registeredAt,
            address registeredBy,
            bool exists
        )
    {
        Assessment memory assessment = assessments[reportId];

        return (
            assessment.reportHash,
            assessment.registeredAt,
            assessment.registeredBy,
            assessment.exists
        );
    }
}
