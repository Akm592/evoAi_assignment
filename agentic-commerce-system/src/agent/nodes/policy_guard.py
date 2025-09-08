import json
from ..state import AgentState

def policy_guard_node(state: AgentState) -> dict:
    """
    Checks for the output of the order_cancel tool and formalizes the policy decision.
    This is a deterministic node that enforces the 60-minute cancellation rule.
    """
    print("---NODE: Policy Guard---")

    # The intent must be 'order_help' to proceed with policy checks
    if state.get("intent") != "order_help":
        print("---POLICY GUARD: Skipping, not an order help request.---")
        return {"policy_decision": None}

    # Evidence from tool calls is expected to be in the state
    evidence = state.get("evidence", [])
    if not evidence:
        print("---POLICY GUARD: No evidence found to make a policy decision.---")
        return {"policy_decision": None}

    # Find the result from the 'order_cancel' tool
    cancel_tool_output = None
    for item in evidence:
        try:
            # Evidence items are stringified JSON, so we parse them
            data = json.loads(item)
            if "success" in data and "reason" in data:
                cancel_tool_output = data
                break
        except (json.JSONDecodeError, TypeError):
            continue

    if not cancel_tool_output:
        print("---POLICY GUARD: No cancellation tool output found in evidence.---")
        return {"policy_decision": None}

    # Formalize the policy decision based on the tool's output
    if cancel_tool_output.get("success") is False:
        decision = {
            "cancel_allowed": False,
            "reason": cancel_tool_output.get("reason")
        }
        print(f"---POLICY GUARD: Cancellation BLOCKED. Reason: {decision['reason']}---")
    else:
        # If success is not explicitly False, we assume it's allowed or not applicable
        decision = {"cancel_allowed": True}
        print("---POLICY GUARD: Cancellation ALLOWED.---")
        
    return {"policy_decision": decision}