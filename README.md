# Agentic Commerce System

This project implements an AI-powered e-commerce assistant for the fictional brand 'EvoAI'. The agent is built using Python, LangChain, and LangGraph, creating a stateful, tool-using graph that can handle product inquiries and order management tasks.

## Features

### Core Functionality
- **Intent Classification**: Automatically determines the user's intent (e.g., product help, order questions).
- **Tool-Based Reasoning**: Uses a set of deterministic Python tools to answer questions based on actual data, preventing factual hallucination.
- **Product Assistance**: 
    - Searches for products by name, price, and tags.
    - **Always returns 2 product recommendations with explicit comparison**.
    - Enhanced size recommendations with comprehensive logic.
    - Provides shipping ETAs based on zip code.
- **Order Management**:
    - Looks up orders by ID and email with input validation.
    - Processes order cancellations based on a strict 60-minute policy.
    - **Enhanced error handling and validation**.
- **Policy Enforcement**: A dedicated 'Policy Guard' node ensures business rules (like the cancellation window) are correctly enforced.
- **Safety Guardrails**: Politely deflects out-of-scope questions, such as requests for discount codes.

### Advanced Features
- **Deterministic Routing**: Keyword-based routing fallback for improved consistency.
- **Input Validation**: Comprehensive validation for order IDs, emails, and zip codes.
- **Enhanced System Prompts**: Dynamic context injection based on user intent.
- **Improved Determinism**: Temperature controls and seeding for reproducible outputs.
- **Comprehensive Error Handling**: Graceful handling of edge cases and invalid inputs.

### Bonus Features
- **Unit Tests**: Edge case testing for 60-minute policy enforcement.
- **Evaluation Framework**: JSON schema validation and response quality metrics.
- **Enhanced Tools**: Better size recommendations and product comparison logic.

## Project Structure

The project uses a standard `src` layout to separate the application code from other files.

```
agentic-commerce-system/
├── .env.example       # Template for environment variables
├── .gitignore
├── README.md          # This file
├── main.py            # Interactive CLI runner
├── requirements.txt   # Python dependencies
├── data/              # Simulated data files
│   ├── orders.json
│   └── products.json
├── prompts/           # System prompts for the agent
│   └── system.md
├── src/
│   └── agent/         # The core agent application
│       ├── __init__.py
│       ├── graph.py       # LangGraph orchestration
│       ├── llm.py         # LLM client configuration
│       ├── state.py       # AgentState definition
│       ├── nodes/         # Individual graph nodes
│       └── tools/         # Agent's capabilities (tools)
└── tests/
    └── run_tests.py   # Automated validation script
```

## Setup and Installation

Follow these steps to set up and run the agent on your local machine.

**1. Create a Virtual Environment**

It is highly recommended to use a virtual environment to manage dependencies.

```bash
# Create the virtual environment
python -m venv venv

# Activate the environment
# On Windows:
# venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate
```

**2. Install Dependencies**

Install all the required Python packages.

```bash
pip install -r requirements.txt
```

**3. Configure Environment Variables**

This project supports two LLM providers: OpenRouter and Groq. You can choose which one to use by setting the `LLM_PROVIDER` variable in your `.env` file.

1.  Copy the example `.env.example` file to a new file named `.env`.
2.  Open the `.env` file and set the `LLM_PROVIDER` to either `"openrouter"` or `"groq"`.
3.  Fill in the credentials for the provider you have chosen.

**For OpenRouter:**
-   Set `LLM_PROVIDER="openrouter"`.
-   Provide your `OPENROUTER_API_KEY` from [openrouter.ai](https://openrouter.ai/keys).
-   Set the `OPENROUTER_MODEL_NAME`. It is highly recommended to use a model with strong, OpenAI-compatible tool-calling, such as `"openai/gpt-3.5-turbo"`.

**For Groq:**
-   Set `LLM_PROVIDER="groq"`.
-   Provide your `GROQ_API_KEY` from [console.groq.com](https://console.groq.com/keys).
-   Set the `GROQ_MODEL_NAME`, for example `"llama3-8b-8192"`.

Your `.env` file should look like this (you only need to fill out the section for the provider you are using):

```
# --- LLM Provider Selection ---
LLM_PROVIDER="openrouter" # or "groq"

# --- OpenRouter Credentials ---
OPENROUTER_API_KEY="your-openrouter-api-key"
OPENROUTER_MODEL_NAME="openai/gpt-3.5-turbo"
OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"

# --- Groq Credentials ---
GROQ_API_KEY="your-groq-api-key"
GROQ_MODEL_NAME="llama3-8b-8192"
```

## How to Run

There are two ways to run the agent.

### 1. Interactive Chat

To chat with the agent manually from your command line, run the `main.py` script:

```bash
python main.py
```

### 2. Automated Tests

To run the four validation test cases required by the assignment, execute the `run_tests.py` script. This will run the agent with predefined prompts and print the final JSON trace and user-facing reply for each.

```bash
python -m tests.run_tests
```

### 3. Unit Tests (Bonus)

Run the unit tests for policy enforcement:

```bash
python -m tests.test_policy
```

### 4. Evaluation Framework (Bonus)

Run the evaluation framework to validate agent performance:

```bash
python -m tests.eval_framework
```

## How It Works

The agent is built on LangGraph. It operates as a cyclical, stateful graph where each node performs a specific task.

1.  **State**: The `AgentState` object is a central dictionary that carries information (like message history, intent, and tool outputs) between nodes.
2.  **Nodes**: Each node is a Python function that receives the current state and can modify it.
    - `router`: Classifies the user's intent.
    - `agent`: The main reasoning loop. It uses the system prompt and an LLM to decide whether to call a tool or respond directly.
    - `tool_executor`: Executes any tools called by the agent node.
    - `policy_guard`: A deterministic check to enforce the 60-minute order cancellation policy.
    - `responder`: Generates the final, polished, user-facing response based on all the evidence gathered.
3.  **Edges**: Conditional edges connect the nodes, directing the flow of logic based on the current state (e.g., if the agent called a tool, the next step is to execute it).