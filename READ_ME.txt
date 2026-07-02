# SecureCivic

Phase 1: Land Governance

## Project Mission

SecureCivic is a decentralized land governance MVP that demonstrates a tamper-proof digital land registry with automatic mutation of ownership after registration. The core idea is to move the most sensitive trust points onto a blockchain while keeping the user experience simple enough for citizens and government staff to use without deep technical knowledge.

This phase focuses on a working end-to-end prototype for two users:

1. Citizen Portal for land owners.
2. Registrar Dashboard for government officials.

## Strategic Decisions

The roadmap below is optimized for a beginner developer and a lightweight setup.

- Frontend: Vanilla HTML5, CSS3, and JavaScript with Fetch API.
- Backend: Python with FastAPI.
- Blockchain: Solidity smart contracts, developed and tested locally with Hardhat and inspected in Remix as needed.
- Storage: IPFS through Pinata for heavy land documents and maps.
- Development style: simple, incremental, and test-first where possible.

## Architecture Overview

The MVP should follow a hybrid architecture:

- The blockchain is the source of truth for ownership state, mutation events, and immutable registry records.
- The backend is the orchestration layer for authentication, API handling, IPFS pinning, file validation, and app workflows.
- The frontend is a thin presentation layer that calls the backend and, when required, triggers wallet-connected blockchain actions.

Recommended responsibility split:

- Smart contract: registry, ownership transfer, mutation approval, role checks, and event emission.
- FastAPI backend: user sessions, role management, land metadata APIs, Pinata proxy integration, and transaction tracking.
- Vanilla frontend: forms, dashboards, search, status views, and transaction feedback.

## Beginner Milestones

These are the milestones that matter most for a first-time full-stack builder:

1. Get the stack running locally with a clean folder structure.
2. Build a basic UI before any advanced logic.
3. Create FastAPI endpoints that serve static data and validate requests.
4. Write and deploy a minimal smart contract with one clear land registry flow.
5. Connect the backend to IPFS for document storage.
6. Connect the frontend to the backend and blockchain in small steps.
7. Add role-based workflows for citizen submission and registrar approval.
8. Make the auto-mutation flow observable through events and status screens.
9. Test the whole system end to end.
10. Package the MVP so it can be demonstrated reliably.

## End-to-End Roadmap

### Phase 0: Product and Technical Foundations

Define the exact MVP scope, user roles, transaction flow, document types, and what is intentionally excluded from phase 1. Freeze the data model early so you do not keep rewriting the contract and backend together.

### Phase 1: Local Development Foundation

Set up the workspace, Python environment, FastAPI project, static frontend shell, and Hardhat contract workspace. At the end of this phase you should be able to open the app locally and see a basic UI plus a running API.

### Phase 2: Registry Core

Implement the first contract version, the main land record data structures, and the basic API wrappers. This is where the registry becomes real and immutable, even if the UI is still rough.

### Phase 3: Document and IPFS Layer

Add document upload, Pinata pinning, hash storage, and retrieval metadata. The app should never rely on storing large files directly on-chain.

### Phase 4: Citizen and Registrar Workflows

Build the user-facing flows for land submission, review, mutation, and status tracking. At this stage the system becomes a usable demo rather than just a technical prototype.

### Phase 5: Auto-Mutation Engine

Implement the actual state transition logic that triggers ownership mutation after a verified registry action. This phase should be treated carefully because it is the core product promise.

### Phase 6: Hardening and Demo Readiness

Add error handling, validation, logs, tests, deployment instructions, and a guided demo dataset. The output of this phase should be stable enough for stakeholder review.

## Weekly Sprint Plan

The plan below assumes one focused sprint per week. If you are working part-time, stretch each sprint to two weeks without changing the order.

### Sprint 1: Scope Lock and Workspace Setup

Goal:

Create the project skeleton and lock the MVP scope before writing feature code.

Step-by-step tasks:

1. Write the product scope and confirm the citizen and registrar user stories.
2. Decide the MVP data fields for land records, owners, mutation requests, and document hashes.
3. Create the folder structure for frontend, backend, contracts, docs, and deployment.
4. Set up Python virtual environment, FastAPI, Uvicorn, and basic project dependencies.
5. Set up Hardhat and initialize the Solidity workspace.
6. Create the first static frontend shell with navigation and placeholder pages.
7. Document the technical rules for what goes on-chain versus off-chain.

Deliverable:

A clean local workspace that opens without errors, plus a written MVP scope and folder structure.

### Sprint 2: UI Skeleton and Navigation

Goal:

Build the visual shell for both portals before connecting any real data.

Step-by-step tasks:

1. Create the Citizen Portal pages: home, submit request, check status, and document upload.
2. Create the Registrar Dashboard pages: queue, record review, approval screen, and audit log view.
3. Add reusable header, sidebar, form, table, and alert styles.
4. Implement simple client-side navigation and page state.
5. Add empty form validations and loading states.
6. Make the layout responsive for desktop and mobile.

Deliverable:

A clickable static prototype of both portals with clean navigation and no backend dependency.

### Sprint 3: FastAPI Foundation

Goal:

Turn the backend into a working API that can support the frontend.

Step-by-step tasks:

1. Create the FastAPI app entry point and route modules.
2. Define core schemas for citizens, registrars, land records, and mutation requests.
3. Add health check and test endpoints.
4. Configure CORS for the frontend.
5. Add a simple in-memory or SQLite-based development data layer.
6. Create API endpoints for listing, submitting, and reviewing land cases.
7. Write basic backend tests for request validation.

Deliverable:

A running FastAPI service with stable endpoints that return and accept structured data.

### Sprint 4: Smart Contract v1

Goal:

Create the first usable Solidity contract for land registry and ownership mutation.

Step-by-step tasks:

1. Define the contract data model for land IDs, owner addresses, registry hash, and mutation status.
2. Add access control for registrar-only and owner-only actions.
3. Implement functions for register land, verify record, trigger mutation, and read record status.
4. Emit events for each important state change.
5. Deploy and test the contract locally with Hardhat.
6. Inspect the contract in Remix for manual verification.

Deliverable:

A deployed local contract with the minimum registry workflow working end to end.

### Sprint 5: IPFS and Pinata Integration

Goal:

Store large land documents off-chain and retain only their immutable hashes on-chain.

Step-by-step tasks:

1. Create a backend service for file upload and validation.
2. Integrate Pinata API credentials securely in environment variables.
3. Upload sample land maps and supporting documents to IPFS.
4. Save returned IPFS hashes and metadata in the backend database.
5. Connect uploaded document references to land record submissions.
6. Add download and preview links for approved records.

Deliverable:

A working document pipeline where files are pinned to IPFS and referenced by hash in the app.

### Sprint 6: Citizen Submission Workflow

Goal:

Let a citizen submit a land case from the portal to the backend and prepare it for registry review.

Step-by-step tasks:

1. Build the citizen submission form with validation.
2. Accept land details, identity details, and supporting file uploads.
3. Send form data to FastAPI using Fetch API.
4. Store the submission as a pending mutation case.
5. Show a submission ID and progress status.
6. Link uploaded documents to the IPFS hash records.

Deliverable:

A citizen can submit a case and see a tracked pending request in the portal.

### Sprint 7: Registrar Review and Approval Workflow

Goal:

Give the registrar a controlled dashboard to validate, approve, or reject a case.

Step-by-step tasks:

1. Display submitted cases in a review queue.
2. Show land metadata, uploaded hashes, and submission history.
3. Add approve and reject actions with reason capture.
4. Lock approved records from accidental editing.
5. Create audit log entries for every registrar action.
6. Connect approval actions to backend persistence and smart contract calls.

Deliverable:

A registrar can review a submitted record and either approve it or reject it with a traceable reason.

### Sprint 8: Auto-Mutation and On-Chain State Sync

Goal:

Implement the signature feature: automatic mutation after successful registration.

Step-by-step tasks:

1. Define the exact trigger condition for auto-mutation.
2. Update the smart contract to emit ownership transfer or mutation completion events.
3. Make the backend listen to and record blockchain events.
4. Update the frontend status views when mutation completes.
5. Add safeguards so duplicate mutation attempts are blocked.
6. Test edge cases such as failed transaction, repeated approval, and missing hash.

Deliverable:

A complete mutation lifecycle visible across contract, backend, and frontend.

### Sprint 9: Validation, Security, and Testing

Goal:

Reduce risk by testing the critical flows and tightening input/security controls.

Step-by-step tasks:

1. Add frontend validation for all user input fields.
2. Add backend validation, error handling, and structured responses.
3. Test contract access control, event emission, and invalid state transitions.
4. Add integration tests for the main citizen and registrar workflows.
5. Review secret handling for Pinata keys, wallet credentials, and environment files.
6. Add clear warnings for non-recoverable blockchain actions.

Deliverable:

A tested MVP with the main bugs reduced and the dangerous failure modes understood.

### Sprint 10: Demo Packaging and Release Readiness

Goal:

Prepare the system for a polished demonstration and future expansion.

Step-by-step tasks:

1. Clean the UI copy and status labels.
2. Seed a demo dataset with realistic land cases.
3. Write setup instructions and environment variable examples.
4. Capture the deployment steps for local demo or cloud hosting.
5. Add a concise troubleshooting section.
6. Freeze the MVP scope and list phase 2 ideas separately.

Deliverable:

A stable demo package with setup instructions, sample data, and a repeatable walkthrough.

## Proposed Folder Structure

Use this directory layout to keep the project understandable for a beginner:

```text
SecureCivic/
├─ frontend/
│  ├─ assets/
│  │  ├─ images/
│  │  └─ icons/
│  ├─ css/
│  │  └─ styles.css
│  ├─ js/
│  │  ├─ app.js
│  │  ├─ api.js
│  │  └─ ui.js
│  ├─ pages/
│  │  ├─ citizen.html
│  │  ├─ registrar.html
│  │  └─ login.html
│  └─ index.html
├─ backend/
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ api/
│  │  │  ├─ routes.py
│  │  │  └─ auth.py
│  │  ├─ core/
│  │  │  ├─ config.py
│  │  │  └─ security.py
│  │  ├─ models/
│  │  │  └─ land.py
│  │  ├─ schemas/
│  │  │  └─ land.py
│  │  ├─ services/
│  │  │  ├─ ipfs.py
│  │  │  └─ blockchain.py
│  │  └─ utils/
│  ├─ tests/
│  │  └─ test_api.py
│  ├─ requirements.txt
│  └─ .env.example
├─ contracts/
│  ├─ contracts/
│  │  └─ LandRegistry.sol
│  ├─ scripts/
│  │  └─ deploy.js
│  ├─ test/
│  │  └─ LandRegistry.test.js
│  └─ hardhat.config.js
├─ docs/
│  ├─ roadmap.md
│  ├─ api-spec.md
│  └─ contract-notes.md
├─ deployment/
│  ├─ local-setup.md
│  └─ demo-checklist.md
└─ README.md
```

## Technical Warnings And Prerequisites

Before you start building, make sure you understand these points:

1. HTML, CSS, JavaScript, and async Fetch API basics.
2. Python fundamentals, virtual environments, and FastAPI request handling.
3. REST API concepts, JSON structures, and browser CORS behavior.
4. Solidity fundamentals, especially `msg.sender`, access control, and event logs.
5. The difference between on-chain data and off-chain files.
6. IPFS and Pinata pinning behavior.
7. Wallet usage, transaction signing, gas fees, and transaction finality.
8. Environment variable management and secret protection.

Potential blockers to expect:

- Wallet setup and local blockchain configuration may be confusing at first.
- Solidity compiler version mismatches can break the build unexpectedly.
- Pinata credentials and IPFS uploads require careful environment handling.
- A land registry is legally sensitive, so the MVP must stay clearly labeled as a demo unless validated by the proper authority.
- Do not store private personal data directly on-chain.
- Auto-mutation logic must be carefully gated to avoid accidental ownership changes.

## MVP Definition Of Done

The MVP is done when all of the following are true:

1. A citizen can submit a land case with documents.
2. Documents are stored in IPFS and referenced by immutable hashes.
3. A registrar can review the case and approve or reject it.
4. The approved record triggers the smart contract flow.
5. Ownership mutation status is visible in the portal.
6. The system can be run locally from a documented setup process.
7. The demo works end to end without manual database editing.

## Recommended Working Rules

- Build one feature at a time and keep each sprint shippable.
- Do not add frameworks unless the project is blocked without them.
- Keep the contract small until the workflow is proven.
- Prefer readable code over clever code.
- Log every important state transition.
- Treat the blockchain as append-only and irreversible.

## Next Logical Step

Start with Sprint 1 and lock the MVP scope before writing application logic. The fastest way to lose time on this project is to build UI, backend, and contract code in parallel without a frozen data model.

