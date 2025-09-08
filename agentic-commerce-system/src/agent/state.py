from typing import List, TypedDict, Annotated, Literal, Optional
from langchain_core.messages import BaseMessage
import operator

# This TypedDict defines the structure of our agent's state.
# It's the central object that is passed between all nodes in the graph.
class AgentState(TypedDict):
    """
    Represents the state of our e-commerce agent.

    Attributes:
        messages: The history of messages in the conversation.
        intent: The classified intent of the user's query.
        tools_called: A list of tools that have been called.
        evidence: A list of evidence strings gathered from tool outputs.
        policy_decision: The decision made by the policy guardrail.
        final_message: The final, user-facing response.
    """
    
    # The 'messages' field will be appended to, not overwritten, thanks to Annotated.
    messages: Annotated[List[BaseMessage], operator.add]
    
    # Tracing & Observability state
    intent: Optional[Literal["product_assist", "order_help", "other"]]
    tools_called: Optional[List[str]]
    evidence: Optional[List[str]]
    policy_decision: Optional[dict]
    final_message: Optional[str]