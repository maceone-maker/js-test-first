# Cost Center Intelligence Agent

Finance Controllers AI Agent for natural language querying of SAP S/4HANA cost center data

## Business challenge

Finance Controllers spend approximately 10 hours per week navigating manual SAP transactions to look up cost center data. They need instant, conversational answers on total cost center counts, the top 5 cost centers by actual spend, and drill-down details on individual cost centers — without opening the SAP GUI.

## Business Goals & Success Criteria

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Time spent on manual cost center lookups per controller per week | 10h/week | 3h/week (save 7h/week) | — | Cost Center Reporting / Controlling (Record to Report) | user |

## Key Milestones

1. **Data connectivity** — Agent successfully connects to SAP S/4HANA Cloud Private Edition and retrieves cost center master data via the Cost Center OData API.
2. **Count query** — Agent answers "how many cost centers do we have?" in natural language with accurate real-time data.
3. **Top 5 by spend** — Agent identifies and returns the top 5 cost centers ranked by total actual costs.
4. **Cost center drill-down** — Agent responds to follow-up questions about a specific cost center's details (name, responsible person, actual costs, hierarchy).
5. **Controller rollout** — Agent is deployed and accessible to Finance Controllers, replacing manual SAP GUI lookups.

## Business Architecture (RBA)

### End-to-End Process

Record to Report

### Process Hierarchy

```
Record to Report (E2E)
└── Perform accounting and financial close
    └── Perform accounting and financial close (BPS-413_002)
        └── Perform financial reporting
        └── Financial Analytics (Cost Center Reporting)
```

### Summary

The challenge maps to the Record to Report E2E process, specifically the "Perform accounting and financial close" sub-process. The agent automates the Financial Analytics activity by giving controllers self-service natural language access to cost center data that today requires manual SAP transactions.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Webhook API ORD ID | Data Product ORD ID | Gap? | Notes / assumptions |
|---|---|---|---|---|---|---|---|---|
| Query total count of cost centers | SAP S/4HANA Cloud Private Edition – Financial Master Data Management (SC5450) | `sap.s4:apiResource:CE_COSTCENTER_0001:v1` | — | — | — | — | Yes | No out-of-box NL query layer; custom AI Agent + MCP needed |
| Retrieve top 5 cost centers by actual spend | SAP S/4HANA Cloud Private Edition – Financial Analytics (SC5664) | `sap.s4:apiResource:CE_COSTCENTER_0001:v1` | — | — | — | — | Yes | Ranking logic built into agent; API supports filtering and sorting |
| Drill into individual cost center details | SAP S/4HANA Cloud Private Edition – Financial Master Data Management (SC5450) | `sap.s4:apiResource:CE_COSTCENTER_0001:v1` | — | — | — | — | Yes | Agent handles follow-up questions; single API call per cost center |
| Natural language interface for controllers | — | — | — | — | — | — | Yes | Fully custom — Python AI Agent (A2A) with LLM reasoning layer |
| Per-user identity tracking and S/4HANA authorization enforcement | SAP Identity Authentication Service (IAS) | — | — | — | — | — | Yes | Requires IAS–BTP–S/4HANA trust setup; token exchange at runtime propagates controller identity |

### Key findings

- SAP S/4HANA Cloud Private Edition covers cost center master data and financial analytics as mandatory capabilities, confirming the data source is available.
- The Cost Center OData API (`CE_COSTCENTER_0001:v1`) is available in the customer's landscape and is the primary data source.
- No pre-built MCP server exists for cost center APIs; an MCP translation file must be generated from the OData spec.
- The natural language query interface is a full gap — a custom Python AI Agent (A2A protocol) is required.
- APIs for cost center hierarchy (`CE_COSTCENTERHIERARCHY_0001:v1`) and controlling area (`API_CONTROLLINGAREA_SRV:v1`) are available and can support richer drill-down queries.
- On-premise variants of cost center APIs (`OP_API_COSTCENTER_SRV_0001:v1`) are marked unavailable for this tenant; cloud-native APIs are confirmed available.

## Recommendations

### Cost Center Intelligence Agent

#### Executive Summary

Python AI Agent providing natural language cost center insights via S/4HANA APIs

#### Recommended Solution

Build a pro-code Python AI Agent (A2A protocol) that wraps the SAP S/4HANA Cloud Private Edition Cost Center OData API (`CE_COSTCENTER_0001:v1`) via an MCP translation layer. The agent interprets natural language questions from Finance Controllers, calls the appropriate API tools to retrieve cost center counts, rankings by actual spend, and individual cost center details, then returns clear, conversational answers — eliminating the need to open SAP GUI.

#### Problem Statement

Finance Controllers spend approximately 10 hours per week manually navigating SAP transactions to answer routine department questions about cost centers. This is repetitive, time-consuming, and blocks controllers from higher-value analytical work.

#### Affected User Roles

- Finance Controllers
- Department managers (consumers of cost center reports)

#### Important factors

##### Eliminates repetitive manual SAP lookups

Controllers no longer need to run transactions like KS03 or S_ALR_87013611 for common questions — the agent handles these instantly through natural language.

##### Leverages existing SAP investment

The solution reuses the customer's existing SAP S/4HANA Cloud Private Edition and its standard Cost Center OData APIs — no new SAP licenses or data replication required.

##### Extensible baseline

The agent starts with count, top-5-by-spend, and drill-down — but the same architecture can easily be extended to budget variance, hierarchy traversal, or trend analysis.

##### Per-user identity tracking via IAS principal propagation

Each controller's identity must flow through to S/4HANA so that audit logs record who queried what, and S/4HANA's own authorization objects enforce per-user data access. This is achieved through SAP Identity Authentication Service (IAS) principal propagation: the controller's BTP login token is exchanged for a short-lived S/4HANA-trusted token at runtime. This requires a configured trust relationship between SAP BTP, IAS, and S/4HANA Cloud Private Edition before the agent can be used in production.

#### Potential risks

##### API authorization and data access

The agent propagates each controller's identity to S/4HANA via IAS principal propagation (OAuth2 token exchange). S/4HANA enforces that user's own authorization objects, ensuring no controller can see cost center data outside their permitted scope. The IAS-to-S/4HANA trust configuration must be established before go-live.

##### Data freshness

The agent queries live OData APIs, so answers reflect the current system state. If controllers expect period-end snapshots, expectations must be aligned during rollout.

#### Recommended solution category

AI Agent

#### Intent fit

95%
