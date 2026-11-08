# FPS Database API

The centralized ledger and administrative backend for the fps ecosystem. This service manages fps registration, financial balances, and transaction auditing, integrating directly with Rafiki/ILP metadata.

## 🏗️ Architecture
- **Framework:** FastAPI (Python 3.11+).
- **Pattern:** **Service Layer Architecture** (Logic is separated from Routing for high reusability).
- **Database:** PostgreSQL with row-level locking for financial integrity.
- **ORM:** SQLAlchemy (Synchronous) with `pool_pre_ping` for connection stability.
- **Migrations:** Alembic.
- **Infrastructure:** Docker & Docker Compose.
- **Documentation:** 100% codebase coverage with professional Google-style docstrings.

## 📊 Database Schema

### 1. `fps_details`
Primary administrative records.
- **Fields:** `fps_name`, `registration_number`, `pan_number` (9 digits), `fps_email`, etc.
- **Status Lifecycle:**
    - `PENDING`: Initial state upon creation via `POST`.
    - `ACTIVE`: Automatically set via `PATCH` when all critical `rafiki_metadata` is provided (tenant_id, wallet_id, etc.).
    - `FAILED`: Set if a configuration attempt via `PATCH` is incomplete.
- **`rafiki_metadata`:** JSONB column for deep integration with the Rafiki system.

### 2. `balances` & `ledger_entries`
Real-time financial tracking.
- **Balances:** Stores current liquid funds per fps.
- **Ledger:** Immutable audit trail of every credit and debit.

### 3. `transactions`
Lifecycle management of inter-fps transfers.
- **States:** `PENDING` → `COMPLETED`, `FAILED`, or `CANCELLED`.
- **Integrity:** Uses atomic database transactions to ensure money is never lost or duplicated.

### 4. `api_keys`
Secure authentication for external integrations.
- Stores hashed keys linked to specific fpss.

---

## 🚀 API Endpoints
**Base Path:** `/v1/internal`

### Health
- `GET /health`: Service health check (returns status of the API).

### fpss (`/v1/internal/fps`)
- `POST /`: Create a new record (Sets status to `PENDING`).
- `GET /`: Retrieve all fpss (paginated).
- `GET /pan/{pan}`: Lookup by 9-digit PAN.
- `GET /lookup`: Verify by name and registration number.
- `GET /{id}`: Retrieve a fps by database ID.
- `GET /email/{email}`: Retrieve a fps by email.
- `PATCH /{id}`: Update metadata (Triggers `ACTIVE` status validation).

### Transactions (`/v1/internal/transactions`)
- `GET /`: Retrieve all transactions (paginated).
- `POST /`: Initialize a transfer.
- `GET /{id}`: Retrieve transaction details by database ID.
- `GET /payment/{payment_id}`: Retrieve transaction details by unique payment ID.
- `PATCH /{id}`: Complete a transfer (Triggers atomic balance movement).

### Balances (`/v1/internal/balances`)
- `GET /{id}/balance`: Get real-time liquid balance.
- `PATCH /{id}/credit`: Manually inject funds (Audit-logged).

### Webhooks (`/v1/internal/webhook`)
- `POST /`: Record external system events with idempotency checks.

---

## 🛠️ Development & Deployment

### Docker Setup
The API is optimized for Docker. It uses the service name `postgres_db` as the default host.
```bash
docker compose up -d --build
```

### Database Migrations
Always use Alembic when changing models in `app/models/`.
```bash
# Generate a new migration
POSTGRES_SERVER=localhost:5433 ./myenv/bin/alembic revision --autogenerate -m "description"

# Apply migrations
POSTGRES_SERVER=localhost:5433 ./myenv/bin/alembic upgrade head
```

### Tools
- **Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Database UI (CloudBeaver):** Available at [http://localhost:8978](http://localhost:8978)
