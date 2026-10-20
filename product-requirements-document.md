# Product Requirements Document (PRD)

**Title:** Cost Center Intelligence Agent
**Date:** 2026-10-19
**Owner:** Finance Controlling Team
**Solution Category:** AI Agent

---

## Product Purpose & Value Proposition

**Elevator Pitch:**
Finance Controllers spend up to 10 hours per week answering routine cost center questions by manually navigating SAP transactions. This agent puts those answers at their fingertips through natural language — no SAP GUI required.

**Business Need:**
When a department manager asks "how much has our cost center spent this period?" or "which cost centers are running the highest costs?", a Finance Controller today must log into SAP, navigate to the correct transaction (e.g. KS03, S_ALR_87013611), apply filters, and extract the answer manually. This is repetitive, time-consuming, and pulls controllers away from higher-value analytical work. A conversational AI agent that queries live S/4HANA data on demand eliminates this bottleneck.

**Expected Value:**
Controllers reclaim approximately 7 hours per week currently spent on manual lookups, reducing time on cost center data retrieval from 10h to 3h per week. Per-user identity propagation via IAS ensures that S/4HANA's own authorization rules are enforced on every query, maintaining compliance and auditability.

**Product Objectives (Prioritized):**
1. Enable Finance Controllers to get instant, accurate answers to cost center questions through natural language — without opening SAP GUI.
2. Enforce per-user identity and S/4HANA authorization on every agent query via IAS principal propagation.
3. Provide a foundation that can be extended to cover additional Controlling queries (budget variance, hierarchy traversal, trend analysis) without rebuilding the agent.

---

## Business Metrics

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Time spent on manual cost center lookups per controller per week | 10h/week | 3h/week (save 7h/week) | — | Cost Center Reporting / Record to Report | user |

---

## User Profiles & Personas

### Primary Persona: Finance Controller

Maria is a 34-year-old Finance Controller at a mid-to-large enterprise. She manages cost center master data, monitors actual spend against budget, and fields daily questions from department heads who want to know where their budgets stand. She is highly proficient in SAP — but that proficiency makes her the go-to person for data that, in principle, requires no expertise to retrieve. She spends an estimated 10 hours per week on manual SAP lookups that could be automated. Maria is pragmatic about AI tools: she will adopt one quickly if it saves her time and gives correct answers, but she will abandon it immediately if it gives wrong data or exposes cost center information to people who should not see it.

**Goals:**
- Answer department questions about cost centers in seconds, not minutes.
- Ensure every answer reflects live S/4HANA data, not a stale export.
- Maintain full confidence that access controls are respected — she should not be able to retrieve data outside her authorization scope, and neither should her colleagues.

**Key Tasks:**
- Ask the agent "how many active cost centers do we have?" and share the answer immediately.
- Ask the agent for the top 5 cost centers by actual spend in the current period.
- Follow up with "tell me more about cost center [X]" to get name, responsible manager, actual costs, and hierarchy position.

### Secondary Persona: Department Manager

David is a 45-year-old operations manager. He does not have SAP access and relies entirely on Finance Controllers to answer his cost center questions. His frustration is with turnaround time — he often needs to wait hours or until the next day for Maria to get back to him. His goal is faster answers, but he is not a direct user of the agent; he benefits indirectly as Maria becomes more responsive.

### Other User Types

- **BTP / Basis Administrator**: Responsible for configuring the IAS–BTP–S/4HANA trust relationship required for principal propagation. Not an end user of the agent.
- **Finance IT Lead**: Oversees rollout and monitors agent behavior in production via observability dashboards.

---

## User Goals & Tasks

### For Finance Controller (Maria):

**Goals:**
- Retrieve live cost center data through conversation, without navigating SAP GUI.
- Trust that every answer reflects her own S/4HANA authorization scope.
- Handle follow-up questions in the same session without re-asking context.

**Key Tasks:**
- Query total count of active cost centers.
- Request a ranked list of top 5 cost centers by actual spend.
- Drill into a specific cost center to retrieve name, responsible person, actual costs, and hierarchy.
- Receive clear error messages when data is unavailable or access is denied.

---

## Product Principles

1. **Live data only**: The agent always queries S/4HANA directly — no caching, no snapshots. Controllers can trust that the answer reflects the current system state.
2. **Identity-first**: Every API call is made under the querying controller's own S/4HANA identity. The agent never uses a shared service account that could bypass authorization rules.
3. **Read-only by design**: The agent retrieves data; it never creates, updates, or deletes records. Financial data integrity is non-negotiable.
4. **Explain the limit**: When the agent cannot answer — due to access denial, missing data, or ambiguous input — it tells the user clearly rather than guessing or returning partial results.
5. **Extensibility from day one**: The initial scope (count, top-5, drill-down) is designed as a launchpad. New query types must be addable without rewiring the agent's core architecture.

---

## Business Context

**Current State:**
Finance Controllers use SAP GUI transactions manually to retrieve cost center data. Common lookups require multiple navigation steps and are not shareable or automatable in their current form. There is no self-service query interface for cost center data in the existing landscape.

**Strategic Alignment:**
This solution advances the organization's goal of enabling AI-assisted finance operations — reducing administrative overhead in the Controlling function and freeing Finance Controllers for higher-value analysis and business partnering.

**Success Criteria:**
See the Business Metrics section.

---

## Goals and Non-Goals

### Goals (In Scope)

- Natural language query of total active cost center count from live S/4HANA data.
- Natural language query of top 5 cost centers ranked by actual spend (current period).
- Natural language drill-down into a specific cost center's details (name, responsible person, actual costs, organizational hierarchy).
- Per-user identity propagation via IAS so S/4HANA authorization objects are enforced per controller.
- Structured observability: all key business steps emit log statements for monitoring.

### Non-Goals (Out of Scope)

- Writing, creating, modifying, or deleting cost center records.
- Budget planning, budget entry, or budget vs. actual variance reporting (future extension).
- Cross-period trend analysis or historical comparisons (future extension).
- Queries on non-cost-center Controlling objects (profit centers, internal orders, WBS elements).
- A dedicated user interface — the agent is accessed via the existing conversational channel.
- IAS–BTP–S/4HANA trust configuration (prerequisite; handled by Basis/BTP admin team separately).

---

## Requirements

### Must-Have Requirements

**R1: Natural Language Cost Center Count**

- **Problem to Solve**: Controllers cannot retrieve the total count of active cost centers without manually running a SAP transaction and counting or exporting results.
- **User Story**: As a Finance Controller, I need to ask how many cost centers exist and receive an accurate, real-time count so that I can answer department questions instantly without opening SAP.
- **Acceptance Criteria**:
  - Given I am authenticated, when I ask "how many cost centers do we have?", then the agent returns the current total count of active cost centers from S/4HANA.
  - Given a variation in phrasing (e.g. "count of cost centers", "total cost centers"), the agent still resolves the intent correctly.
- **Maps to Objective**: Objective 1
- **Priority Rank**: 1

**R2: Top 5 Cost Centers by Actual Spend**

- **Problem to Solve**: Identifying the highest-spending cost centers requires running a custom report in SAP, sorting, and manually extracting the top results — a multi-step process that takes several minutes.
- **User Story**: As a Finance Controller, I need to ask which cost centers have the highest actual spend and receive a ranked top-5 list so that I can quickly identify where costs are concentrated.
- **Acceptance Criteria**:
  - Given I am authenticated, when I ask for the top 5 cost centers by spend, then the agent returns a list of 5 cost centers ranked by total actual costs, including cost center ID, name, and actual cost amount.
  - The ranking reflects live data from S/4HANA at query time.
- **Maps to Objective**: Objective 1
- **Priority Rank**: 2

**R3: Cost Center Detail Drill-Down**

- **Problem to Solve**: After seeing a top-5 list or count result, controllers often need more context on a specific cost center — which requires a separate manual lookup in SAP.
- **User Story**: As a Finance Controller, I need to ask for details on a specific cost center by name or ID and receive its key attributes so that I can answer department questions without switching to SAP GUI.
- **Acceptance Criteria**:
  - Given I reference a specific cost center (by ID or name), when I ask for its details, then the agent returns cost center name, responsible person, actual costs, and organizational hierarchy position.
  - The agent handles follow-up questions within the same conversation session (e.g. "tell me more about the first one").
- **Maps to Objective**: Objective 1
- **Priority Rank**: 3

**R4: Per-User Identity Propagation via IAS**

- **Problem to Solve**: A shared service account would bypass S/4HANA's per-user authorization rules, creating a compliance risk and preventing accurate audit trails of who accessed what data.
- **User Story**: As a Finance Controller, I need my SAP identity to be used for every API call the agent makes so that I can only access cost center data I am authorized to see, and audit logs correctly record my queries.
- **Acceptance Criteria**:
  - Given I am authenticated on BTP, when the agent calls the S/4HANA Cost Center API, then the call is made under my propagated S/4HANA identity via IAS token exchange — not a shared service account.
  - If I request data outside my S/4HANA authorization scope, the agent returns a clear access-denied message rather than partial or incorrect data.
- **Maps to Objective**: Objective 2
- **Priority Rank**: 4

**R5: Graceful Handling of Unavailable Data or Access Denial**

- **Problem to Solve**: If the agent silently returns incomplete data or an empty result when access is denied, controllers may trust incorrect answers.
- **User Story**: As a Finance Controller, I need the agent to clearly tell me when it cannot retrieve data — due to authorization, connectivity, or ambiguous input — so that I do not act on incomplete or missing information.
- **Acceptance Criteria**:
  - Given the S/4HANA API returns an authorization error, when I ask a query, then the agent returns a plain-language message explaining that I do not have access to that data.
  - Given the API is unavailable, when I ask a query, then the agent returns a clear service-unavailable message rather than a generic error or empty result.
- **Maps to Objective**: Objective 1
- **Priority Rank**: 5

### High-Want Requirements

**R6: Controlling Area Awareness**

- **Problem to Solve**: Cost centers exist within Controlling Areas; controllers managing multiple controlling areas need to scope their queries appropriately.
- **User Story**: As a Finance Controller managing multiple controlling areas, I need to specify a controlling area in my question so that the agent returns data scoped to the correct organizational unit.
- **Priority Rank**: 1

**R7: Cost Center Hierarchy Context**

- **Problem to Solve**: Cost centers belong to hierarchies; understanding a cost center's position in the hierarchy is often as important as its spend figures.
- **User Story**: As a Finance Controller, I need the agent to include cost center hierarchy information in drill-down responses so that I can communicate organizational context to department managers.
- **Priority Rank**: 2

---

## Non-Functional Requirements

### Performance

- **Latency**: Agent responses for standard queries (count, top-5, drill-down) must complete within 5 seconds at the 95th percentile under normal load.
- **Throughput**: The agent must support concurrent queries from all active Finance Controllers without degradation.

### Reliability

- **Availability**: The agent inherits the availability of SAP BTP and S/4HANA Cloud Private Edition. Downtime of either upstream system must result in a clear, user-facing message rather than a silent failure.
- **Fallback**: If the S/4HANA API is unreachable, the agent must return a plain-language message and not attempt to answer from cached or fabricated data.

### Explainability

- **Traceability**: Every agent response is traceable to a specific S/4HANA API call. No data is inferred or generated by the LLM without an API backing.
- **Decision Logging**: All milestone events (see Milestones section) are emitted as structured logs and available in the observability dashboard.
- **Uncertainty Communication**: When the agent cannot resolve intent with confidence, it asks a clarifying question rather than guessing.

---

## Solution Architecture

**Architecture Overview:**
A Python AI Agent (A2A protocol) deployed on SAP BTP receives natural language queries from Finance Controllers. It uses an MCP (Model Context Protocol) translation layer — generated from the SAP S/4HANA Cost Center OData API spec — to call the live `CE_COSTCENTER_0001:v1` API. IAS principal propagation ensures each controller's identity is forwarded to S/4HANA on every call.

**Key Components:**

- **Python AI Agent (A2A)**: Core reasoning layer. Interprets natural language, selects the appropriate MCP tool, and formats the response for the controller.
- **MCP Translation Layer**: Generated from the `CE_COSTCENTER_0001:v1` OData API spec. Exposes typed tools (e.g., `get_cost_center_count`, `get_top_cost_centers_by_spend`, `get_cost_center_details`) that the agent calls.
- **SAP S/4HANA Cloud Private Edition**: Source of truth for all cost center data. Queried live on every request.
- **IAS Principal Propagation**: Token exchange between SAP BTP and S/4HANA Cloud Private Edition. Ensures every API call is made under the querying controller's identity, not a shared service account.

**Integration Points:**

- **CE_COSTCENTER_0001:v1 (OData)**: Primary data source for cost center master data and actual costs. Read-only. Called per user query.
- **CE_COSTCENTERHIERARCHY_0001:v1 (OData)**: Secondary source for hierarchy context in drill-down responses. Read-only.
- **IAS Token Exchange Endpoint**: Used at runtime to exchange the controller's BTP JWT for an S/4HANA-trusted token before each API call.

**Deployment Environments:**

- **Development**: Connected to S/4HANA sandbox or non-productive client. No production data.
- **Production**: Connected to S/4HANA productive system. IAS trust fully configured. Per-user authorization enforced.

### Agent Extensibility & Instrumentation

**Agent Extensibility:**
The agent is designed with clearly separated tool definitions (via the MCP translation layer), making it straightforward to add new query capabilities without modifying the agent's core reasoning logic. Planned extension points include:
- Budget vs. actual variance queries (new MCP tool from the same or related API).
- Cross-period trend queries (new MCP tool + time parameter support).
- Cost center hierarchy traversal (MCP tool from `CE_COSTCENTERHIERARCHY_0001:v1`).

**Business Step Instrumentation:**
All key business steps emit structured log statements following the pattern `[MILESTONE_ID].[achieved|missed]: [description]`. These logs feed the observability dashboard and support debugging in production. See the Milestones section for the full list.

### Automation & Agent Behaviour

**Automation Level:** Autonomous agent — the agent determines which tool to call based on natural language input, with no fixed workflow graph.

**Actions the system performs without human approval:**
- Querying cost center count, rankings, and details from S/4HANA.
- Formatting and returning structured responses to the controller.

**Actions that require human review or approval:**
- None. The agent is read-only by design.

**Model or engine used:** Large language model via SAP Generative AI Hub (GPT-4o or equivalent). Tool calls are deterministic; the LLM is used only for intent classification and response formatting.

**Knowledge & data sources accessed:**

- **SAP S/4HANA Cloud Private Edition — Cost Center API**: Live master data and actual cost figures. Owned by the Finance Controlling team.
- **SAP S/4HANA Cloud Private Edition — Cost Center Hierarchy API**: Organizational hierarchy data. Owned by the Finance Controlling team.

**Tools or connectors invoked:**

- `get_cost_center_count` (MCP tool — CE_COSTCENTER_0001): Returns the total count of active cost centers. Read-only.
- `get_top_cost_centers_by_spend` (MCP tool — CE_COSTCENTER_0001): Returns cost centers ranked by total actual costs, with a configurable limit. Read-only.
- `get_cost_center_details` (MCP tool — CE_COSTCENTER_0001): Returns attributes for a specific cost center by ID or name. Read-only.
- `get_cost_center_hierarchy` (MCP tool — CE_COSTCENTERHIERARCHY_0001): Returns hierarchy context for a given cost center. Read-only.

**Guardrails & fail-safes:**

- The agent never writes, creates, modifies, or deletes any S/4HANA records.
- If the S/4HANA API returns an authorization error, the agent surfaces a plain-language access-denied message and does not retry with elevated credentials.
- If the agent cannot resolve the user's intent after one clarifying question, it responds with a scoped list of supported questions rather than attempting a best-guess query.
- If the S/4HANA service is unavailable, the agent returns a service-unavailable message and does not fabricate data.

### Configuration & Data

**Configuration Scope:**
- IAS–BTP–S/4HANA trust relationship must be established before production go-live (Basis/BTP admin responsibility).
- MCP translation file generated from the `CE_COSTCENTER_0001:v1` OData spec and registered with the agent.
- Agent system prompt scoped to cost center querying only — no general-purpose instructions.

**Organisational & Master Data:**
- No master data creation or migration required. The agent reads existing cost center data from S/4HANA.

---

## Governance, Risk & Compliance

**Data Handling:**
- The agent accesses financial master data (cost center names, responsible persons, actual costs). This data is business-sensitive and must not be cached, stored, or logged in full by the agent layer.
- No PII is involved in cost center data retrieval.

**Compliance Frameworks:**
- S/4HANA authorization objects (CO_KOSTL) govern which cost centers each controller can access. The agent enforces this by propagating the user's identity — it cannot bypass SAP's own access controls.
- Audit logs for cost center data access are maintained by S/4HANA's standard logging, with the controller's identity correctly recorded via IAS propagation.

**Approval Flows:**
- No approval flows required; the agent is read-only.

---

## Release Criteria

- **Functionality**: All Must-Have requirements (R1–R5) pass acceptance criteria against a non-productive S/4HANA client.
- **Identity**: IAS principal propagation verified — agent calls confirmed to carry the controller's identity in S/4HANA audit logs.
- **Authorization**: Confirmed that a controller cannot retrieve cost center data outside their S/4HANA authorization scope via the agent.
- **Guardrails**: Access-denied and service-unavailable scenarios both return clear, user-facing messages.
- **Observability**: All five milestone log events confirmed in the observability dashboard during pre-production testing.
- **Read-only**: Confirmed through integration testing that no write operations are possible via the agent's exposed tools.

---

## Milestones

### M1: S/4HANA Data Connectivity Established

- **Description**: The agent successfully authenticates (via IAS principal propagation) and retrieves at least one cost center record from the live S/4HANA Cost Center API.
- **Achieved when**: A test query returns a valid cost center record with no authentication or connectivity errors.
- **Log on achievement**: `M1.achieved: S/4HANA Cost Center API connection established with IAS principal propagation`
- **Log on miss**: `M1.missed: S/4HANA Cost Center API connection failed — check IAS trust configuration and API availability`

### M2: Cost Center Count Query Resolved

- **Description**: The agent correctly interprets a natural language count question and returns the total number of active cost centers from S/4HANA.
- **Achieved when**: The agent returns a numeric count that matches the result of a manual S/4HANA query for active cost centers.
- **Log on achievement**: `M2.achieved: cost center count query resolved successfully — count returned to controller`
- **Log on miss**: `M2.missed: cost center count query did not resolve — intent not classified or API call failed`

### M3: Top 5 Cost Centers by Spend Returned

- **Description**: The agent returns a ranked list of the top 5 cost centers by total actual costs for the current period.
- **Achieved when**: The agent returns exactly 5 cost centers ranked by actual spend, with cost center ID, name, and cost amount, matching S/4HANA data.
- **Log on achievement**: `M3.achieved: top-5 cost centers by spend returned successfully`
- **Log on miss**: `M3.missed: top-5 query did not complete — ranking logic failed or API returned insufficient records`

### M4: Cost Center Detail Drill-Down Answered

- **Description**: The agent responds to a follow-up question about a specific cost center and returns its name, responsible person, actual costs, and hierarchy.
- **Achieved when**: The agent returns all four attributes for the requested cost center in a single response.
- **Log on achievement**: `M4.achieved: cost center detail drill-down completed — all attributes returned`
- **Log on miss**: `M4.missed: cost center detail drill-down incomplete — one or more attributes missing or API call failed`

### M5: Agent Deployed and Accessible to Finance Controllers

- **Description**: The agent is live in the production environment, IAS trust is fully configured, and Finance Controllers can submit queries through the conversational channel.
- **Achieved when**: At least one Finance Controller successfully completes a live query in the production environment with their own S/4HANA identity propagated.
- **Log on achievement**: `M5.achieved: agent live in production — controller identity propagation confirmed`
- **Log on miss**: `M5.missed: production deployment incomplete or IAS trust not validated with real controller identity`

---

## Risks, Assumptions, and Dependencies

### Risks

- **IAS trust configuration delay**: Setting up the IAS–BTP–S/4HANA principal propagation trust requires Basis and BTP admin involvement. Delays here block production go-live.
- **API authorization scope**: If the technical configuration grants the service principal overly broad access during development, controllers may receive data beyond their intended scope during testing.
- **LLM intent classification accuracy**: For unusual phrasings or mixed-language queries, the agent may misclassify intent and call the wrong tool. Mitigation: guardrail that asks a clarifying question when confidence is low.

### Assumptions (Validate These)

- The `CE_COSTCENTER_0001:v1` OData API is available and accessible in the customer's S/4HANA Cloud Private Edition tenant.
- Finance Controllers already have the appropriate S/4HANA authorization objects (CO_KOSTL) assigned for their cost center scope.
- The IAS–BTP trust relationship can be established by the customer's admin team within the project timeline.

### Dependencies

- IAS–BTP–S/4HANA trust configuration (external dependency — Basis/BTP admin team).
- SAP Generative AI Hub availability for the LLM reasoning layer.
- `CE_COSTCENTER_0001:v1` API availability in the target S/4HANA Cloud Private Edition environment.

---

## Appendix

### Glossary

- **Cost Center**: An organizational unit in SAP Controlling that tracks actual costs. Each cost center has a responsible person and belongs to a hierarchy.
- **Actual Costs**: The real expenditure posted to a cost center in the current period, as recorded in S/4HANA.
- **IAS**: SAP Identity Authentication Service — the identity provider that brokers trust between SAP BTP and S/4HANA.
- **Principal Propagation**: The mechanism by which an authenticated user's identity is forwarded from one system (BTP) to another (S/4HANA) without requiring a separate login.
- **MCP (Model Context Protocol)**: A standard that wraps API calls as typed tools consumable by AI agents.
- **A2A (Agent-to-Agent)**: SAP's protocol for deploying and invoking AI agents on BTP.
- **Controlling Area**: The highest organizational unit in SAP Controlling. Cost centers belong to a controlling area.

### References

- SAP S/4HANA Cost Center API: `sap.s4:apiResource:CE_COSTCENTER_0001:v1`
- SAP S/4HANA Cost Center Hierarchy API: `sap.s4:apiResource:CE_COSTCENTERHIERARCHY_0001:v1`
- SAP Identity Authentication Service (IAS) principal propagation documentation
- SAP BTP AI Agent (A2A protocol) documentation
