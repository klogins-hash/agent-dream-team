#!/usr/bin/env python3
"""Main entry point for the Agent Dream Team."""

import sys
from team import run_task


def main():
    """Run the agent dream team with a sample task."""
    
    # Default task
    default_task = "Research the latest trends in AI agents and write a comprehensive summary with key insights."
    
    # Get task from command line or use default
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = default_task
        print("💡 No task provided, using default task.")
        print(f"   To provide a custom task, run: python main.py 'your task here'\n")
    
    # Run the task
    try:
        result = run_task(task, verbose=True)
        return 0
    except KeyboardInterrupt:
        print("\n\n⚠️  Task interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
