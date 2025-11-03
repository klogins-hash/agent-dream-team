#!/usr/bin/env python3
"""Interactive demo for the Agent Dream Team."""

from team import run_task


def print_header():
    """Print the demo header."""
    print("=" * 80)
    print("🌟 Agent Dream Team - Interactive Demo")
    print("=" * 80)
    print("\nThis demo showcases a multi-agent system with:")
    print("  • Coordinator: Task analysis and delegation")
    print("  • Researcher: Information gathering")
    print("  • Writer: Content creation")
    print("  • Reviewer: Quality assurance")
    print("\n" + "=" * 80 + "\n")


def run_demo_tasks():
    """Run a series of demo tasks."""
    
    tasks = [
        {
            "name": "Research & Write",
            "description": "Research AI agents and write a brief overview",
            "task": "Research the concept of AI agents and write a 3-paragraph overview suitable for beginners."
        },
        {
            "name": "Analysis Task",
            "description": "Analyze a topic and provide insights",
            "task": "Analyze the benefits and challenges of multi-agent systems in production environments."
        },
        {
            "name": "Creative Task",
            "description": "Create engaging content",
            "task": "Write a creative introduction for a blog post about the future of AI collaboration."
        }
    ]
    
    print("📋 Available Demo Tasks:\n")
    for i, task_info in enumerate(tasks, 1):
        print(f"{i}. {task_info['name']}")
        print(f"   {task_info['description']}\n")
    
    print(f"{len(tasks) + 1}. Custom task (enter your own)")
    print("0. Exit\n")
    
    while True:
        try:
            choice = input("Select a task (0-{}): ".format(len(tasks) + 1)).strip()
            
            if choice == "0":
                print("\n👋 Goodbye!")
                return
            
            if choice == str(len(tasks) + 1):
                custom_task = input("\nEnter your custom task: ").strip()
                if custom_task:
                    print()
                    run_task(custom_task, verbose=True)
                else:
                    print("❌ Task cannot be empty")
                    continue
            else:
                task_idx = int(choice) - 1
                if 0 <= task_idx < len(tasks):
                    task_info = tasks[task_idx]
                    print(f"\n🎯 Running: {task_info['name']}\n")
                    run_task(task_info['task'], verbose=True)
                else:
                    print("❌ Invalid choice")
                    continue
            
            # Ask if user wants to continue
            print("\n" + "=" * 80 + "\n")
            continue_choice = input("Run another task? (y/n): ").strip().lower()
            if continue_choice != 'y':
                print("\n👋 Goodbye!")
                return
            print("\n" + "=" * 80 + "\n")
            
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            return
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Run the interactive demo."""
    print_header()
    
    try:
        run_demo_tasks()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
