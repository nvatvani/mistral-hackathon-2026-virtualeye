# VirtualEye: Privacy-First CCTV Intelligence & Accessibility

Welcome to **VirtualEye**, a concept project built for the 2026 Hackathon showcasing real-world, high-impact use-cases of local Large Language Models (LLMs). This project focuses on delivering powerful, privacy-preserving AI tools directly at the edge, requiring no cloud dependencies so that privacy is maximised; and the solution easily becomes GDPR compliant by having to shed data to continue local operations.

## 🚀 The Concepts

This project integrates two distinct yet powerful AI-driven capabilities into a single seamless application:

### 1. The "Blind-Accessibility" Assistant
An assistant designed to help visually impaired users navigate complex software interfaces or physical environments. Users upload a screenshot of a UI or a photo of a room.
- **The Logic:** The LLM provides a high-detail spatial description (*"There is a button in the top right labeled 'Save', and a search bar in the center"*).
- **Hackathon Hook:** *"AI-driven inclusivity at the edge."*

### 2. The "Virtual Eye" CCTV Incident Reporter
A portal that performs **Temporal Reasoning** on still frames. Instead of describing images in isolation, the model analyzes the delta (change) between them to infer critical events.
- **The Logic:** *"In Image 1, the gate is closed. In Image 2, the gate is open and a person is running."*
- **Output:** `RED (Significant Event) – Unauthorized entry detected via gate breach.`
- **Hackathon Hook:** *"Local, private security intelligence without the cloud."*

## 🛠️ Project Framework

- **Local LLM Backend:** Interactions are powered by Mistral's vision-compatible model `mistralai/ministral-3-14b-reasoning` hosted locally via [LMStudio](https://lmstudio.ai). The API endpoint is locally available at `http://192.168.1.3:1234/`.
- **Frontend/Web Framework:** A lightweight, stateless Python-driven web application.
- **Authentication:** Strict login requirement per session. Credentials are securely managed via a plain-text file storing usernames and hashed passwords.
- **Hosting & Deployment:** The application relies entirely on static resources, allowing it to be continuously built and deployed via **GitHub Actions** and hosted on **GitHub Pages**.

### Repository Structure

```text
mistral-hackathon-2026-virtualeye/
├── .github/
│   └── workflows/          # GitHub Actions CI/CD pipelines
├── app/                    # Main application source code
│   ├── index.html          # Entry point for the static web app
│   ├── config.json         # Configuration file for endpoints
│   ├── static/             # CSS styling variables
│   │   └── style.css
│   ├── auth/               # PyScript application logic logic
│   │   └── main.py
│   └── data/               # Plain-text data models
│       └── users.txt       # Plain-text credentials file (username:hashed_password)
├── pyproject.toml          # Project dependencies
├── LICENSE                 # Apache 2.0 License
└── README.md               # Project documentation
```

## 💻 Quick Start

### Prerequisites
- [LMStudio](https://lmstudio.ai/) running locally on `192.168.1.3` at port `1234`, with a Vision-compatible model loaded.
- [uv](https://github.com/astral-sh/uv) (Extremely fast Python package installer and resolver).

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nvatvani/mistral-hackathon-2026-virtualeye.git
   cd mistral-hackathon-2026-virtualeye
   ```

2. **Initialize a virtual environment:**
   Use `uv` to create a virtual environment with a custom prompt.
   ```bash
   uv venv --prompt "mistral-hackathon-2026-virtualeye"
   ```

3. **Activate the environment:**
   - **Linux/macOS:**
     ```bash
     source .venv/bin/activate
     ```
   - **Windows:**
     ```cmd
     .venv\Scripts\activate
     ```

4. **Install dependencies:**
   Using `uv`, sync the necessary project requirements from `pyproject.toml`.
   ```bash
   uv pip sync pyproject.toml
   ```

5. **Start the local server:**
   Ensure LMStudio is running, then serve the static application locally for testing (using port 8080 to avoid common local conflicts):
   ```bash
   python -m http.server 8080 --directory app
   ```
   Navigate to `http://localhost:8080` in your browser.

## 📄 License
This project is licensed under the **Apache 2.0 License** - see the [LICENSE](LICENSE) file for details.
