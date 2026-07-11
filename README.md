# SecureCivic

SecureCivic is a blockchain-enabled land governance MVP that combines a FastAPI backend, a Hardhat-based smart contract workflow, and a lightweight browser frontend for citizen submissions and registrar approvals.

The project is built around a hybrid trust model: sensitive state transitions are enforced on-chain, while form handling, file validation, request orchestration, and audit visibility are handled by the backend and frontend layers.

## 1. Project Overview & Features

SecureCivic focuses on a controlled mutation workflow for land records. The current implementation supports:

- Role-based mutations for citizen submission and registrar approval flows.
- Web3 and Hardhat integration for local blockchain signing, transaction execution, and contract interaction.
- Immutable audit log entries for key state transitions and blockchain execution outcomes.
- IPFS document upload support through Pinata for off-chain document storage.
- A responsive browser interface for viewing assets, submitting requests, and tracking mutation status.
- Local development support through FastAPI, Hardhat, and a simulated blockchain environment.

Core project surfaces:

- Backend API: [backend_Civic/main.py](backend_Civic/main.py)
- Frontend application: [frontent_Civic/index.html](frontent_Civic/index.html)
- Solidity contracts and tests: [contracts/](contracts/)

## 2. Environment Variables Guide (Task 3)

SecureCivic uses environment variables to separate secrets from source code. Create [backend_Civic/.env](backend_Civic/.env) locally using [.env.example](.env.example) as the template.

| Variable | Required | Description |
| --- | --- | --- |
| `PINATA_API_KEY` | Yes for IPFS uploads | Public Pinata API key used by the backend when preparing document upload requests. |
| `PINATA_SECRET_API_KEY` | Yes for IPFS uploads | Secret Pinata API key used with the Pinata upload flow. Keep this out of version control. |
| `REGISTRAR_PRIVATE_KEY` | Yes for production or custom registrar signing | Ethereum private key used by the backend to sign registrar transactions. For local development, the backend falls back to the standard Hardhat account if this variable is missing. |

Example template:

```env
PINATA_API_KEY="your-pinata-api-key"
PINATA_SECRET_API_KEY="your-pinata-secret-api-key"
REGISTRAR_PRIVATE_KEY="0x-your-private-key"
```

Recommended notes:

- Keep `.env` local only and never commit it.
- Use `.env.example` to document the expected variables without exposing secrets.
- For local demos, the default Hardhat registrar key can be used only against a local node.

## 3. Deployment & Setup Instructions (Task 4)

Follow the steps below for a local demo environment.

### Prerequisites

- Node.js and npm
- Python 3.12 or compatible virtual environment support
- A local browser for opening the frontend

### Local setup

1. Install frontend and Hardhat dependencies.

```bash
npm install
```

2. Start a local Hardhat blockchain.

```bash
npx hardhat node
```

3. Open a second terminal, activate the Python environment for the backend, then start FastAPI.

```bash
uvicorn main:app --reload
```

If your backend file lives in `backend_Civic/`, run the command from that directory:

```bash
cd backend_Civic
uvicorn main:app --reload
```

4. Open the frontend in your browser.

```text
frontent_Civic/index.html
```

You can open the file directly in a browser or use your editor’s live preview if available.

### Cloud hosting readiness

SecureCivic is structured so it can be moved toward cloud hosting with a standard FastAPI deployment model and containerized builds. The backend can be packaged for Docker-based deployment, while the smart contract and frontend layers remain compatible with a production pipeline that swaps local endpoints for hosted RPC and storage services.

## 4. Troubleshooting Section (Task 5)

Common issues and quick fixes:

### `REGISTRAR_PRIVATE_KEY` not configured or 500 error

- Confirm that `backend_Civic/.env` exists and includes `REGISTRAR_PRIVATE_KEY`.
- Make sure the key is a valid hex private key starting with `0x`.
- For local development, allow the backend to use the default Hardhat key only when connected to the local Hardhat node.

### Blockchain node connection failures

- Verify that `npx hardhat node` is running before submitting registrar actions.
- Confirm the backend is pointed at the correct local RPC endpoint.
- Restart the node if the contract address or deployment state changed.

### Missing virtualenv dependencies

- Activate the correct Python environment before starting FastAPI.
- Install missing packages inside the active environment.
- If file uploads fail during app startup, ensure `python-multipart` is installed.

Example recovery commands:

```bash
pip install -r requirements.txt
pip install python-multipart
```

## 5. Phase 2 Future Scope (Task 6)

Phase 2 should begin with scope freezing. The current MVP requirements should remain fixed before expanding the feature set so that contract behavior, backend state transitions, and frontend workflows stay predictable.

Future enhancements can include:

- Decentralized identity integration, including DID-based verification for user and registrar roles.
- Automated multi-signature validation for high-value properties and sensitive mutation approvals.
- Gas optimization models for lower-cost on-chain execution and better transaction planning.
- Expanded audit analytics for mutation history, dispute tracing, and registrar oversight.
- Stronger document provenance checks and policy-driven file validation before IPFS pinning.
- More advanced role separation and policy enforcement for district-level and state-level workflows.

The key principle for Phase 2 is to preserve the current MVP contract surface unless a change is explicitly justified by the next product milestone.

## Project Notes

- Hardhat configuration: [hardhat.config.ts](hardhat.config.ts)
- Solidity tests: [contracts/](contracts/)
- Backend API: [backend_Civic/main.py](backend_Civic/main.py)
- Frontend shell: [frontent_Civic/index.html](frontent_Civic/index.html)

## License

No license has been specified yet. Add one before public distribution.
