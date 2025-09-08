import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from langchain_core.tools import tool

# Get the absolute path to the data directory
DATA_PATH = Path(__file__).parent.parent.parent.parent / "data"

@tool
def product_search(query: str, price_max: int, tags: List[str] = None) -> List[dict]:
    """
    Search for products based on a query, maximum price, and optional tags.

    Args:
        query: The user's search query for product titles.
        price_max: The maximum price of products to return.
        tags: A list of tags to filter products by.
    """
    with open(DATA_PATH / "products.json") as f:
        products = json.load(f)

    results = []
    for p in products:
        # Filter by price
        if p['price'] > price_max:
            continue
        # Filter by query in title (case-insensitive)
        if query.lower() not in p['title'].lower():
            continue
        # Filter by tags if provided
        if tags and not all(tag in p['tags'] for tag in tags):
            continue
        results.append(p)
    
    # For determinism, sort by price and return up to 2 items
    return sorted(results, key=lambda p: p['price'])[:2]

@tool
def size_recommender(user_input: str) -> str:
    """
    Provides a size recommendation based on simple user input.
    For example, if the user says they're 'between M/L', this gives a recommendation.
    """
    if "between m/l" in user_input.lower() or "between l/m" in user_input.lower():
        return "Based on your input, Medium (M) is often a safer middle choice for a comfortable fit."
    return "I can't make a specific recommendation without more information, but I can show you the available sizes."

@tool
def eta(zip_code: str) -> str:
    """
    Provides a shipping ETA for a given zip code. This is a rule-based function.
    """
    # Simple rule-based ETA for demonstration
    return f"Shipping to zip code {zip_code} typically takes 2-5 business days."

@tool
def order_lookup(order_id: str, email: str) -> Optional[dict]:
    """
    Looks up an order using the order ID and customer email.

    Args:
        order_id: The unique identifier for the order.
        email: The email address associated with the order.
    """
    with open(DATA_PATH / "orders.json") as f:
        orders = json.load(f)
    
    for order in orders:
        if order['order_id'] == order_id and order['email'] == email:
            return order
    return {"error": "Order not found."}

@tool
def order_cancel(order_id: str, simulated_now: Optional[str] = None) -> dict:
    """
    Cancels an order if it was created within the last 60 minutes.

    Args:
        order_id: The ID of the order to cancel.
        simulated_now: An optional ISO format string to fix the current time for testing.
    """
    with open(DATA_PATH / "orders.json") as f:
        orders = json.load(f)
        
    order_to_cancel = next((o for o in orders if o['order_id'] == order_id), None)

    if not order_to_cancel:
        return {"error": f"Order {order_id} not found."}

    created_at_str = order_to_cancel['created_at']
    created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))

    # Use simulated_now for testing, otherwise use the actual current time in UTC
    if simulated_now:
        now = datetime.fromisoformat(simulated_now.replace("Z", "+00:00"))
    else:
        now = datetime.now(timezone.utc)

    time_diff_minutes = (now - created_at).total_seconds() / 60

    if time_diff_minutes <= 60:
        # In a real system, you would update the order status here
        return {"success": True, "message": f"Order {order_id} has been successfully canceled."}
    else:
        return {
            "success": False, 
            "reason": "Cancellation failed: Order was placed more than 60 minutes ago.",
            "minutes_since_order": int(time_diff_minutes)
        }