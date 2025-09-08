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

def router_node(state: AgentState) -> dict:
    """
    Classifies the user's intent and updates the 'intent' field in the state.
    """
    print("---NODE: Router---")
    
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
    
    question = state["messages"][-1].content
    
    response = router_chain.invoke({"question": question})
    
    route_json = extract_json_from_string(response.content)
    
    if route_json and "destination" in route_json:
        destination = route_json["destination"]
        if destination not in ["product_assist", "order_help", "other"]:
            destination = "other"
    else:
        destination = "other"

    print(f"---ROUTER: Classified intent as '{destination}'---")
    
    return {"intent": destination}