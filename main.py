#!/usr/bin/env python3
"""
EvoAI Agentic Commerce System - Interactive CLI
A sophisticated e-commerce assistant powered by LangGraph
"""

import json
import sys
import time
from datetime import datetime
from langchain_core.messages import HumanMessage
from src.agent.graph import create_graph

# ANSI color codes for better terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_banner():
    """Display the application banner."""
    banner = f"""{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════╗
║                    🛍️  EvoAI Commerce Assistant                  ║
║                                                                  ║
║          Your intelligent shopping companion powered by          ║
║                         LangGraph AI                            ║
╚══════════════════════════════════════════════════════════════════╝{Colors.ENDC}
"""
    print(banner)

def print_help():
    """Display help information."""
    help_text = f"""{Colors.YELLOW}📋 How I can help you:

{Colors.GREEN}🛍️  Product Assistance:{Colors.ENDC}
   • Find dresses by style, occasion, price
   • Get size recommendations
   • Check shipping times to your location
   • Compare products
   
{Colors.BLUE}📦 Order Management:{Colors.ENDC}
   • Look up your orders
   • Cancel orders (within 60 minutes)
   • Get order status updates
   
{Colors.CYAN}💡 Example queries:{Colors.ENDC}
   • "Find me a wedding guest dress under $120"
   • "I'm between M/L for size, what do you recommend?"
   • "Cancel order A1003 for alex@example.com"
   • "What's the ETA to zip code 560001?"

{Colors.YELLOW}⌨️  Commands:{Colors.ENDC}
   • Type 'help' for this message
   • Type 'debug' to toggle debug mode
   • Type 'clear' to clear conversation history
   • Type 'exit' or 'quit' to end the session
"""
    print(help_text)

def print_thinking_animation(duration=2):
    """Display a thinking animation."""
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    end_time = time.time() + duration
    
    while time.time() < end_time:
        for char in chars:
            if time.time() >= end_time:
                break
            print(f"\r{Colors.YELLOW}🤔 {char} Agent is thinking...{Colors.ENDC}", end="", flush=True)
            time.sleep(0.1)
    print(f"\r{' ' * 30}\r", end="")  # Clear the line

def format_agent_response(response, debug_mode=False, trace=None):
    """Format the agent response with better styling."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    print(f"\n{Colors.CYAN}┌─ 🤖 EvoAI Assistant [{timestamp}] ──────────────────────────{Colors.ENDC}")
    print(f"{Colors.CYAN}│{Colors.ENDC}")
    
    # Format the response with proper line breaks
    lines = response.split('\n')
    for line in lines:
        if line.strip():
            print(f"{Colors.CYAN}│{Colors.ENDC} {line}")
        else:
            print(f"{Colors.CYAN}│{Colors.ENDC}")
    
    print(f"{Colors.CYAN}└────────────────────────────────────────────────────────────────{Colors.ENDC}")
    
    if debug_mode and trace:
        print(f"\n{Colors.YELLOW}🔍 Debug Trace:{Colors.ENDC}")
        print(f"{Colors.YELLOW}├─ Intent: {trace.get('intent', 'None')}{Colors.ENDC}")
        print(f"{Colors.YELLOW}├─ Tools Called: {', '.join(trace.get('tools_called', []) or [])}{Colors.ENDC}")
        print(f"{Colors.YELLOW}├─ Evidence Count: {len(trace.get('evidence', []) or [])}{Colors.ENDC}")
        policy = trace.get('policy_decision')
        if policy:
            print(f"{Colors.YELLOW}└─ Policy Decision: {json.dumps(policy, indent=2)}{Colors.ENDC}")
        else:
            print(f"{Colors.YELLOW}└─ Policy Decision: None{Colors.ENDC}")

def get_user_input():
    """Get styled user input."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n{Colors.GREEN}┌─ 👤 You [{timestamp}] ──────────────────────────────────────────{Colors.ENDC}")
    try:
        user_input = input(f"{Colors.GREEN}│{Colors.ENDC} ")
        print(f"{Colors.GREEN}└────────────────────────────────────────────────────────────────{Colors.ENDC}")
        return user_input.strip()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}👋 Goodbye! Thanks for using EvoAI Commerce Assistant!{Colors.ENDC}")
        sys.exit(0)

def main():
    """
    Enhanced main function with better CLI experience.
    """
    print_banner()
    
    # Initialize settings
    debug_mode = False
    conversation_count = 0
    
    try:
        # Create the compiled LangGraph agent
        print(f"{Colors.YELLOW}🚀 Initializing EvoAI Commerce Assistant...{Colors.ENDC}")
        app = create_graph()
        print(f"{Colors.GREEN}✅ Agent ready! How can I help you today?{Colors.ENDC}")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error initializing agent: {e}{Colors.ENDC}")
        return
    
    print_help()
    
    # In-memory message history
    messages = []

    while True:
        try:
            user_input = get_user_input()
            
            # Handle empty input
            if not user_input:
                print(f"{Colors.YELLOW}💭 Please enter a message or type 'help' for assistance.{Colors.ENDC}")
                continue
            
            # Handle special commands
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print(f"\n{Colors.CYAN}👋 Thank you for using EvoAI Commerce Assistant!{Colors.ENDC}")
                print(f"{Colors.CYAN}💫 Have a great day and happy shopping!{Colors.ENDC}")
                break
                
            elif user_input.lower() == 'help':
                print_help()
                continue
                
            elif user_input.lower() == 'debug':
                debug_mode = not debug_mode
                status = "enabled" if debug_mode else "disabled"
                print(f"{Colors.YELLOW}🔧 Debug mode {status}.{Colors.ENDC}")
                continue
                
            elif user_input.lower() == 'clear':
                messages = []
                conversation_count = 0
                print(f"{Colors.YELLOW}🧹 Conversation history cleared.{Colors.ENDC}")
                continue
            
            # Process the user input
            conversation_count += 1
            messages.append(HumanMessage(content=user_input))
            
            # Show thinking animation
            print_thinking_animation(1.5)
            
            # Invoke the graph
            inputs = {"messages": messages}
            final_state = app.invoke(inputs)
            
            # Extract response and trace
            response = final_state.get("final_message", "I'm sorry, I encountered an error processing your request.")
            
            # Create trace for debug mode
            trace = {
                'intent': final_state.get('intent'),
                'tools_called': final_state.get('tools_called'),
                'evidence': final_state.get('evidence'),
                'policy_decision': final_state.get('policy_decision')
            }
            
            # Add the agent's response to the history
            messages.append(HumanMessage(content=response))
            
            # Display the formatted response
            format_agent_response(response, debug_mode, trace)
            
            # Show conversation stats
            if conversation_count % 5 == 0:
                print(f"\n{Colors.CYAN}💬 Conversation stats: {conversation_count} exchanges{Colors.ENDC}")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}👋 Goodbye! Thanks for using EvoAI Commerce Assistant!{Colors.ENDC}")
            break
        except Exception as e:
            print(f"\n{Colors.RED}❌ An error occurred: {e}{Colors.ENDC}")
            print(f"{Colors.YELLOW}🔄 Please try again or type 'help' for assistance.{Colors.ENDC}")

if __name__ == "__main__":
    main()
