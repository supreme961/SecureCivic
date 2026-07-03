from datetime import datetime, timezone
from itertools import count
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


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
