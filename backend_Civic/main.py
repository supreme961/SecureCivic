from datetime import datetime, timezone
from itertools import count
import os
import tempfile
from pathlib import Path
from typing import Literal
import traceback

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from web3 import Web3
from web3.exceptions import ContractLogicError

DEFAULT_HARDHAT_PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

# 1. Local Hardhat Blockchain se connect karo
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# 2. Jo address hume mila tha deployment par (db786f39-4441-4765-ad5b-5e7094ccdb8c)
contract_address = "0x5FbDB2315678afecb367f032d93F642f64180aa3"

# 3. Aapke LandRegistry contract ki ABI
contract_abi = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "_id", "type": "uint256"},
            {"internalType": "string", "name": "_location", "type": "string"},
            {"internalType": "uint256", "name": "_area", "type": "uint256"}
        ],
        "name": "registerLand",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "name": "lands",
        "outputs": [
            {"internalType": "uint256", "name": "id", "type": "uint256"},
            {"internalType": "string", "name": "location", "type": "string"},
            {"internalType": "uint256", "name": "area", "type": "uint256"},
            {"internalType": "address", "name": "owner", "type": "address"},
            {"internalType": "bool", "name": "isForSale", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# 4. Contract instance banao
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# 5. Tx send karne ke liye default account set karo (Hardhat ka pehla dummy account)
w3.eth.default_account = w3.eth.accounts[0]

def load_backend_environment() -> str | None:
	project_root = Path(__file__).resolve().parent.parent
	search_paths = [
		project_root / ".env",
		project_root.parent / ".env",
		Path.cwd() / ".env",
	]

	for env_path in search_paths:
		if env_path.exists():
			load_dotenv(dotenv_path=env_path)
			return str(env_path)

	load_dotenv()
	return None


loaded_env_path = load_backend_environment()
PINATA_JWT = os.getenv("PINATA_JWT")

if not PINATA_JWT or not PINATA_JWT.strip():
	loaded_from = loaded_env_path or "the default dotenv search path"
	print(
		f"WARNING: PINATA_JWT is missing or empty after loading environment variables from {loaded_from}. "
		"Document uploads will fail until PINATA_JWT is configured."
	)

app = FastAPI(
	title="SecureCivic Land Registry API",
	version="1.0.0",
	description="FastAPI backend for citizen asset mutation and registrar approvals.",
)


# Allow common local frontend development origins without opening the API broadly.
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


class MutationRequest(BaseModel):
	asset_id: str = Field(..., description="Property ID tied to the requested mutation")
	owner_name: str = Field(..., min_length=1, description="Current or intended owner name")
	property_type: str = Field(..., min_length=1, description="Asset category, e.g. Residential or Agricultural")
	area: str = Field(..., min_length=1, description="Parcel size or area description")
	location: str = Field(..., min_length=1, description="Human-readable asset location")


class ApprovalAction(BaseModel):
	status: Literal["Approved", "Rejected"] = Field(..., description="Registrar decision")
	comments: str = Field("", description="Registrar notes for the decision")


class LandRegistrationRequest(BaseModel):
	asset_id: int = Field(..., description="Land asset identifier")
	location: str = Field(..., min_length=1, description="Land location")
	area: int = Field(..., description="Land area")


def utc_now() -> str:
	return datetime.now(timezone.utc).isoformat()


request_sequence = count(1)


def generate_request_id() -> str:
	return f"REQ-2026-{next(request_sequence):03d}"


assets_db = [
	{
		"property_id": "PROP-2026-001",
		"owner_name": "Aarav Sharma",
		"property_type": "Residential",
		"area": "1200 sq ft",
		"location": "Sector 12, New Delhi",
		"status": "Verified",
		"last_updated": utc_now(),
	},
	{
		"property_id": "PROP-2026-002",
		"owner_name": "Meera Iyer",
		"property_type": "Agricultural",
		"area": "2.5 acres",
		"location": "Hosur Road, Karnataka",
		"status": "Pending",
		"last_updated": utc_now(),
	},
]


requests_db = [
	{
		"request_id": generate_request_id(),
		"asset_id": "PROP-2026-002",
		"owner_name": "Meera Iyer",
		"property_type": "Agricultural",
		"area": "2.5 acres",
		"location": "Hosur Road, Karnataka",
		"status": "Pending",
		"comments": "Initial mutation request awaiting registrar review.",
		"created_at": utc_now(),
		"updated_at": utc_now(),
	}
]


audit_logs = [
	{
		"timestamp": utc_now(),
		"action": "System initialized",
		"details": "Seeded SecureCivic demo assets, requests, and audit trail.",
	}
]


def log_audit(action: str, details: str) -> None:
	audit_logs.append(
		{
			"timestamp": utc_now(),
			"action": action,
			"details": details,
		}
	)


def find_request(request_id: str) -> dict:
	for request in requests_db:
		if request["request_id"] == request_id:
			return request
	raise HTTPException(status_code=404, detail="Mutation request not found")


def find_asset(property_id: str) -> dict | None:
	for asset in assets_db:
		if asset["property_id"] == property_id:
			return asset
	return None


def get_registrar_account() -> tuple[object, str]:
	registrar_private_key = os.getenv("REGISTRAR_PRIVATE_KEY", "").strip().replace("\\n", "").replace("\\r", "")
	if not registrar_private_key:
		registrar_private_key = DEFAULT_HARDHAT_PRIVATE_KEY
		print("WARNING: REGISTRAR_PRIVATE_KEY is not configured; using the local Hardhat default private key for development.")

	try:
		registrar_account = w3.eth.account.from_key(registrar_private_key)
	except Exception as exc:
		raise HTTPException(status_code=500, detail=f"Invalid registrar private key: {exc}") from exc

	return registrar_account, registrar_private_key


def build_seal_transaction(request_record: dict, registrar_address: str) -> dict:
	contract_functions = contract.functions
	if hasattr(contract_functions, "approveMutation"):
		contract_call = contract_functions.approveMutation(request_record["request_id"])
	elif hasattr(contract_functions, "mintLandRecord"):
		contract_call = contract_functions.mintLandRecord(
			request_record["request_id"],
			request_record["asset_id"],
			request_record["owner_name"],
			request_record["location"],
		)
	else:
		contract_call = contract_functions.registerLand(
			int(request_record["asset_id"].split("-")[-1]) if isinstance(request_record["asset_id"], str) and request_record["asset_id"].split("-")[-1].isdigit() else 1,
			request_record["location"],
			int(float(str(request_record["area"]).split()[0])) if str(request_record["area"]).replace(".", "", 1).isdigit() or str(request_record["area"]).split()[0].replace(".", "", 1).isdigit() else 1,
		)

	nonce = w3.eth.get_transaction_count(registrar_address)
	base_tx = contract_call.build_transaction(
		{
			"from": registrar_address,
			"nonce": nonce,
			"chainId": w3.eth.chain_id,
		}
	)
	if "gas" not in base_tx:
		base_tx["gas"] = w3.eth.estimate_gas(base_tx)
	if "gasPrice" not in base_tx and "maxFeePerGas" not in base_tx:
		base_tx["gasPrice"] = w3.eth.gas_price
	return base_tx


def get_pinata_error_message(response: requests.Response | None, fallback: str) -> str:
	if response is None:
		return fallback

	try:
		payload = response.json()
		if isinstance(payload, dict):
			for key in ("error", "message", "details"):
				value = payload.get(key)
				if value:
					return str(value)
			return str(payload)
		return str(payload)
	except Exception:
		response_text = response.text.strip()
		return response_text or fallback


def upload_file_to_pinata(file_path: str, filename: str, content_type: str | None) -> dict:
	pinata_jwt = os.getenv("PINATA_JWT", "").strip().replace("\\n", "").replace("\\r", "")
	if not pinata_jwt:
		raise HTTPException(status_code=500, detail="PINATA_JWT is not configured")

	response = None
	try:
		headers = {"Authorization": f"Bearer {pinata_jwt}"}
		with open(file_path, "rb") as file_handle:
			files = {
				"file": (
					filename,
					file_handle,
					content_type or "application/octet-stream",
				),
			}
			response = requests.post(
				"https://api.pinata.cloud/pinning/pinFileToIPFS",
				headers=headers,
				files=files,
				timeout=60,
			)

		response.raise_for_status()
		payload = response.json()
		ipfs_hash = payload.get("IpfsHash")
		if not ipfs_hash:
			raise ValueError("Pinata response did not include IpfsHash")

		return {
			"IpfsHash": ipfs_hash,
			"gateway_url": f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}",
		}
	except HTTPException:
		raise
	except Exception as exc:
		traceback.print_exc()
		error_message = get_pinata_error_message(response, str(exc))
		raise HTTPException(status_code=500, detail=error_message)


@app.get("/")
def health_check() -> dict:
	return {
		"message": "SecureCivic backend is running.",
		"status": "healthy",
		"timestamp": utc_now(),
	}


@app.get("/api/citizen/assets")
def get_citizen_assets() -> dict:
	return {
		"assets": assets_db,
		"requests": requests_db,
	}


@app.post("/api/citizen/mutate")
def create_mutation_request(payload: MutationRequest) -> dict:
	request_id = generate_request_id()
	record = {
		"request_id": request_id,
		"asset_id": payload.asset_id,
		"owner_name": payload.owner_name,
		"property_type": payload.property_type,
		"area": payload.area,
		"location": payload.location,
		"status": "Pending",
		"comments": "Citizen mutation request submitted.",
		"created_at": utc_now(),
		"updated_at": utc_now(),
	}
	requests_db.append(record)
	log_audit(
		action="Mutation request created",
		details=f"{request_id} submitted for asset {payload.asset_id} by {payload.owner_name}.",
	)
	return {
		"success": True,
		"message": "Mutation request submitted successfully.",
		"request": record,
	}


@app.get("/api/registrar/dashboard")
def registrar_dashboard() -> dict:
	return {
		"queue": requests_db,
		"audit_logs": audit_logs,
	}


@app.post("/api/registrar/action/{request_id}")
def registrar_action(request_id: str, action: ApprovalAction) -> dict:
	request_record = find_request(request_id)
	if request_record["status"] != "Pending":
		raise HTTPException(status_code=400, detail=f"Request {request_id} has already been processed.")

	asset_record = find_asset(request_record["asset_id"])
	asset_status = None

	blockchain_tx_hash = None
	if action.status == "Approved":
		try:
			registrar_account, registrar_private_key = get_registrar_account()
			tx_payload = build_seal_transaction(request_record, registrar_account.address)
			signed_transaction = registrar_account.sign_transaction(tx_payload)
			tx_hash = w3.eth.send_raw_transaction(signed_transaction.raw_transaction)
			if not tx_hash:
				raise ValueError("Blockchain transaction hash was not returned")
			receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
			if getattr(receipt, "status", 0) != 1:
				raise ValueError("Blockchain transaction execution failed")

			blockchain_tx_hash = tx_hash.hex()
			request_record["status"] = "Approved"
			request_record["comments"] = action.comments
			request_record["updated_at"] = utc_now()

			if asset_record is not None:
				asset_record["status"] = "Verified"
				asset_record["owner_name"] = request_record["owner_name"]
				asset_record["property_type"] = request_record["property_type"]
				asset_record["area"] = request_record["area"]
				asset_record["location"] = request_record["location"]
				asset_record["last_updated"] = utc_now()
				asset_status = asset_record["status"]

			log_audit(
				action="Blockchain record sealed",
				details=(
					f"{request_id} sealed on-chain by registrar {registrar_account.address} with tx {blockchain_tx_hash}. "
					f"Block {receipt.blockNumber} confirmed."
				),
			)
		except HTTPException:
			raise
		except (ValueError, ContractLogicError, Exception) as exc:
			traceback.print_exc()
			log_audit(
				action="Blockchain sealing failed",
				details=f"{request_id} approval failed: {exc}",
			)
			raise HTTPException(status_code=500, detail=f"Blockchain sealing failed: {exc}") from exc
	elif action.status == "Rejected":
		request_record["status"] = "Rejected"
		request_record["comments"] = action.comments
		request_record["updated_at"] = utc_now()

		if asset_record is not None:
			asset_status = asset_record["status"]

	log_audit(
		action=f"Mutation request {action.status.lower()}",
		details=f"{request_id} was {action.status.lower()} by registrar. Comments: {action.comments or 'No comments provided.'}",
	)

	return {
		"success": True,
		"message": f"Request {request_id} {action.status.lower()} successfully.",
		"request": request_record,
		"asset_status": asset_status,
		"blockchain_tx_hash": blockchain_tx_hash,
	}


@app.post("/register-land/")
def register_land(payload: LandRegistrationRequest) -> dict:
	tx_hash = contract.functions.registerLand(
		payload.asset_id,
		payload.location,
		payload.area,
	).transact()
	w3.eth.wait_for_transaction_receipt(tx_hash)
	return {"tx_hash": tx_hash.hex()}


@app.post("/upload-document/")
def upload_document(document: UploadFile = File(...)) -> dict:
	temp_file_path = None
	try:
		with tempfile.NamedTemporaryFile(delete=False) as temp_file:
			temp_file_path = temp_file.name
			content = document.file.read()
			temp_file.write(content)

		try:
			pinata_result = upload_file_to_pinata(temp_file_path, document.filename or "upload.bin", document.content_type)
		except HTTPException:
			raise
		except Exception as exc:
			traceback.print_exc()
			raise HTTPException(status_code=500, detail=str(exc))
		return {
			"success": True,
			"IpfsHash": pinata_result["IpfsHash"],
			"gateway_url": pinata_result["gateway_url"],
		}
	finally:
		document.file.close()
		if temp_file_path and os.path.exists(temp_file_path):
			os.remove(temp_file_path)


@app.get("/get-land/{land_id}")
def get_land(land_id: int) -> dict:
	land = contract.functions.lands(land_id).call()
	land_record = {
		"id": int(land[0]),
		"location": land[1],
		"area": int(land[2]),
		"owner": land[3],
		"is_for_sale": land[4],
	}
	if land_record["id"] == 0:
		raise HTTPException(status_code=404, detail="Land not found")
	return land_record
