# Phantom Banking

> Embedded Wallets for the Unbanked – Powered by FNB Botswana

Phantom Banking is a Banking-as-a-Service (BaaS) platform that enables businesses to serve all customers, even the unbanked, by spawning sub-accounts or wallets under their FNB merchant profile. These embedded wallets can accept payments via QR, EFT, and more — with optional KYC upgrades to full accounts.

---

## 🌍 Vision

> Deliver banking-like services without requiring customers to open a personal bank account — by embedding FNB functionality directly into everyday businesses.

---

## ⚙️ Tech Stack

| Layer                 | Tools / Frameworks                                  |
| --------------------- | --------------------------------------------------- |
| Frontend              | React (Vite), Tailwind CSS, Axios                   |
| Backend               | Django, Django REST Framework, PostgreSQL           |
| Documentation         | Docusaurus (docs site), Swagger (API docs), Postman |
| Workflow / Automation | GitHub Projects, Git, BPMN (Camunda-ready)          |
| UI Design             | Figma                                               |

---

## 📦 Monorepo Structure

```
phantom-banking/
├── backend/ # Django backend (API, PostgreSQL)
├── frontend/ # React frontend (Vite)
├── docs/ # Docusaurus-powered documentation site
├── postman/ # Postman collections for API testing
├── swagger/ # OpenAPI/Swagger definitions
├── bpmn/ # BPMN process flows for future automation
├── scripts/ # Init scripts, deployment, etc.
└── README.md # This file
```

yaml
Copy
Edit

---

## 🚀 MVP Features

-   🔐 Business dashboard to manage embedded wallets and transactions
-   📲 Multi-channel payment support: QR, EFT
-   🧩 API & SDK for integration into POS systems or apps
-   🆙 KYC upgrade path to transition wallets into full FNB accounts

---

## 🔁 Future Integrations

-   ✅ KYC Verification Flow (Manual + API)
-   🌐 Cross-border payments (regional expansion)
-   🔄 Camunda BPMN workflows for scalable automation

---

## 👥 Core Team

| Name              | Role                          | Skills                                             |
| ----------------- | ----------------------------- | -------------------------------------------------- |
| Goitseone Themba  | Lead / Fullstack              | React, APIs, DevOps, Architecture                  |
| Bakang Kgopolo    | ML & Automation               | Python, ML, Instrumentation, Research              |
| Thabo Mantsima    | Backend & Systems Integration | Django, Automation, Industrial Instrumentation     |
| Oarabile Koore    | Frontend                      | React, Typescript, Mobile app Dev with DroidScript |
| Lebang Garebantsi | Security & Networking         | Fullstack, API Security, Network Admin             |

---

## 📘 Setup Guide

> Follow instructions in the respective backend/ and frontend/ folders to set up the dev environment.

Clone the repository:

```bash
git clone https://github.com/Goitseone-Themba/phantom-banking.git
cd phantom-banking
```

📄 License
This project is for educational and demo purposes for the FNB "Bank of the Future" Hackathon 2025. Commercial use requires approval from the core team and FNB Botswana.

📫 Contact
For questions or collaborations, reach out via GitHub issues or email: goitseonerozthemba@gmail.com .

vbnet
Copy
Edit

Would you like me to add badges (e.g. build status, license, etc.), or generate a versioned changelog/roadmap next?
