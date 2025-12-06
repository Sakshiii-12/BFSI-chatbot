# BFSI Chatbot - Agentic AI for Personal Loan Sales

The **BFSI Chatbot** is an Agentic AI solution designed to simulate an intelligent loan officer for Non-Banking Financial Companies (NBFCs). It automates the personal loan process from customer engagement and KYC verification to credit evaluation and sanction letter generation—through a conversational interface.

The chatbot is designed to handle multiple customers simultaneously and maintain context throughout the interaction. It provides a personalized, human-like experience by dynamically responding to user inputs, evaluating eligibility, and guiding applicants through each step of the loan process. This system demonstrates how modular AI agents can collaboratively deliver complex financial services efficiently while ensuring compliance with predefined business rules.

Developed for **EY Techathon 6.0 – Challenge II: BFSI (Tata Capital)**, it showcases how Agentic AI principles can improve operational efficiency, reduce processing time, and enhance the digital customer experience.


## 1. Problem Overview

The NBFC aims to increase conversions on personal loan applications sourced through digital channels. To achieve this, the system provides an interactive chatbot that behaves like a human sales executive, understands customer needs, and coordinates multiple back-end agents to complete the end-to-end personal loan journey:

1. Conversational engagement and need discovery
2. Sales negotiation and offer discussion
3. Verification checks (KYC, PAN, salary slip)
4. Credit bureau score retrieval
5. Underwriting based on defined eligibility rules
6. Sanction letter generation for approved applications

The system must demonstrate realistic orchestration between agents, reproducible decisions, auditability, and the ability to handle edge cases such as rejections and conditional approvals.



## 2. Key Features

### Agentic Architecture

* **Master Agent** orchestrates the complete loan workflow and manages conversation flow.
* **Sales Agent** discusses loan needs, amounts, and recommends suitable offers.
* **Verification Agent** performs KYC checks using a mock CRM, extracts PAN and salary from uploaded documents, and detects anomalies.
* **Underwriting Agent** applies NBFC underwriting rules and produces structured decisions.
* **Sanction Letter Agent** generates PDF sanction letters for approved applications.

### End-to-End Loan Pipeline

* Customer describes their loan requirement through chat or form inputs.
* Master Agent triggers worker agents and compiles their outputs into a unified decision trace.
* Decisions include EMI calculation, EMI-to-salary percentage, rule firing explanations, and risk scoring.

### Credit and Offer Systems

* Mock credit bureau API returning deterministic scores.
* Offer Mart server providing tiered loan offers.
* Recommender to prioritize offers based on credit strength and applicant profile.

### Document Intelligence

* PAN extraction via regex.
* Salary inference from uploaded PDF or images.
* Simple fraud detection using document anomalies.

### User Interfaces (Streamlit)

* **Customer Dashboard**
  Loan simulation, chat interface, sanction letter downloads, activity tracking.
* **Manager Dashboard**
  Audit logs, data exports, manual review queue for conditional approvals.

### Auditability and Explainability

* All decisions logged in `outputs/decision_traces.jsonl`.
* Conditional cases logged in `outputs/manual_review.jsonl`.
* XAI module produces risk scores and rule-based explanations.
* Sanction letters include decision rationale and conversation transcript.

### Edge Case Handling

* Automatic rejection for low credit score.
* Conditional decisions requiring salary slip upload.
* Rejection when requested amount exceeds 2× pre-approved limit.
* Fraud anomaly flagging via PAN mismatch.



## 3. Project Structure

```
bfsi_chatbot/
├── app.py
├── config.py
├── requirements.txt
├── data/
│   ├── demo_customers.json
│   └── kyc_data.json
├── agents/
│   ├── master_agent.py
│   ├── sales_agent.py
│   ├── verification_agent.py
│   ├── underwriting_agent.py
│   ├── sanction_agent.py
│   └── utils.py
├── services/
│   ├── credit_bureau.py
│   ├── crm_mock.py
│   ├── doc_intel.py
│   ├── fraud_detection.py
│   ├── offer_mart.py
│   ├── recommender.py
│   ├── audit.py
│   ├── report_generator.py
│   └── xai.py
├── api/
│   └── mock_server.py
├── chat/
│   ├── chat_ui.py
│   ├── nlu.py
│   └── llm_stub.py
├── ui/
│   ├── auth_page.py
│   ├── customer_page.py
│   ├── manager_page.py
│   └── theme.py
├── tests/
│   └── test_utils.py
└── outputs/
    ├── sanction_letters/
    ├── decision_traces.jsonl
    └── manual_review.jsonl
```



## 4. How to Run

### Install dependencies

```
pip install -r requirements.txt
```

### Start the application

```
streamlit run app.py
```

### Login Credentials

These demo credentials are defined in `config.py`:

**Customer**
Email: `customer@nbfc.com`
Password: `Customer789`

**Manager**
Email: `manager@nbfc.com`
Password: `Manager456`



## 5. How to Use

### Customer Mode

1. Sign in as a customer.
2. Navigate using the sidebar:

   * **Overview**: Profile summary and recent loan decisions
   * **Compare**: Run two loan scenarios side-by-side
   * **Simulate**: Run structured loan checks, upload salary slips, view decisions
   * **Chat**: Interact with the loan assistant using natural language
3. If approved, download the sanction letter PDF.

### Manager Mode

1. Sign in as a manager.
2. Explore:

   * **Overview**: Global KPIs and export options
   * **Audit**: View historical decision logs
   * **Manual Reviews**: Approve or reject conditional cases
3. All actions are logged for audit compliance.



## 6. Underwriting Rules Implemented

1. **Credit Score Rule**

   * If credit score < 700 → Reject.

2. **Within Pre-Approved Limit**

   * If requested amount ≤ pre-approved limit → Approve instantly.

3. **Moderate Risk Band (≤ 2× Pre-Approved)**

   * Requires salary verification.
   * Approve only if EMI ≤ 50 percent of monthly salary.
   * Otherwise reject.

4. **High-Risk Band (> 2× Pre-Approved)**

   * Reject automatically.



## 7. Data and Mock Systems

* Demo Customer Data - 
  At least 10 synthetic customers with salary, credit score, pre-approved amounts, PAN.

* CRM Mock Server - 
  Provides PAN, address, phone, salary.

* Credit Bureau API - 
  Mock deterministic score between 620 and 820.



## 8. PDF Generation

Sanction letters include:

* Applicant details
* Decision summary
* EMI and EMI-to-salary ratio
* Rules fired
* Risk score
* Conversation transcript

Unicode sanitization and optional TTF font support ensure reliable PDF creation.



## 9. Testing

Unit tests available in `tests/test_utils.py` include:

* EMI calculation
* Loan rejection based on credit score
* Additional recommended tests for full underwriting logic

Run using:

```
pytest
```


## 10. Limitations and Assumptions

* Document extraction uses regex-based heuristics, not OCR.
* Recommender logic is simplified but demonstrates offer-based reasoning.
* Sales Agent behavior is template-driven rather than LLM-powered.
* Mock systems simulate real banking back-ends and are not meant for production use.


## 11. Future Improvements

* Integrate real OCR for document extraction.
* Add more advanced LLM-based sales negotiation.
* Support multilingual chat flows.
* Add complex fraud scoring models.
* Replace mock APIs with real banking systems.
