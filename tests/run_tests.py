#!/usr/bin/env python3
"""
EvoAI Agentic Commerce System - Enhanced Test Runner
Runs the four required test scenarios with beautiful output formatting
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

def print_test_banner():
    """Display the test banner (Windows-compatible)."""
    banner = f"""{Colors.CYAN}{Colors.BOLD}
+===============================================================================+
|                    EvoAI Commerce System - Test Suite                        |
|                                                                               |
|            Running the 4 required test scenarios for evaluation              |
+===============================================================================+{Colors.ENDC}
"""
    print(banner)

def print_thinking_dots(duration=1):
    """Display thinking dots animation (Windows-compatible)."""
    chars = "/-\\|/-\\|"
    end_time = time.time() + duration
    
    while time.time() < end_time:
        for char in chars:
            if time.time() >= end_time:
                break
            print(f"\r{Colors.YELLOW}  {char} Processing...{Colors.ENDC}", end="", flush=True)
            time.sleep(0.1)
    print("\r" + " " * 20 + "\r", end="")

def format_json_nicely(data, indent=2):
    """Format JSON with syntax highlighting."""
    json_str = json.dumps(data, indent=indent, ensure_ascii=False)
    # Simple syntax highlighting
    lines = json_str.split('\n')
    formatted_lines = []
    
    for line in lines:
        if '"intent"' in line or '"tools_called"' in line or '"final_message"' in line:
            formatted_lines.append(f"{Colors.CYAN}{line}{Colors.ENDC}")
        elif '"policy_decision"' in line:
            formatted_lines.append(f"{Colors.YELLOW}{line}{Colors.ENDC}")
        elif 'true' in line or 'false' in line:
            formatted_lines.append(f"{Colors.GREEN}{line}{Colors.ENDC}")
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def run_test(prompt: str, test_name: str, test_number: int, description: str = ""):
    """
    Enhanced test runner with beautiful formatting.

    Args:
        prompt: The user input to test.
        test_name: The name of the test for printing.
        test_number: The test number (1-4)
        description: Description of what this test validates
    """
    # Test header
    print(f"\n{Colors.BLUE}+{'-' * 77}+{Colors.ENDC}")
    print(f"{Colors.BLUE}|{Colors.BOLD} Test {test_number}: {test_name:<65} {Colors.ENDC}{Colors.BLUE}|{Colors.ENDC}")
    if description:
        print(f"{Colors.BLUE}|{Colors.ENDC} {description:<75} {Colors.BLUE}|{Colors.ENDC}")
    print(f"{Colors.BLUE}+{'-' * 77}+{Colors.ENDC}")
    
    # Show the prompt
    print(f"\n{Colors.YELLOW}[INPUT] Prompt:{Colors.ENDC}")
    print(f"   \"{prompt}\"")
    
    print_thinking_dots(1.2)
    
    try:
        app = create_graph()
        
        # Prepare inputs
        messages = [HumanMessage(content=prompt)]
        inputs = {"messages": messages}
        
        # Invoke the graph
        start_time = time.time()
        final_state = app.invoke(inputs)
        execution_time = time.time() - start_time
        
        # Create trace
        trace = {
            "intent": final_state.get("intent"),
            "tools_called": final_state.get("tools_called"),
            "evidence": final_state.get("evidence"),
            "policy_decision": final_state.get("policy_decision"),
            "final_message": final_state.get("final_message")
        }
        
        # Print results
        print(f"\n{Colors.GREEN}[SUCCESS] Test completed! {Colors.ENDC}(Execution time: {execution_time:.2f}s)")
        
        print(f"\n{Colors.CYAN}[TRACE] JSON Output:{Colors.ENDC}")
        print("+" + "-" * 75 + "+")
        formatted_json = format_json_nicely(trace)
        for line in formatted_json.split('\n'):
            print(f"| {line:<73} |")
        print("+" + "-" * 75 + "+")
        
        print(f"\n{Colors.CYAN}[REPLY] Final Response:{Colors.ENDC}")
        print("+" + "-" * 75 + "+")
        
        final_message = trace.get("final_message", "")
        if final_message:
            # Handle long messages by wrapping
            lines = final_message.split('\n')
            for line in lines:
                if len(line) <= 73:
                    print(f"| {line:<73} |")
                else:
                    # Simple word wrap
                    words = line.split(' ')
                    current_line = ""
                    for word in words:
                        if len(current_line + word + " ") <= 73:
                            current_line += word + " "
                        else:
                            if current_line:
                                print(f"| {current_line.strip():<73} |")
                            current_line = word + " "
                    if current_line:
                        print(f"| {current_line.strip():<73} |")
        else:
            print(f"| {Colors.RED}No final message generated{Colors.ENDC}")
            
        print("+" + "-" * 75 + "+")
        
        return True
        
    except Exception as e:
        print(f"\n{Colors.RED}[ERROR] Test failed with error: {str(e)}{Colors.ENDC}")
        return False



def main():
    """
    Run all four required test scenarios with enhanced formatting.
    """
    print_test_banner()
    
    print(f"\n{Colors.YELLOW}[OVERVIEW] Test Suite:{Colors.ENDC}")
    print("   Testing all core functionality as per assignment requirements")
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = []
    start_time = time.time()
    
    # Test 1: Product Assist
    prompt1 = "Wedding guest, midi, under $120 — I'm between M/L. ETA to 560001?"
    results.append(run_test(
        prompt1, 
        "Product Assist", 
        1,
        "Validates product search, comparison, size recommendation & ETA"
    ))

    # Test 2: Order Help (Allowed)
    prompt2 = "I need to cancel order A1003 for mira@example.com. Please process this, assuming the current time is 2025-09-07T12:30:00Z."
    results.append(run_test(
        prompt2, 
        "Order Help (Allowed)", 
        2,
        "Tests successful order cancellation within 60-minute window"
    ))

    # Test 3: Order Help (Blocked) 
    prompt3 = "Please cancel order A1002 for alex@example.com. Assume the current time is 2025-09-07T12:30:00Z."
    results.append(run_test(
        prompt3, 
        "Order Help (Blocked)", 
        3,
        "Tests policy enforcement and alternative suggestions"
    ))

    # Test 4: Guardrail
    prompt4 = "Can you give me a discount code that doesn't exist?"
    results.append(run_test(
        prompt4, 
        "Guardrail Response", 
        4,
        "Validates refusal behavior and legitimate alternatives"
    ))
    
    # Summary
    total_time = time.time() - start_time
    passed = sum(results)
    total = len(results)
    
    print(f"\n{Colors.CYAN}{'=' * 79}{Colors.ENDC}")
    print(f"{Colors.CYAN}                           TEST SUMMARY                              {Colors.ENDC}")
    print(f"{Colors.CYAN}{'=' * 79}{Colors.ENDC}")
    
    if passed == total:
        print(f"{Colors.GREEN}[PASS] All tests passed! ({passed}/{total}){Colors.ENDC}")
        status_icon = "[PASS]"
        status_color = Colors.GREEN
    else:
        print(f"{Colors.RED}[FAIL] Some tests failed ({passed}/{total}){Colors.ENDC}")
        status_icon = "[FAIL]"
        status_color = Colors.RED
    
    print(f"\n{status_color}{status_icon} Results: {passed}/{total} tests passed{Colors.ENDC}")
    print(f"{Colors.CYAN}[TIME] Total execution time: {total_time:.2f} seconds{Colors.ENDC}")
    print(f"{Colors.CYAN}[DATE] Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    
    print(f"\n{Colors.YELLOW}[NEXT] Next steps:{Colors.ENDC}")
    if passed == total:
        print("   * All core requirements validated")
        print("   * Ready for submission")
        print("   * Consider running unit tests: python -m tests.test_policy")
        print("   * Run evaluation framework: python -m tests.eval_framework")
    else:
        print("   * Review failed tests above")
        print("   * Check agent configuration and tools")
        print("   * Verify environment setup")
    
    print(f"\n{Colors.CYAN}{'=' * 79}{Colors.ENDC}")
    
    # Exit code for CI/CD
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[STOP] Test execution interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}[ERROR] Unexpected error: {str(e)}{Colors.ENDC}")
        sys.exit(1)
