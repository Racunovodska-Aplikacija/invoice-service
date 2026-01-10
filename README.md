# Invoice Service

Invoice management service for the RAC application with REST API. Invoice responses are enriched via gRPC calls to company/partner/product services.

## Database

- **Database Name**: `invoiceDB` (default via `DB_DATABASE`)
- **HTTP Port**: 8000

## Entities

### Invoice
- `id` (UUID, Primary Key)
- `user_id` (UUID, Required)
- `company_id` (UUID, Required)
- `partner_id` (UUID, Required)
- `invoice_number` (String, Required)
- `issue_date` (Timestamp, Required)
- `service_date` (Timestamp, Required)
- `due_date` (Timestamp, Required)
- `notes` (Text, Optional)
- `status` (Enum: `ISSUED` | `PAID` | `CANCELLED`)
- `company_name` (String, Optional) - Snapshot for list display
- `partner_name` (String, Optional) - Snapshot for list display
- `total` (Numeric, Optional) - Snapshot for list display

### InvoiceLine
- `id` (UUID, Primary Key)
- `invoice_id` (UUID, Foreign Key)
- `product_id` (UUID, Required)
- `amount` (Integer, Required)

## REST API Endpoints

All `/invoices` endpoints require JWT authentication.

**Headers:**
```
Authorization: Bearer {jwt-token}
```

**Or cookie:**
```
jwt={jwt-token}
```

### Invoice Management (Protected)

#### Get All Invoices
```
GET /invoices
```

#### Get Invoice by ID (Enriched)
```
GET /invoices/:id
```

#### Create Invoice
```
POST /invoices
```

**Request Body (example):**
```json
{
  "company_id": "00000000-0000-0000-0000-000000000001",
  "partner_id": "00000000-0000-0000-0000-000000000002",
  "invoice_number": "INV-000001",
  "issue_date": "2026-01-10T12:00:00Z",
  "service_date": "2026-01-10T12:00:00Z",
  "due_date": "2026-02-09T12:00:00Z",
  "notes": "Optional notes",
  "lines": [
    { "product_id": "00000000-0000-0000-0000-000000000010", "amount": 2 }
  ]
}
```

#### Update Invoice
```
PUT /invoices/:id
```

#### Delete Invoice
```
DELETE /invoices/:id
```

### Health Check
```
GET /health
```

## gRPC Integrations (Client)

Invoice enrichment uses gRPC clients (this service does not expose a gRPC server).

- **Company service**: `COMPANY_SERVICE_HOST` + `COMPANY_SERVICE_GRPC_PORT` (default: `company-service:50051`)
- **Partner service**: `PARTNER_SERVICE_HOST` + `PARTNER_SERVICE_GRPC_PORT` (default: `partner-service:50051`)
- **Product service**: uses the product gRPC stub; host/port are read from `COMPANY_SERVICE_HOST` + `COMPANY_SERVICE_GRPC_PORT` in the current implementation.

## Environment Variables

### Database

- `DB_HOST` (default: `localhost`)
- `DB_PORT` (default: `5433`)
- `DB_USERNAME` (default: `postgres`)
- `DB_PASSWORD` (default: `postgres`)
- `DB_DATABASE` (default: `invoiceDB`)

### gRPC Clients

- `COMPANY_SERVICE_HOST` (default: `company-service`)
- `COMPANY_SERVICE_GRPC_PORT` (default: `50051`)
- `PARTNER_SERVICE_HOST` (default: `partner-service`)
- `PARTNER_SERVICE_GRPC_PORT` (default: `50051`)

## Running Locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Docker Build

```bash
docker build -t invoice-service:latest
```

