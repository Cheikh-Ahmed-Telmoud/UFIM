# UFIM : USSD Financial Inclusion Middleware

**UFIM (USSD Financial Inclusion Middleware)** is a modular middleware platform built with Django. Its primary goal is to serve as an intelligent, secure, and scalable gateway between Telecom Operator networks (MNOs) / USSD aggregators (such as Africa's Talking) and the Information Systems of financial institutions (Banks, Mobile Wallets, Microfinance institutions).

The project integrates a workflow engine entirely driven by database metadata, allowing dynamic design and modification of USSD menus without changing the source code. UFIM also serves as a foundation for scientific research in cybersecurity thanks to its reinforced mechanisms for protecting sensitive data (PIN isolation, log masking, strong encryption of channels and data).

---

## 1. Key Features

*   **Dynamic Workflow Engine**: Steps, conditional branching, validation regular expressions, and USSD menu prompt texts are configurable directly in the database.
*   **Native Multilingual Support**: Full and dynamic support for French (`fr`), English (`en`), and Arabic (`ar`).
*   **Abstract Financial Connectors**: Extensible integration layer to connect to banking APIs (REST, SOAP, ISO 8583) via specific connectors (`BankConnector`, `WalletConnector`).
*   **Stateless Session Management**: Tracking and persistence of USSD session states with a strict expiration time (120 seconds TTL).
*   **Reinforced Security (Scientific Design)**:
    *   **PIN Isolation**: No persistent or temporary storage of the user's PIN code in the database or logs.
    *   **Fernet Encryption**: AES-128 symmetric encryption in the database for partner institution credentials.
    *   **Secure Channels**: Planned integration of mTLS and HMAC-SHA256 signatures for requests to financial institutions.
    *   **Audit Log Masking**: Logging middleware that automatically anonymizes sensitive data (e.g., phone number `+222******77` and complete PIN masking).

---

## 2. Global Architecture

UFIM's architecture is structured in watertight layers to isolate network reception, orchestration logic, temporary storage, and communication with institutions.

### Component Structural Diagram

![Global Architecture](./images/archi_global.png)


### 3. USSD Request Lifecycle (Data Flow)

This diagram shows the path of a request sent by the end user's terminal through the middleware.

![Data Flow Diagram](./images/diagram_data_flow.png)


## 4. Project Structure

```text
UFIM/
│
├── config/                  # Global Django project configuration
│   ├── settings.py          # Settings (Security, Database, Keys, Logs)
│   ├── urls.py              # Main URL routing
│   └── wsgi.py / asgi.py    # Application server entry points
│
├── ussd/                    # USSD gateway entry point
│   ├── views.py             # Africa's Talking HTTP POST Webhook
│   └── urls.py              # Public URL /ussd/
│
├── ussd_sessions/           # Persistent USSD session management
│   ├── manager.py           # Initialization, update, and validation logic
│   └── models.py            # UssdSession model (TTL, temporary data)
│
├── workflows/               # Dynamic workflow engine
│   ├── engine.py            # State transition computation, regex validation, prompts
│   └── models.py            # Workflow, WorkflowStep, and WorkflowStepBranch models
│
├── routing/                 # Connectors with financial institutions
│   ├── dispatcher.py        # Dynamic routing to the institution's connector
│   └── connectors/          # Third-party connector implementations
│       ├── base.py          # Abstract base class BaseConnector
│       ├── bank_connector.py # Connectors for traditional banks
│       └── wallet_connector.py # Connectors for mobile wallets (e.g. Mobile Money)
│
├── institutions/            # Institution metadata
│   └── models.py            # Institution and Service models
│
├── security/                # Security and encryption tools
│   └── crypto.py            # Fernet symmetric encryption utilities
│
├── monitoring/              # Logging and auditing
│   └── security_logger.py   # Anonymization middleware and audit log writing
│
├── cahier_charge/           # Project specifications and architecture documents
│
├── Dockerfile               # Application image build recipe
├── docker-compose.yml       # Local orchestration (Django + PostgreSQL)
├── seed_data.py             # DB population script (Demo)
├── requirements.txt         # Python project dependencies
└── manage.py                # Django administration utility script
```

---

## 5. Installation and Setup

### Option A. Running with Docker (Recommended)

Docker allows running the application and an isolated PostgreSQL database without local configuration.

1.  **Launch orchestration**:
    ```bash
    docker-compose up --build
    ```
    This command will:
    *   Download and configure the PostgreSQL database image.
    *   Build the Python image for the UFIM application.
    *   Run database migrations.
    *   Automatically execute the `seed_data.py` population script.
    *   Start the server on port `8080` (mapped to the internal Docker port `8000`).

2.  **Verify operation**:
    The application responds at `http://localhost:8080/ussd/`.

---

### Option B. Local Installation in Development Mode

If you prefer to run the application outside a container:

1.  **Create a virtual environment** and activate it:
    ```bash
    # On Windows (PowerShell)
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    
    # On Linux / macOS
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure environment variables (Optional)**:
    By default, UFIM uses SQLite (`db.sqlite3`) and a static local encryption key. If you wish to use a custom key or database:
    *   `UFIM_ENCRYPTION_KEY`: Fernet encryption key (32 bytes base64-encoded).
    *   `DATABASE_URL`: Database connection URL (e.g., `postgres://user:pass@host:port/db_name`).

4.  **Apply migrations**:
    ```bash
    python manage.py migrate
    ```

5.  **Populate the database with demo data**:
    ```bash
    python manage.py shell < seed_data.py
    ```

6.  **Start the development server**:
    ```bash
    python manage.py runserver
    ```
    The server will listen on `http://127.0.0.1:8000/`.

---

## 6. Logging and Security Audit

All security events (API authentication, transfer execution, expired session blocks) and incoming/outgoing requests pass through an audit logger located in `ufim_audit.log`.

To read security logs in real-time:
```bash
# On Unix / Linux
tail -f ufim_audit.log
```

Phone numbers appear anonymized (e.g. `+222******77`) and fields like `pin` are excluded or completely masked to prevent any confidential data leaks.

---

## 7. Tests & Screenshots

*Below are the screenshots captured from the Africa's Talking USSD Simulator, demonstrating the end-to-end user flows for various financial services (Balance inquiry, Transfers, Payments, etc.) mapped through the dynamic workflow engine.*

### 7.1. Simulation Flow (Part 1)

<p align="center">
  <img src="./images/1.png" width="24%">
  <img src="./images/2.png" width="24%">
  <img src="./images/3.png" width="24%">
  <img src="./images/4.png" width="24%">
  <img src="./images/5.png" width="24%">
</p>
<p align="center">
  <img src="./images/7.png" width="24%">
  <img src="./images/8.png" width="24%">
  <img src="./images/9.png" width="24%">
  <img src="./images/10.png" width="24%">
  <img src="./images/11.png" width="24%">
</p>

<p align="center">
  <img src="./images/7.png" width="24%">
  <img src="./images/16.png" width="24%">
  <img src="./images/17.png" width="24%">
  <img src="./images/18.png" width="24%">
  <img src="./images/19.png" width="24%">
</p>

### 7.2. Simulation Flow (Part 2)
<p align="center">
  <img src="./images/12.png" width="24%">
  <img src="./images/13.png" width="24%">
  <img src="./images/14.png" width="24%">
  <img src="./images/15.png" width="24%">
</p>
<p align="center">
  <img src="./images/13.png" width="24%">
  <img src="./images/20.png" width="24%">
  <img src="./images/21.png" width="24%">
  <img src="./images/22.png" width="24%">
</p>

### 7.3. Simulation Flow (Part 3)

<p align="center">
  <img src="./images/23.png" width="24%">
  <img src="./images/24.png" width="24%">
  <img src="./images/25.png" width="24%">
</p>
