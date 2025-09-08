from langchain_core.prompts import ChatPromptTemplate
from ..state import AgentState
from ..llm import get_llm

def responder_node(state: AgentState) -> dict:
    """
    Generates the final user-facing response based on the accumulated state.

    This node synthesizes all gathered information (evidence, policy decisions)
    into a coherent, helpful, and brand-aligned message.
    """
    print("---NODE: Responder---")
    
    llm = get_llm()
    
    # System prompt that grounds the LLM in the collected data
    system_prompt = """You are a helpful e-commerce assistant for the brand 'EvoAI'.
Your brand voice is: concise, friendly, and non-pushy.

Generate a final, user-facing response based *only* on the provided context.
Do not invent any information.

Here is the context:
- User's original query: {question}
- Evidence gathered from tools: {evidence}
- Policy decisions made: {policy_decision}

Based on this context, provide a clear and helpful answer.
- If a cancellation was blocked, clearly state the policy reason and offer at least two alternatives
  (e.g., changing the shipping address, applying the order total to store credit, or connecting with support).
- If providing product suggestions, mention the product titles, prices, and available sizes directly from the evidence.
- If giving a shipping ETA, state the provided window.
- Keep the response concise and directly answer the user's query.
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
    ])

    # Chain the prompt and LLM
    response_chain = prompt | llm
    
    # Prepare the input for the chain from the state
    question = state["messages"][-1].content
    
    evidence_list = state.get("evidence")
    if not isinstance(evidence_list, list):
        evidence_list = []
    evidence = "\n".join(evidence_list)
    
    policy_decision = str(state.get("policy_decision", "N/A"))

    # Invoke the chain
    response = response_chain.invoke({
        "question": question,
        "evidence": evidence,
        "policy_decision": policy_decision,
    })

    print(f"---RESPONDER: Generated final message.---")

    return {"final_message": response.content}