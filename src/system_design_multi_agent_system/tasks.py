"""The 9 pipeline tasks.

Tasks run strictly sequentially. Each task passes its output forward via the
`context` list, so every agent builds on the full accumulated knowledge of all
prior agents.
"""

from crewai import Task

from .agents import (
    api_designer,
    capacity_estimator,
    critic,
    data_modeler,
    reliability_engineer,
    requirements_analyst,
    scalability_engineer,
    synthesizer,
    system_architect,
)

requirements_task = Task(
    description=(
        "Analyze the following system design prompt and produce a structured requirements document.\n\n"
        "User Prompt: {user_prompt}\n\n"
        "Your output must include:\n"
        "1. **Functional Requirements** — Core features the system must support (5-8 items)\n"
        "2. **Non-Functional Requirements** — Scale targets, latency SLA, availability SLA, consistency model\n"
        "3. **User Personas** — Who uses this system and what their primary interaction looks like\n"
        "4. **Assumptions** — What you are assuming because it is not stated in the prompt\n"
        "5. **Out of Scope** — What this design will deliberately NOT cover"
    ),
    expected_output=(
        "A structured requirements document with five clearly labeled sections: "
        "functional requirements, non-functional requirements, user personas, assumptions, out of scope."
    ),
    agent=requirements_analyst,
)

capacity_task = Task(
    description=(
        "Using the requirements document, perform back-of-envelope capacity calculations.\n\n"
        "Show your working for each item below:\n"
        "1. **Users** — DAU and MAU\n"
        "2. **Traffic** — Average and peak Read QPS, Average and peak Write QPS\n"
        "3. **Storage** — Size per record, daily writes, 5-year total\n"
        "4. **Bandwidth** — Inbound and outbound\n"
        "5. **Servers** — Estimated application and database server counts\n"
        "6. **Ratios** — Read:Write ratio, hot vs cold data split\n\n"
        "End with a summary table of all key numbers."
    ),
    expected_output=(
        "A capacity estimation report with step-by-step calculations, explicit assumptions, "
        "and a summary table of all key metrics."
    ),
    agent=capacity_estimator,
    context=[requirements_task],
)

architecture_task = Task(
    description=(
        "Design the high-level system architecture using the requirements and capacity estimates.\n\n"
        "1. **Architecture Style** — Microservices / Monolith / Serverless with explicit justification\n"
        "2. **Core Components** — Each service or component with its single clear responsibility\n"
        "3. **Component Diagram** — Full system topology in Mermaid notation (graph TD)\n"
        "4. **Request Flow** — End-to-end walkthrough of a typical user request\n"
        "5. **External Dependencies** — CDN, object storage, third-party and cloud services\n"
        "6. **Communication** — Where to use synchronous (REST/gRPC) vs asynchronous (queues) and why"
    ),
    expected_output=(
        "An architecture document with a component list, a Mermaid graph TD diagram, "
        "an end-to-end request flow, and justification for every key architectural decision."
    ),
    agent=system_architect,
    context=[requirements_task, capacity_task],
)

data_model_task = Task(
    description=(
        "Design the data model and database strategy, building on the architecture decisions.\n\n"
        "1. **Database Choices** — Which database(s) (SQL/NoSQL/Cache/Search) and why for each\n"
        "2. **Core Schemas** — Key tables or collections with fields and data types\n"
        "3. **Indexing Strategy** — Primary and secondary indexes for the main query patterns\n"
        "4. **Partitioning** — How data is sharded or partitioned across nodes\n"
        "5. **Access Patterns** — The 3-5 most critical read and write operations\n"
        "6. **Data Lifecycle** — Archival policy, TTL settings, hot/warm/cold tiers"
    ),
    expected_output=(
        "A data modeling document with justified database selections, schema definitions, "
        "indexing strategy, partitioning approach, and data lifecycle policy."
    ),
    agent=data_modeler,
    context=[requirements_task, capacity_task, architecture_task],
)

api_design_task = Task(
    description=(
        "Design the API contracts, consistent with the architecture and data model.\n\n"
        "1. **API Style** — REST, GraphQL, or gRPC with explicit justification\n"
        "2. **Core Endpoints** — Method, path, request body, response schema, status codes\n"
        "3. **Authentication** — Auth mechanism (JWT/OAuth2/API keys) and authorization model\n"
        "4. **Rate Limiting** — Limits per endpoint, per user, per tenant\n"
        "5. **Versioning** — Versioning strategy (URL path, header, or query param)\n"
        "6. **Error Handling** — Standard error response format with machine-readable codes"
    ),
    expected_output=(
        "An API design document with OpenAPI-style endpoint specs, auth strategy, "
        "rate limiting rules, versioning approach, and error response format."
    ),
    agent=api_designer,
    context=[requirements_task, capacity_task, architecture_task, data_model_task],
)

scalability_task = Task(
    description=(
        "Design the scalability strategy to handle the estimated load and traffic peaks.\n\n"
        "1. **Load Balancing** — Algorithm and layer (L4/L7) with configuration details\n"
        "2. **Caching** — What to cache, where (client/CDN/app/DB), and invalidation strategy\n"
        "3. **Horizontal Scaling** — Auto-scaling policies and stateless service design\n"
        "4. **Database Scaling** — Read replicas, write sharding, connection pooling\n"
        "5. **Async Processing** — Queue-based offloading for non-latency-critical operations\n"
        "6. **Rate Limiting** — Protecting downstream services from traffic spikes"
    ),
    expected_output=(
        "A scalability document covering caching with invalidation, load balancing config, "
        "auto-scaling rules, database scaling approach, and async processing patterns."
    ),
    agent=scalability_engineer,
    context=[requirements_task, capacity_task, architecture_task, data_model_task, api_design_task],
)

reliability_task = Task(
    description=(
        "Design the reliability, fault tolerance, and observability strategy.\n\n"
        "1. **Failure Modes** — Top 5 failure scenarios and exactly how the system handles each\n"
        "2. **Replication** — Data replication strategy and consistency guarantee\n"
        "3. **Circuit Breakers & Retries** — Where to apply, timeout values, backoff policies\n"
        "4. **Disaster Recovery** — RTO and RPO targets, backup strategy, multi-region failover\n"
        "5. **Observability** — Key metrics (RED/USE), alert thresholds, distributed tracing\n"
        "6. **Deployment** — Blue-green, canary, or rolling deployment with rollback plan"
    ),
    expected_output=(
        "A reliability document covering failure modes, replication strategy, "
        "circuit breaker config, DR plan with RTO/RPO targets, and observability stack."
    ),
    agent=reliability_engineer,
    context=[
        requirements_task, capacity_task, architecture_task,
        data_model_task, api_design_task, scalability_task,
    ],
)

critique_task = Task(
    description=(
        "Review all seven specialist documents and produce a critical assessment.\n\n"
        "1. **Bottlenecks** — Where will the system degrade or break under load?\n"
        "2. **Single Points of Failure** — Which components take the whole system down if they fail?\n"
        "3. **Consistency Gaps** — Where could data become stale or inconsistent?\n"
        "4. **Missing Pieces** — What critical components are absent from any specialist design?\n"
        "5. **Over-Engineering** — Where is complexity unjustified by the requirements?\n"
        "6. **Trade-offs** — What important trade-offs were made explicitly or left implicit?\n"
        "7. **Recommendations** — Specific fixes labeled High / Medium / Low priority"
    ),
    expected_output=(
        "A critical review with issues labeled by severity (High/Medium/Low), "
        "identified trade-offs with implications, and concrete prioritized recommendations."
    ),
    agent=critic,
    context=[
        requirements_task, capacity_task, architecture_task,
        data_model_task, api_design_task, scalability_task, reliability_task,
    ],
)

synthesis_task = Task(
    description=(
        "Synthesize all eight specialist outputs into one final system design document.\n\n"
        "Use exactly this structure:\n\n"
        "# System Design: [System Name]\n\n"
        "## 1. Requirements\n"
        "## 2. Capacity Estimation\n"
        "## 3. High-Level Architecture\n"
        "## 4. Data Model\n"
        "## 5. API Design\n"
        "## 6. Scalability\n"
        "## 7. Reliability & Fault Tolerance\n"
        "## 8. Key Trade-offs & Design Decisions\n"
        "## 9. Future Improvements\n\n"
        "Rules:\n"
        "- Include the Mermaid diagram from the architect verbatim in section 3\n"
        "- Include the summary table from the capacity estimator verbatim in section 2\n"
        "- Integrate the critic's findings into section 8\n"
        "- Resolve any contradictions between specialist outputs\n"
        "- The result must be ready for a system design interview or an internal RFC"
    ),
    expected_output=(
        "A complete Markdown system design document with all 9 sections, "
        "the Mermaid diagram, capacity table, API specs, and trade-offs documented."
    ),
    agent=synthesizer,
    context=[
        requirements_task, capacity_task, architecture_task, data_model_task,
        api_design_task, scalability_task, reliability_task, critique_task,
    ],
)

# Ordered list matching the sequential pipeline
ALL_TASKS = [
    requirements_task,
    capacity_task,
    architecture_task,
    data_model_task,
    api_design_task,
    scalability_task,
    reliability_task,
    critique_task,
    synthesis_task,
]

# (title, task) pairs for the 8 specialist tasks — excludes the final synthesis
SPECIALIST_SECTIONS = [
    ("1. Requirements Analysis", requirements_task),
    ("2. Capacity Estimation", capacity_task),
    ("3. System Architecture", architecture_task),
    ("4. Data Model", data_model_task),
    ("5. API Design", api_design_task),
    ("6. Scalability", scalability_task),
    ("7. Reliability", reliability_task),
    ("8. Critique", critique_task),
]
