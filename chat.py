#!/usr/bin/env python3
"""Interactive chat interface for the Agent Dream Team."""

import sys
import threading
from team import create_team


def print_banner():
    """Print a fun welcome banner."""
    print("\n" + "=" * 80)
    print("🌟✨ AGENT DREAM TEAM CHAT ✨🌟")
    print("=" * 80)
    print("\n💬 Chat with your AI agent team! They'll collaborate to help you.\n")
    print("Commands:")
    print("  • Type your request and press Enter")
    print("  • Type '+' followed by a message to add context while agents work")
    print("  • Type 'exit' or 'quit' to leave")
    print("  • Type 'help' for tips\n")
    print("=" * 80 + "\n")


def print_help():
    """Print helpful tips."""
    print("\n💡 Tips for great results:")
    print("  • Be specific about what you want")
    print("  • Ask for research, writing, analysis, or reviews")
    print("  • Try: 'Research X and write a summary'")
    print("  • Try: 'Analyze the pros and cons of X'")
    print("  • Try: 'Write a creative story about X'")
    print("\n💬 While agents are working:")
    print("  • Type '+' followed by additional context")
    print("  • Example: '+ make it more technical'")
    print("  • Example: '+ focus on recent developments'\n")


def format_response(result):
    """Format and display the agent team's response."""
    print("\n" + "🤖 " + "=" * 76)
    print("AGENT TEAM RESPONSE")
    print("=" * 80 + "\n")
    
    # Get the last agent result
    if result.results and result.node_history:
        last_node_id = result.node_history[-1].node_id
        if last_node_id in result.results:
            node_result = result.results[last_node_id]
            if hasattr(node_result.result, 'message'):
                message = node_result.result.message
                if message and "content" in message:
                    for content_block in message["content"]:
                        if "text" in content_block:
                            print(content_block["text"])
    
    print("\n" + "=" * 80)
    print(f"⏱️  Time: {result.execution_time/1000:.1f}s | 🔄 Handoffs: {len(result.node_history)}")
    print("=" * 80 + "\n")


def main():
    """Run the interactive chat."""
    print_banner()
    
    # Create the team once
    print("🚀 Initializing agent team...")
    try:
        team = create_team()
        print("✅ Team ready!\n")
    except Exception as e:
        print(f"❌ Failed to initialize team: {e}")
        return 1
    
    # State for managing additional context
    additional_context = []
    agents_working = False
    
    def listen_for_additions():
        """Listen for additional context while agents work."""
        nonlocal additional_context, agents_working
        while agents_working:
            try:
                extra = input()
                if extra.strip().startswith('+'):
                    context = extra.strip()[1:].strip()
                    if context:
                        additional_context.append(context)
                        print(f"📝 Added: {context}")
            except:
                pass
    
    # Chat loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            # Handle commands
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\n👋 Thanks for chatting! Goodbye!\n")
                break
            
            if user_input.lower() == 'help':
                print_help()
                continue
            
            # Check if adding context to previous request
            if user_input.startswith('+'):
                context = user_input[1:].strip()
                if context:
                    print(f"💡 Note: Use '+' while agents are working for live updates.")
                    print(f"   Starting new request with: {context}\n")
                    user_input = context
                else:
                    continue
            
            # Reset additional context
            additional_context = []
            agents_working = True
            
            # Start listener thread for additional context
            listener = threading.Thread(target=listen_for_additions, daemon=True)
            listener.start()
            
            # Build full request with any additional context
            full_request = user_input
            
            # Process the request
            print("\n🔄 Agents working... (type '+ message' to add context)\n")
            result = team(full_request)
            
            agents_working = False
            
            # If additional context was added, mention it
            if additional_context:
                print(f"\n📋 Additional context noted: {', '.join(additional_context)}")
                print("💡 Tip: For best results, include this in your next request!\n")
            
            # Display response
            format_response(result)
            
        except KeyboardInterrupt:
            agents_working = False
            print("\n\n👋 Interrupted. Goodbye!\n")
            break
        except Exception as e:
            agents_working = False
            print(f"\n❌ Error: {e}\n")
            import traceback
            traceback.print_exc()
            print("\n💡 Try rephrasing your request or type 'help' for tips.\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
