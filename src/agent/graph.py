import json
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import ToolMessage
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

tools = [product_search, size_recommender, eta, order_lookup, order_cancel]
tool_node = ToolNode(tools)

def agent_node(state: AgentState) -> dict:
    """
    The core reasoning node of the agent.
    """
    print("---NODE: Agent---")

    system_prompt_path = Path(__file__).parent.parent.parent / "prompts" / "system.md"
    base_system_prompt = system_prompt_path.read_text()
    
    # Add dynamic context based on intent
    intent = state.get("intent")
    dynamic_context = ""
    
    if intent == "product_assist":
        dynamic_context = "\n\n**CRITICAL FOR PRODUCT ASSIST:**\n" + \
                         "- ALWAYS call product_search first\n" + \
                         "- Product search returns UP TO 2 items - use ALL returned items\n" + \
                         "- If user asks about size, call size_recommender\n" + \
                         "- If user asks about shipping/ETA, call eta tool\n" + \
                         "- In final response, ALWAYS compare the products if 2 are available\n" + \
                         "- Include specific details: titles, prices, colors, available sizes\n" + \
                         "- Mention why each product suits the user's needs\n"
    elif intent == "order_help":
        dynamic_context = "\n\n**CRITICAL FOR ORDER HELP:**\n" + \
                         "- ALWAYS call order_lookup first with order_id and email\n" + \
                         "- If order found, IMMEDIATELY call order_cancel to check policy\n" + \
                         "- Never make cancellation decisions yourself - let the tool decide\n" + \
                         "- The policy_guard will handle the final decision\n"
    
    enhanced_system_prompt = base_system_prompt + dynamic_context

    prompt = ChatPromptTemplate.from_messages([
        ("system", enhanced_system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])

    llm = get_llm()
    llm_with_tools = llm.bind_tools(tools)

    chain = prompt | llm_with_tools

    response = chain.invoke({"messages": state["messages"]})

    return {"messages": [response]}


def tool_executor_node(state: AgentState) -> dict:
    """
    This node is responsible for executing the tools called by the agent.
    """
    print("---NODE: Tool Executor---")

    tool_calls = state["messages"][-1].tool_calls

    # The ToolNode returns a dictionary with a single 'messages' key
    # containing a list of ToolMessage objects.
    tool_result = tool_node.invoke(state)
    tool_messages = tool_result["messages"]

    # The evidence is the stringified version of the tool output
    evidence = [msg.content for msg in tool_messages]
    tools_called = [call["name"] for call in tool_calls]

    print(f"---TOOLS EXECUTED: {', '.join(tools_called)}---")

    return {
        "messages": tool_messages,
        "evidence": evidence,
        "tools_called": tools_called,
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
    If the 'order_cancel' tool was just called, route to the policy guard.
    Otherwise, loop back to the agent to continue reasoning.
    """
    print("---EDGE: Route After Tools---")

    # The most recently called tools are in the state
    tools_called = state.get("tools_called", [])

    if "order_cancel" in tools_called:
        return "policy_guard"
    else:
        return "agent"


# 3. Assemble the Graph

def build_graph_structure():
    """
    Builds and returns the LangGraph builder (uncompiled) for visualization and compilation.
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

    return graph


def create_graph():
    """
    Builds and compiles the LangGraph agent.
    """
    graph = build_graph_structure()
    return graph.compile()
