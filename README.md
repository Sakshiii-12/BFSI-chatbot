# BFSI Chatbot - Agentic AI for Personal Loan Sales

The **BFSI Chatbot** is an Agentic AI solution designed to simulate an intelligent loan officer for Non-Banking Financial Companies (NBFCs).  
It automates the personal loan process—from customer engagement and KYC verification to credit evaluation and sanction letter generation—through a conversational interface.

The chatbot is designed to handle multiple customers simultaneously and maintain context throughout the interaction. It provides a personalized, human-like experience by dynamically responding to user inputs, evaluating eligibility, and guiding applicants through each step of the loan process.  
This system demonstrates how modular AI agents can collaboratively deliver complex financial services efficiently while ensuring compliance with predefined business rules.

Developed for **EY Techathon 6.0 – Challenge II: BFSI (Tata Capital)**, it showcases how Agentic AI principles can improve operational efficiency, reduce processing time, and enhance the digital customer experience.


# Project Structure

```
bfsi_chatbot/
│
├── app.py                        # Main router (login → customer/manager dashboards)
├── config.py                     # App settings, credentials
├── requirements.txt
│
├── data/
│   ├── demo_customers.json       # Sample customer dataset
│   └── kyc_data.json             # Demo PAN/salary slip/KYC store
│
├── outputs/
│   ├── decision_traces.jsonl     # Audit logs for every loan decision
│   ├── manual_review.jsonl       # Pending conditional cases for managers
│   └── sanction_letters/         # Auto-generated PDF sanction letters
│
├── agents/                       # Core Agentic AI System
│   ├── master_agent.py           # Orchestrates the full pipeline
│   ├── sales_agent.py            # Conversational offer & upsell logic
│   ├── verification_agent.py     # PAN/KYC verification + document checks
│   ├── underwriting_agent.py     # NBFC rule engine (EMI rules, risk, scoring)
│   ├── sanction_agent.py         # Sanction letter PDF generator
│   └── utils.py                  # EMI calc + helper functions
│
├── services/                     # Mock APIs & intelligence components
│   ├── credit_bureau.py          # Mock credit score service
│   ├── offer_mart.py             # Pre-approved loan offer catalog
│   ├── crm_mock.py               # Dummy CRM lookup
│   ├── doc_intel.py              # Document intelligence (PAN/salary slip)
│   ├── fraud_detection.py        # Optional anomaly/fake-doc checks
│   ├── recommender.py            # Loan recommendation engine
│   ├── scenario_compare.py       # A/B scenario comparison logic
│   └── xai.py                    # Explainable decisioning module
│
├── chat/
│   ├── chat_ui.py                # WhatsApp-style chat interface
│   ├── nlu.py                    # Intent detection + entity extraction
│   └── llm_stub.py               # Fallback LLM response generator
│
├── ui/
│   ├── theme.py                  # Global CSS, theme colors, styling
│   ├── auth_page.py              # Login screen
│   ├── customer_page.py          # Customer dashboard
│   ├── manager_page.py           # Manager dashboard (audit + reviews)
│   └── ui_components.py          # Reusable cards, KPIs, tables
```


# Login Credentials

| Role     | Email                                             | Password        |
| -------- | ------------------------------------------------- | --------------- |
| Customer | **[customer@nbfc.com](mailto:customer@nbfc.com)** | **Customer789** |
| Manager  | **[manager@nbfc.com](mailto:manager@nbfc.com)**   | **Manager456**  |

---

# How to Use the Application

### **1. Install dependencies**

```bash
pip install -r requirements.txt
```

### **2. Run the app**

```bash
streamlit run app.py
```

### **3. Log in using customer or manager credentials**

* **Customer** → Loan simulation, chat assistant, scenario comparison
* **Manager** → Audit logs, operational dashboard, manual case decisions

### **4. Explore the system**

* Customers can:

  * Chat with the loan assistant (“I need 3 lakh for medical”)
  * Run structured EMI calculations
  * Compare two loan scenarios
  * View portfolio summary & past activity

* Managers can:

  * Check all previous customer decisions
  * See explainable reasoning (XAI)
  * Export audit logs
  * Approve or reject conditional cases


# Overview

This project simulates a **real NBFC underwriting workflow** using an **Agentic AI system**:

1. **Sales Agent**
   Extracts intent, amounts, reasons, upsell suggestions.

2. **Verification Agent**
   PAN/KYC checks, salary slip parsing, fraud flags.

3. **Underwriting Agent**
   EMI rules, affordability checks, risk scoring, explainability.

4. **Sanction Agent**
   Generates a professional sanction letter (PDF).

All actions are logged in JSONL, offering complete auditability.


# Features

### Customer-Facing

* WhatsApp-style clean chat interface
* Conversational loan advisory
* EMI calculation & eligibility decision
* Multi-scenario loan comparison
* Auto-generated sanction letter
* Clean dashboard with donut analytics
* Salary, credit score, risk-based evaluation
* Transparent rule-based explanations (XAI)

### Manager-Facing

* Manager dashboard with key metrics
* Manual review queue for conditional cases
* Approve/reject decisions with notes
* Audit trail viewer (decision history)
* Export logs (CSV / JSON)
* Color-coded decision tables & KPIs

### AI & Logic

* Multistage Agentic workflow
* Intent extraction (NLU)
* Document intelligence (PAN / salary slip)
* Fraud anomaly checks
* Rule-driven underwriting + risk scoring
* Fully explainable decisions (XAI)

### UI / UX

* Clean sidebar navigation
* Uniform theme + custom styling
* Compact layouts with minimal whitespace
* Responsive cards & KPIs
* Donut charts with NBFC-appropriate colors
