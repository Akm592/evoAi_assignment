import json
import re
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

from ..state import AgentState
from ..llm import get_llm

class RouteQuery(BaseModel):
    """Routes the user's query to the appropriate workflow."""
    destination: Literal["product_assist", "order_help", "other"] = Field(
        description="The destination for the user's query based on its content."
    )

def extract_json_from_string(text: str) -> dict | None:
    """
    Extracts a JSON object from a string that may contain other text.
    """
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
    return None

def deterministic_keyword_routing(question: str) -> str | None:
    """
    Provides deterministic routing based on keywords to reduce LLM non-determinism.
    Returns None if no clear keyword match is found.
    """
    question_lower = question.lower()
    
    # Order-related keywords (high priority)
    order_keywords = [
        'order', 'cancel', 'cancellation', 'a1001', 'a1002', 'a1003',
        'order_id', 'email', 'refund', 'return'
    ]
    if any(keyword in question_lower for keyword in order_keywords):
        return "order_help"
    
    # Product-related keywords
    product_keywords = [
        'dress', 'product', 'wedding', 'midi', 'price', 'size', 'eta',
        'shipping', 'available', 'recommend', 'compare', 'zip'
    ]
    if any(keyword in question_lower for keyword in product_keywords):
        return "product_assist"
    
    # Discount/guardrail keywords
    guardrail_keywords = [
        'discount', 'code', 'coupon', 'promo', 'sale'
    ]
    if any(keyword in question_lower for keyword in guardrail_keywords):
        return "other"
    
    return None

def router_node(state: AgentState) -> dict:
    """
    Classifies the user's intent and updates the 'intent' field in the state.
    Uses deterministic keyword matching first, then falls back to LLM.
    """
    print("---NODE: Router---")
    
    question = state["messages"][-1].content
    
    # Try deterministic routing first
    deterministic_route = deterministic_keyword_routing(question)
    if deterministic_route:
        print(f"---ROUTER: Deterministic classification as '{deterministic_route}'---")
        return {"intent": deterministic_route}
    
    # Fall back to LLM routing
    print("---ROUTER: Using LLM for classification---")
    llm = get_llm()
    
    system_prompt = '''You are an expert at routing a user's request.
Based on the user's message, classify it into one of the following destinations:
- product_assist: For any questions about finding, comparing, or getting details about products.
- order_help: For any questions about existing orders, including cancellations, status, or modifications.
- other: For any other queries.

Return a JSON object with a single key "destination" and the value of the chosen destination.
For example:
{{"destination": "product_assist"}}
'''
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{question}"),
    ])
    
    router_chain = prompt | llm
    
    response = router_chain.invoke({"question": question})
    
    route_json = extract_json_from_string(response.content)
    
    if route_json and "destination" in route_json:
        destination = route_json["destination"]
        if destination not in ["product_assist", "order_help", "other"]:
            destination = "other"
    else:
        destination = "other"

    print(f"---ROUTER: LLM classified intent as '{destination}'---")
    
    return {"intent": destination}
