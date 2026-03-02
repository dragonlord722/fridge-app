🍳 AI Fridge Chef: Enterprise Applied AI Platform

API Documentation: https://fridge-backend-service-845166114793.us-central1.run.app/docs
🚀 Project Evolution

This platform has evolved from a monolithic Python prototype (Milestone 1) into a hardened, decoupled microservices architecture (Milestone 2). By separating the presentation layer from the inference logic, the system achieves enterprise-grade security, independent scalability, and zero-trust communication.
🏗️ System Architecture (Current: Milestone 2)

The system is designed as a Stateless Microservice architecture deployed on Google Cloud Platform (GCP).

    Frontend (Presentation Layer): Streamlit (Hosted on Streamlit Community Cloud). Acts as a "dumb" client that manages image uploads and renders JSON responses.

    Backend (Inference Layer): FastAPI (Containerized with Docker, deployed on Google Cloud Run). Handles image processing, LLM orchestration, and security validation.

    AI Engine: Google Gemini 2.5 Flash (Multimodal VLM).

    CI/CD: GitHub Actions with Workload Identity Federation (WIF) for secure, keyless GCP deployments.

🛡️  Engineering & Security Highlights

    Microservice Decoupling: Migrated from a stateful monolith to a stateless architecture. This separation allow the heavy UI processing and the lightweight AI orchestration to scale independently.

    Zero-Trust Security: Implemented a custom X-Portfolio-Token header validation to ensure only authorized clients can invoke high-cost AI operations.

    Rate Limiting & Cost Control: Integrated SlowAPI with a "Fixed Window" algorithm (5 requests/min per IP) to protect API quotas from automated abuse or accidental "token burn".

    CORS Policy Enforcement: Configured the FastAPI backend to strictly allow requests only from the authorized Streamlit domain, mitigating cross-site request forgery.

    Payload Optimization: Engineered the frontend to compress and base64-encode image payloads, significantly reducing network latency and improving request reliability.

🗺️ Future Roadmap 
Milestone 3: AI Reliability & "Evals"

    Goal: Move from "it works most of the time" to quantifiable engineering metrics.

    Implementation: Integration of evaluation frameworks (e.g., Promptfoo) into the CI pipeline to track hallucination rates and JSON schema adherence across 50+ varied fridge scenarios.

    Prompt Guardrails: Implementing specific JSON error states for non-food images (e.g., preventing the model from hallucinating "rubber salad" recipes if a user uploads a photo of a tire).

Milestone 4: Operational Excellence & Observability

    Multi-Model Routing (The Adapter Pattern): Implementing an abstract LLMProvider interface to allow seamless switching (and fallback) between Gemini, GPT-4o, and Claude 3.5 Sonnet.

    Observability: Instrumenting the backend to log critical LLM metrics: token usage (prompt vs. completion), p99 latency percentiles, and downstream API timeouts.

    Token Budgets: Introducing a Firestore "ledger" to track and cap total LLM spend per session ID/IP address.

Milestone 5: Personalization & Mobile Expansion

    Identity (OAuth 2.0): Integrating Google Sign-In for user accounts and history tracking.

    Persistence: Two-tier storage using Google Cloud Storage (GCS) for raw image blobs and Firestore for structured recipe metadata.

    Android Client: Developing a native Kotlin/Compose mobile app that consumes the same Cloud Run REST API, showcasing multi-client interoperability.

💻 Local Development Setup
Prerequisites

    Python 3.9+

    GCP Service Account Key (configured in Streamlit Secrets)

    A Google Gemini API Key

Installation

    Clone and Navigate:
    Bash

    git clone https://github.com/dragonlord722/fridge-app
    cd fridge-app

    Backend Setup:
    Bash

    cd backend
    pip install -r requirements.txt
    X_PORTFOLIO_TOKEN=your_secret uvicorn app.main:app --reload

    Frontend Setup:
    Bash

    cd frontend
    pip install -r requirements.txt
    streamlit run streamlit_app.py

📄 License

Distributed under the MIT License. See LICENSE for more information.