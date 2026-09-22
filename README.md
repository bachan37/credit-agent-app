### Run Server
```
uv run python -m credit_agent_app.main server
```

### project description 
```
Loan Eligibility Assessment is a system that assesses the eligibility of an individual for a loan based on their credit information and financial details.

The system uses a rule-based approach to determine eligibility and provides a loan eligibility report.

Key Features:

Credit score retrieval from static API

Loan eligibility calculation

Interest rate determination

Loan tenure calculation

Eligibility status determination

Supports multiple banks/lenders

Credit score based interest rate

Supports multiple loan products

Can be extended to support multiple lenders

Use Case:

A loan officer or loan officer's assistant can use this system to quickly assess the eligibility of an individual for a loan.

Example Interaction:

User inputs the applicant's PAN number.

The system retrieves the applicant's credit information from the static API.

The system calculates the applicant's loan eligibility based on their credit information and financial details.

The system returns a loan eligibility report that includes:

Eligible loan amount

Applicable interest rate

Recommended loan tenure

Eligibility status

Status of each check
```

### Code structure
<ol>
    <li>tools - contains tools that can be used by the agent.</li>
    <li>pipelines - contains pipelines that can be used by the agent.</li>
    <li>agents - contains agents that can be used by the agent.</li>
    <li>models - contains models that can be used by the agent.</li>
    <li>api - contains API endpoints that can be used by the agent.</li>
    <li>config - contains configuration for the agent.</li>
<ol>
