from datetime import datetime, timezone
from itertools import count
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from web3 import Web3

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
	request_record["status"] = action.status
	request_record["comments"] = action.comments
	request_record["updated_at"] = utc_now()

	asset_record = find_asset(request_record["asset_id"])
	asset_status = None
	if action.status == "Approved" and asset_record is not None:
		asset_record["status"] = "Verified"
		asset_record["owner_name"] = request_record["owner_name"]
		asset_record["property_type"] = request_record["property_type"]
		asset_record["area"] = request_record["area"]
		asset_record["location"] = request_record["location"]
		asset_record["last_updated"] = utc_now()
		asset_status = asset_record["status"]
	elif action.status == "Rejected" and asset_record is not None:
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
