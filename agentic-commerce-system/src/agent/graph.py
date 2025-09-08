import json
import re
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, ToolMessage
from pathlib import Path

from .state import AgentState
from .llm import get_llm

# Import nodes
from .nodes.router import router_node
from .nodes.policy_guard import policy_guard_node
from .nodes.responder import responder_node

# Import tools
from .tools.tools import (
    product_search,
    size_recommender,
    eta,
    order_lookup,
    order_cancel
)

# 1. Define the Agent and Tool Executor Nodes

# The list of tools our agent can use
tools = [product_search, size_recommender, eta, order_lookup, order_cancel]

# The ToolNode is a pre-built node from LangGraph that executes tools
tool_node = ToolNode(tools)

def agent_node(state: AgentState) -> dict:
    """
    The core reasoning node of the agent. It decides whether to call a tool
    or to generate a final response based on a manual, prompt-based tool-calling approach.
    """
    print("---NODE: Agent---")
    
    system_prompt_path = Path(__file__).parent.parent.parent / "prompts" / "system.md"
    system_prompt = system_prompt_path.read_text()

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])

    llm = get_llm()
    
    chain = prompt | llm
    
    response = chain.invoke({"messages": state["messages"]})
    
    # Manually parse for tool calls
    tool_calls = []
    match = re.search(r"```json\n(\{.*?\})\n```", response.content, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            tool_call_data = json.loads(json_str)
            if isinstance(tool_call_data, list):
                for i, tool in enumerate(tool_call_data):
                    tool_calls.append({
                        "name": tool["tool_name"],
                        "args": tool["arguments"],
                        "id": f"tool_call_{i}"
                    })
            else:
                tool_calls.append({
                    "name": tool_call_data["tool_name"],
                    "args": tool_call_data["arguments"],
                    "id": "tool_call_0"
                })
            ai_message = AIMessage(content="", tool_calls=tool_calls)
        except (json.JSONDecodeError, KeyError):
            ai_message = AIMessage(content=response.content)
    else:
        ai_message = AIMessage(content=response.content)

    return {"messages": [ai_message]}

def tool_executor_node(state: AgentState) -> dict:
    """
    This node is responsible for executing the tools called by the agent.
    It also formats the output and adds it to the 'evidence' field in the state.
    """
    print("---NODE: Tool Executor---")
    
    tool_calls = state["messages"][-1].tool_calls
    
    # The ToolNode, when invoked directly, returns the raw tool outputs
    raw_tool_outputs = tool_node.invoke(state)
    
    # We need to create ToolMessage objects to add back to the history
    tool_messages = []
    for i, tool_output in enumerate(raw_tool_outputs):
        tool_messages.append(
            ToolMessage(
                content=json.dumps(tool_output), # Content must be a string
                tool_call_id=tool_calls[i]['id'],
            )
        )

    # The evidence is also the stringified version of the tool output
    evidence = [msg.content for msg in tool_messages]
    
    tools_called = [call['name'] for call in tool_calls]
    
    print(f"---TOOLS EXECUTED: {', '.join(tools_called)}---")
    
    return {
        "messages": tool_messages,
        "evidence": evidence,
        "tools_called": tools_called
    }
    
# 2. Define the Conditional Edges

def should_continue(state: AgentState) -> str:
    """
    Decision point after the agent node.
    """
    print("---EDGE: Should Continue?---")
    if state["messages"][-1].tool_calls:
        return "execute_tools"
    else:
        return END

def route_after_tools(state: AgentState) -> str:
    """
    Decision point after executing tools.
    """
    print("---EDGE: Route After Tools---")
    if state.get("intent") == "order_help":
        return "policy_guard"
    else:
        return "agent"

# 3. Assemble the Graph

def create_graph():
    """
    Builds and compiles the LangGraph agent.
    """
    
    graph = StateGraph(AgentState)
    
    graph.add_node("router", router_node)
    graph.add_node("agent", agent_node)
    graph.add_node("tool_executor", tool_executor_node)
    graph.add_node("policy_guard", policy_guard_node)
    graph.add_node("responder", responder_node)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        lambda state: state["intent"],
        {
            "product_assist": "agent",
            "order_help": "agent",
            "other": "responder",
        }
    )

    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "execute_tools": "tool_executor",
            END: "responder"
        }
    )

    graph.add_conditional_edges(
        "tool_executor",
        route_after_tools,
        {
            "policy_guard": "policy_guard",
            "agent": "agent"
        }
    )
    
    graph.add_edge("policy_guard", "responder")
    
    graph.add_edge("responder", END)
    
    return graph.compile()
