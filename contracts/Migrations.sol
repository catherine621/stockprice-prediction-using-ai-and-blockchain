// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Migrations {
    address public owner;
    uint256 public last_completed_migration;

    constructor() {
        owner = msg.sender;
    }

    function setCompleted(uint256 completed) public {
        require(msg.sender == owner, "Only owner can set");
        last_completed_migration = completed;
    }
}
