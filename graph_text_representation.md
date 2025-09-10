
# EvoAI LangGraph Architecture - Text Representation

## Graph Flow:

```
┌─────────────┐
│ User Query  │
└─────┬───────┘
      │
      ▼
┌─────────────┐
│ Router Node │ ◄── Classifies intent: product_assist | order_help | other
└─────┬───────┘
      │
      ├─── product_assist/order_help ──┐
      │                                │
      └─── other ────────────────────┐ │
                                     │ │
                                     ▼ ▼
               ┌─────────────┐    ┌─────────────┐
               │ Agent Node  │    │ Responder   │
               └─────┬───────┘    │ Node        │
                     │            └─────────────┘
                     │                 ▲
         ┌───────────┴──────────────┐  │
         │                          │  │
    needs tools               no tools │
         │                          │  │
         ▼                          │  │
┌─────────────┐                     │  │
│ Tool        │ ◄── Executes tools  │  │
│ Executor    │     (5 available)   │  │
└─────┬───────┘                     │  │
      │                             │  │
      ├─── continue reasoning ──────┘  │
      │                                │
      └─── order_cancel called ──────┐ │
                                     │ │
                                     ▼ │
                               ┌─────────────┐
                               │ Policy      │
                               │ Guard       │ ◄── 60-min rule
                               └─────┬───────┘
                                     │
                                     └─────────┘

## Tools Available:
1. product_search(query, price_max, tags)
2. size_recommender(user_input)
3. eta(zip_code)
4. order_lookup(order_id, email)
5. order_cancel(order_id, timestamp)

## Node Descriptions:
- Router: Intent classification (deterministic keywords + LLM fallback)
- Agent: Core reasoning with dynamic context injection
- Tool Executor: Business logic execution
- Policy Guard: Strict 60-minute cancellation enforcement
- Responder: Final response generation + JSON trace output
```
