# src/agent/state.py
from typing import List, TypedDict, Annotated, Literal, Optional
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    """
    Represents the state of our e-commerce agent.
    ...
    """

    messages: Annotated[List[BaseMessage], operator.add]

    intent: Optional[Literal["product_assist", "order_help", "other"]]

    # FIX: Make these fields accumulate instead of being overwritten
    tools_called: Annotated[Optional[List[str]], operator.add]
    evidence: Annotated[Optional[List[str]], operator.add]

    policy_decision: Optional[dict]
    final_message: Optional[str]
