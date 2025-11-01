# 🤖 Autonomous RPA Monitoring with CrewAI

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Latest-green)](https://www.crewai.com/)
[![License](https://img.shields.io/badge/License-MIT-purple)](LICENSE)
![Autonomous RPA Monitoring with CrewAI Diagram](https://ik.imagekit.io/azeveytqm/Gemini_Generated_Image_d93kegd93kegd93k.jpeg?updatedAt=1761995712549)

## ✨ Overview

This project demonstrates an innovative approach to **autonomous RPA monitoring and debugging** by integrating **CrewAI** (an AI Agent orchestration framework) with **UiPath Orchestrator** and **Kibana (Elasticsearch)**.

This solution automates the entire manual debugging process using a team of specialized AI agents running **100% locally** on your machine. Given a UiPath Job ID, the CrewAI agents will:

1.  **Fetch Job Details:** Connect to UiPath Orchestrator to retrieve comprehensive data for the specified job.
2.  **Extract Key Information:** Identify critical identifiers like `RobotName` and `BatchExecutionKey` from the job data.
3.  **Query Kibana:** Use the extracted information to intelligently search Kibana (Elasticsearch) for relevant logs.
4.  **Provide Analysis:** Present a consolidated summary of job details and associated logs, including any errors, for rapid debugging.

This project bridges the gap between RPA operations and IT observability, paving the way for more resilient and self-diagnosing automation processes.

## 🚀 Features

* **Autonomous Agent Workflow:** A CrewAI team orchestrates the entire monitoring process.
* **Local & Swappable LLM:** Powered by **Ollama**, allowing you to run any open-source model (e.g., Llama 3, Mixtral, Phi3) locally. This eliminates API costs and ensures data privacy.
* **UiPath Orchestrator Integration:** Custom tool for secure (OAuth 2.0 Client Credentials) API access to UiPath job data.
* **Kibana/Elasticsearch Integration:** Custom tool for secure (API Key) querying of logs based on dynamic criteria.
* **Dynamic Input:** Easily specify the UiPath Job ID you want to investigate.
* **Detailed Logging:** `verbose` mode provides insight into agent thinking processes and tool usage.

## ⚙️ How It Works

The system operates as a sequential CrewAI workflow:

1.  **UiPath Orchestrator Agent (Researcher):**
    * **Goal:** Fetch details for a given UiPath Job ID.
    * **Tool:** `get_uipath_job_data` (Custom Python tool that handles OAuth authentication and Orchestrator API calls).
    * **Output:** Comprehensive JSON data of the UiPath job.

2.  **Kibana Analyst Agent (Writer):**
    * **Goal:** Analyze the UiPath job data and query Kibana for relevant logs.
    * **Tool:** `query_kibana_logs` (Custom Python tool that handles Elasticsearch API Key authentication and log searching).
    * **Input:** The JSON output from the UiPath Orchestrator Agent.
    * **Output:** A summary of logs found in Kibana, highlighting key information for debugging.


## 🛠️ Technologies Used

* **Python 3.10+**
* **CrewAI**: For orchestrating intelligent agents.
* **Ollama**: To run local Large Language Models (LLMs).
* **Llama 3**: The **default** LLM model used locally (this is easily swappable for any other model in Ollama).
* **`requests`**: For making HTTP requests to APIs.
* **`langchain-community`**: Provides the DuckDuckGo search tool (optional, for general research).

## 🚀 Getting Started

Follow these steps to set up and run the project on your Mac.

### Prerequisites

* **macOS with M-series chip (recommended for Ollama performance)**
* **Python 3.10+** installed.
* **UiPath Automation Cloud Account:** With permissions to create External Applications.
* **Kibana/Elasticsearch Instance:** With permissions to create API Keys and access to your UiPath logs index.

### 1. Install `uv` and Project Dependencies

`uv` is a fast Python package manager and installer.

```bash
# Install uv (if you haven't already)
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh

# Navigate into your project directory (if you're not already there)
cd my_first_crew

# Install CrewAI and all necessary tools within a virtual environment
# This command installs CrewAI, crewai[tools] for DuckDuckGo, and other dependencies
uv add requests duckduckgo-search langchain-community
```
### 2. Set Up Ollama

This project uses Ollama to run any open-source model locally.

Download & Install Ollama: Go to https://ollama.com, download the macOS application, and install it.

Run Ollama App: Launch the Ollama application. It should run in your menu bar.

Download a Model: Open your terminal and pull the default model (Llama 3). You can pull any other model you wish to use.

```bash
ollama pull llama3  # Default
ollama pull mixtral # Alternative
```
### 3. Configure API Credentials (Environment Variables)

This project requires API access to UiPath Orchestrator and Kibana. For security, these should be set as environment variables in your terminal before running the script.

**UiPath Orchestrator (OAuth 2.0 Client Credentials)**

**1. Generate Credentials:**

* Log into your UiPath Automation Cloud.

* Navigate to Admin > External Applications > Add Application.

* Choose Confidential Application.

* Add relevant Scopes (e.g., OR.Jobs.Read, OR.Queues.Read).

* Copy the Client ID and Client Secret immediately (the secret is shown only once).

**2. Set Environment Variables:**
```bash
export UIPATH_CLIENT_ID="your_client_id_from_uipath"
export UIPATH_CLIENT_SECRET="your_client_secret_from_uipath"
export UIPATH_ACCOUNT_NAME="your_account_logical_name_from_url" # e.g., 'yourcompany'
export UIPATH_TENANT_NAME="your_tenant_name_from_url"           # e.g., 'DefaultTenant'
```
**Kibana / Elasticsearch (API Key)**
 **1. Generate API Key:**
 
* Log into your Kibana instance.

* Go to Management > Dev Tools.

* Execute the following command, adjusting the `names` array to your log index (e.g., `uipath-logs-*`):

```JSON
POST /_security/api_key
{
  "name": "crewai_monitor_key",
  "role_descriptors": {
    "crewai_reader": {
      "cluster": ["monitor"],
      "index": [
        {
          "names": ["uipath-logs-*"],
          "privileges": ["read", "view_index_metadata"]
        }
      ]
    }
  }
}
```
* Copy the `id` and `api_key` from the response immediately.
**2. Set Environment Variables:**
``` Bash
export KIBANA_API_ID="your_api_key_id_from_kibana_response"
export KIBANA_API_SECRET="your_api_key_secret_from_kibana_response"
export KIBANA_HOST="[https://your-elastic-cluster.co](https://your-elastic-cluster.co)" # e.g., [https://abcde12345.es.amazonaws.com:9200](https://abcde12345.es.amazonaws.com:9200)
export KIBANA_INDEX="uipath-logs-*" # The Elasticsearch index where your UiPath logs are stored
```
### 4. Run the Crew
1. Update `run.py`: Open `run.py` and replace `job_id_to_check` with an actual, recent UiPath Job ID you want to investigate.

```Python
# Example in run.py
job_id_to_check = "00000000-0000-0000-0000-000000000001" # <- Change this to a real Job ID
result = crew.kickoff(inputs={'job_id': job_id_to_check})
```
2. Execute the Script: In the same terminal where you set your environment variables, run:

```Bash
uv run python run.py
```
Watch the terminal as your AI agents come to life, fetching data, querying logs, and presenting their findings!

###⚙️ Customization

* Change LLM Model: The project is configured for `llama3` by default. You can easily switch to any model supported by Ollama (like `mixtral`, `codellama`, or phi3) by simply changing the `model` name in your `run.py` script.

* Agent Roles/Goals: Modify `run.py` to change agent `role`, `goal`, and `backstory` to fine-tune their behavior.

* Tasks: Adjust task `description` and `expected_output` for different monitoring or analysis scenarios.

* New Tools: Extend `my_tools.py` with more custom tools to interact with other systems (e.g., n8n, databases, service management platforms).

### 🤝 Contributing
Contributions are welcome! If you have suggestions, improvements, or new features, please feel free to:

1. Fork the repository.

2. Create a new branch (`git checkout -b feature/AmazingFeature`).

3. Make your changes.

4.Commit your changes (`git commit -m 'Add some AmazingFeature'`).

5. Push to the branch (`git push origin feature/AmazingFeature`).

6. Open a Pull Request.

### 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

### 📧 Contact
andrewabdelmalek@outlook.com 

Project Link: https://github.com/andrewihab988/Autonomous-RPA-Monitoring-with-CrewAI/
