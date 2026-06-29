# MAVVE Architecture

MAVVE is composed of a FastAPI backend, a React frontend, and a PostgreSQL/Redis data tier. At its core, it leverages **LangGraph** for deterministic state-machine agent orchestration and **Bhashini** for multimodal vernacular translation.

## System Overview

```mermaid
graph TD
    User([User WhatsApp]) <-->|Webhook / API| WA[WhatsApp Service]
    WA <--> Bhashini[Bhashini ASR/TTS]
    WA <--> MAVVE_Orchestrator
    
    subgraph "MAVVE Core Backend (FastAPI)"
        MAVVE_Orchestrator[LangGraph Orchestrator]
        RTO_Predictor[RTO Predictor Engine]
        Session_Mgr[Redis Session Manager]
        
        MAVVE_Orchestrator <--> AddressAgent[Address Agent]
        MAVVE_Orchestrator <--> IntentAgent[Intent Agent]
        MAVVE_Orchestrator <--> PrepaidAgent[Prepaid Conversion Agent]
    end
    
    MAVVE_Orchestrator <--> LLM[Gemini 1.5 Flash]
    
    Client_System([E-Commerce Backend]) -->|POST /intercept| RTO_Predictor
    RTO_Predictor -->|High Risk| Session_Mgr
    Session_Mgr --> MAVVE_Orchestrator
    
    DB[(PostgreSQL)]
    MAVVE_Orchestrator --> DB
    
    Frontend[React Dashboard] -->|API / WebSockets| MAVVE_Orchestrator
```

## LangGraph State Machine

MAVVE uses a directed cyclic graph to handle multi-turn conversations. The `Orchestrator` node determines which specialized agent should respond based on the detected risk factors.

```mermaid
stateDiagram-v2
    [*] --> AnalyzeRisk
    AnalyzeRisk --> AddressAgent: Address Anomaly
    AnalyzeRisk --> PrepaidAgent: High RTO COD
    AnalyzeRisk --> IntentAgent: Suspicious User
    
    AddressAgent --> HumanInput
    PrepaidAgent --> HumanInput
    IntentAgent --> HumanInput
    
    HumanInput --> OrchestratorRouting
    OrchestratorRouting --> AddressAgent
    OrchestratorRouting --> PrepaidAgent
    OrchestratorRouting --> IntentAgent
    
    OrchestratorRouting --> DispatchOrder: Validated
    OrchestratorRouting --> CancelOrder: Cancelled/Escalated
    
    DispatchOrder --> [*]
    CancelOrder --> [*]
```

## Bhashini Multimodal Pipeline

When a user sends a Voice Note in a vernacular language (e.g., Hindi, Marathi), MAVVE executes the following chain:

1. **ASR (Speech to Text)**: Bhashini converts Vernacular Audio ➡️ Vernacular Text.
2. **NMT (Translation)**: Bhashini translates Vernacular Text ➡️ English Text.
3. **LLM Processing**: Gemini processes the English text and formulates a response.
4. **NMT (Translation)**: Bhashini translates English Reply ➡️ Vernacular Reply.
5. **TTS (Text to Speech)**: Bhashini converts Vernacular Reply ➡️ Vernacular Audio.
6. Audio is dispatched to the user via WhatsApp.
