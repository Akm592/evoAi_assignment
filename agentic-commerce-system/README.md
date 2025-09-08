# Agentic Commerce System

This project implements an AI-powered e-commerce assistant for the fictional brand 'EvoAI'. The agent is built using Python, LangChain, and LangGraph, creating a stateful, tool-using graph that can handle product inquiries and order management tasks.

## Features

- **Intent Classification**: Automatically determines the user's intent (e.g., product help, order questions).
- **Tool-Based Reasoning**: Uses a set of deterministic Python tools to answer questions based on actual data, preventing factual hallucination.
- **Product Assistance**: 
    - Searches for products by name, price, and tags.
    - Recommends sizes.
    - Provides shipping ETAs based on zip code.
- **Order Management**:
    - Looks up orders by ID and email.
    - Processes order cancellations based on a strict 60-minute policy.
- **Policy Enforcement**: A dedicated 'Policy Guard' node ensures business rules (like the cancellation window) are correctly enforced.
- **Safety Guardrails**: Politely deflects out-of-scope questions, such as requests for discount codes.

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

You will need an API key from [OpenRouter](https://openrouter.ai/keys) to run the agent.

1.  Copy the example `.env.example` file to a new file named `.env`.
2.  Open the `.env` file and paste your OpenRouter API key.
3.  **Important**: For this agent to function correctly, it requires a model with strong tool-calling capabilities. It is highly recommended to set the model name to `openai/gpt-3.5-turbo`.

Your `.env` file should look like this:

```
# OpenRouter Credentials
OPENROUTER_API_KEY="your-openrouter-api-key"
OPENROUTER_MODEL_NAME="openai/gpt-3.5-turbo"
OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"
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