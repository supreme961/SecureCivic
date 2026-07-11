"""Integration tests for the SecureCivic FastAPI backend.

The project does not ship pytest in the current environment, so this script
uses the standard library unittest runner and can be executed directly.
"""

from __future__ import annotations

import importlib
import sys
import types
import unittest
from copy import deepcopy
from itertools import count
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException


PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
	sys.path.insert(0, str(PROJECT_DIR))


def _install_fake_web3() -> None:
	if "web3" in sys.modules and getattr(sys.modules["web3"], "__securecivic_test_stub__", False):
		return

	web3_module = types.ModuleType("web3")
	exceptions_module = types.ModuleType("web3.exceptions")

	class ContractLogicError(Exception):
		pass

	class FakeTxCall:
		def __init__(self, function_name: str, request_id: str | None = None):
			self.function_name = function_name
			self.request_id = request_id

		def build_transaction(self, base_tx: dict) -> dict:
			transaction = dict(base_tx)
			transaction["function_name"] = self.function_name
			transaction["request_id"] = self.request_id
			transaction["gas"] = transaction.get("gas", 21000)
			return transaction

	class FakeFunctions:
		def __init__(self):
			self.approved_request_ids: list[str] = []

		def approveMutation(self, request_id: str) -> FakeTxCall:
			self.approved_request_ids.append(request_id)
			return FakeTxCall("approveMutation", request_id)

		def registerLand(self, asset_id: int, location: str, area: int) -> FakeTxCall:
			return FakeTxCall("registerLand", str(asset_id))

	class FakeContract:
		def __init__(self):
			self.functions = FakeFunctions()

	class FakeSignedTransaction:
		raw_transaction = b"raw-transaction-bytes"

	class FakeAccount:
		address = "0xB4A1000000000000000000000000000000009C22"

		def sign_transaction(self, tx_payload: dict) -> FakeSignedTransaction:
			self.last_signed_transaction = tx_payload
			return FakeSignedTransaction()

	class FakeAccountNamespace:
		def from_key(self, private_key: str) -> FakeAccount:
			account = FakeAccount()
			account.private_key = private_key
			return account

	class FakeEth:
		def __init__(self):
			self.accounts = [FakeAccount.address]
			self.account = FakeAccountNamespace()
			self.default_account = None
			self.chain_id = 31337
			self.gas_price = 1
			self.contract_instance = FakeContract()
			self.last_raw_transaction = None

		def contract(self, address=None, abi=None):
			return self.contract_instance

		def get_transaction_count(self, address: str) -> int:
			return 1

		def estimate_gas(self, base_tx: dict) -> int:
			return 21000

		def send_raw_transaction(self, raw_transaction: bytes) -> bytes:
			self.last_raw_transaction = raw_transaction
			return bytes.fromhex("12" * 32)

		def wait_for_transaction_receipt(self, tx_hash: bytes):
			return SimpleNamespace(status=1, blockNumber=123)

	class FakeHTTPProvider:
		def __init__(self, *args, **kwargs):
			self.args = args
			self.kwargs = kwargs

	class FakeWeb3:
		__securecivic_test_stub__ = True

		HTTPProvider = FakeHTTPProvider

		def __init__(self, provider):
			self.provider = provider
			self.eth = FakeEth()

	web3_module.Web3 = FakeWeb3
	exceptions_module.ContractLogicError = ContractLogicError
	web3_module.exceptions = exceptions_module

	sys.modules["web3"] = web3_module
	sys.modules["web3.exceptions"] = exceptions_module


_install_fake_web3()
main = importlib.import_module("main")


class SecureCivicIntegrationTests(unittest.TestCase):
	def setUp(self) -> None:
		self.original_assets = deepcopy(main.assets_db)
		self.original_requests = deepcopy(main.requests_db)
		self.original_audit_logs = deepcopy(main.audit_logs)

		main.assets_db[:] = deepcopy(self.original_assets)
		main.requests_db[:] = deepcopy(self.original_requests)
		main.audit_logs[:] = deepcopy(self.original_audit_logs)
		main.request_sequence = count(1)

	def tearDown(self) -> None:
		main.assets_db[:] = self.original_assets
		main.requests_db[:] = self.original_requests
		main.audit_logs[:] = self.original_audit_logs
		main.request_sequence = count(1)

	def create_citizen_request(self) -> dict:
		payload = main.MutationRequest(
			asset_id="PROP-2026-900",
			owner_name="Shrestha Devi",
			property_type="Residential",
			area="1850000",
			location="Sector 21, New Delhi",
		)
		response = main.create_mutation_request(payload)
		self.assertTrue(response["success"])
		return response["request"]

	def test_citizen_workflow_submits_new_land_request(self) -> None:
		initial_count = len(main.requests_db)

		request_record = self.create_citizen_request()

		self.assertEqual(len(main.requests_db), initial_count + 1)
		self.assertEqual(request_record["status"], "Pending")
		self.assertEqual(request_record["asset_id"], "PROP-2026-900")
		self.assertEqual(request_record["owner_name"], "Shrestha Devi")

	def test_registrar_workflow_approves_request_and_triggers_blockchain_mutation(self) -> None:
		request_record = self.create_citizen_request()
		request_id = request_record["request_id"]

		fake_account = SimpleNamespace(
			address="0xB4A1000000000000000000000000000000009C22",
			sign_transaction=lambda tx_payload: SimpleNamespace(raw_transaction=b"signed-tx"),
		)

		with patch.object(main, "get_registrar_account", return_value=(fake_account, main.DEFAULT_HARDHAT_PRIVATE_KEY)):
			response = main.registrar_action(
				request_id,
				main.ApprovalAction(status="Approved", comments="Approved from test."),
			)

		self.assertEqual(response["request"]["status"], "Approved")
		self.assertTrue(response["blockchain_tx_hash"])
		self.assertIn(request_id, main.contract.functions.approved_request_ids)

	def test_unauthorized_role_action_is_blocked(self) -> None:
		request_record = self.create_citizen_request()
		request_id = request_record["request_id"]

		def deny_registrar_access():
			raise HTTPException(status_code=403, detail="Unauthorized role")

		with patch.object(main, "get_registrar_account", side_effect=deny_registrar_access):
			with self.assertRaises(HTTPException) as raised:
				main.registrar_action(
					request_id,
					main.ApprovalAction(status="Approved", comments="Attempted by unauthorized role."),
				)

		self.assertEqual(raised.exception.status_code, 403)
		self.assertEqual(raised.exception.detail, "Unauthorized role")

	def test_duplicate_request_state_transition_returns_400(self) -> None:
		request_record = self.create_citizen_request()
		request_id = request_record["request_id"]

		fake_account = SimpleNamespace(
			address="0xB4A1000000000000000000000000000000009C22",
			sign_transaction=lambda tx_payload: SimpleNamespace(raw_transaction=b"signed-tx"),
		)

		with patch.object(main, "get_registrar_account", return_value=(fake_account, main.DEFAULT_HARDHAT_PRIVATE_KEY)):
			first_response = main.registrar_action(
				request_id,
				main.ApprovalAction(status="Approved", comments="Initial approval."),
			)

		self.assertEqual(first_response["request"]["status"], "Approved")

		with self.assertRaises(HTTPException) as raised:
			main.registrar_action(
				request_id,
				main.ApprovalAction(status="Approved", comments="Duplicate approval."),
			)

		self.assertEqual(raised.exception.status_code, 400)
		self.assertIn("already been processed", raised.exception.detail)


if __name__ == "__main__":
	unittest.main(verbosity=2)
