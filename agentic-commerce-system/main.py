# main.py
import json
from langchain_core.messages import HumanMessage
from src.agent.graph import create_graph

def main():
    """
    Main function to run the OrderGenius agent from the command line.
    """
    print("Welcome to the Agentic Commerce System!")
    print("Type 'exit' to end the conversation.")
    
    # Create the compiled LangGraph agent
    app = create_graph()
    
    # In-memory message history
    messages = []

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        # Add user message to history
        messages.append(HumanMessage(content=user_input))
        
        # The input to the graph is a dictionary with a 'messages' key
        inputs = {"messages": messages}
        
        print("Agent is thinking...")
        
        # Invoke the graph and get the final state
        # We use .stream() to see intermediate steps, but .invoke() is fine for the final result
        final_state = app.invoke(inputs)
        
        # The final response is in the 'final_message' key of the state
        response = final_state.get("final_message", "I'm sorry, I encountered an error.")
        
        # Add the agent's response to the history for context in the next turn
        messages.append(response)
        
        print(f"\nAgent: {response}")
        
        # Optional: Print the full trace for debugging
        # print("\n--- Full Trace ---")
        # print(json.dumps(final_state, indent=2))
        # print("--------------------")

if __name__ == "__main__":
    main()
