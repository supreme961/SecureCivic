// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.28;

import {LandRegistry} from "./LandRegistry.sol";
import {Test} from "forge-std/Test.sol";

contract LandRegistryTest is Test {
  LandRegistry registry;

  function setUp() public {
    registry = new LandRegistry();
  }

  function testApproveMutationEmitsEventAndBlocksDuplicates() public {
    vm.expectEmit(true, false, false, true);
    emit LandRegistry.MutationCompleted("REQ-2026-001");

    registry.approveMutation("REQ-2026-001");

    vm.expectRevert("Mutation already processed!");
    registry.approveMutation("REQ-2026-001");
  }
}