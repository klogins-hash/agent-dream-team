#!/usr/bin/env python3
"""Enhanced chat interface with memory and advanced tools."""

import sys
import threading
from team_enhanced import create_enhanced_team


def print_banner():
    print("\n" + "=" * 80)
    print("🌟✨ ENHANCED AGENT DREAM TEAM ✨🌟")
    print("=" * 80)
    print("\n💬 Now with Memory, Advanced Tools & Enhanced Intelligence!\n")
    print("=" * 80 + "\n")


def format_response(result):
    print("\n" + "🤖 " + "=" * 76)
    print("AGENT TEAM RESPONSE")
    print("=" * 80 + "\n")
    
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
    print_banner()
    
    print("🚀 Initializing enhanced team...")
    try:
        team, memory = create_enhanced_team()
        print("✅ Team ready with memory and advanced tools!\n")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return 1
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit']:
                print("\n👋 Goodbye!\n")
                break
            
            print("\n🔄 Agents working...\n")
            result = team(user_input)
            format_response(result)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
