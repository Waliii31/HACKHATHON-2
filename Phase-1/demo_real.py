#!/usr/bin/env python3
"""Demonstrate the Todo Application functionality step by step"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.manager import TodoManager
from src.main import display_tasks

def demonstrate_todo_app():
    print("=== Todo Application ===")
    print("1. Add Task")
    print("2. View All Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Mark Task Complete")
    print("6. Mark Task Incomplete")
    print("7. Exit")
    print("========================")
    print()

    # Create a fresh manager for demonstration
    manager = TodoManager()

    # Demonstrate Option 1: Add Task
    print("1")
    print("Title: Buy groceries")
    print("Description (optional): Buy vegetables and fruits")
    print()

    task1 = manager.add_task('Buy groceries', 'Buy vegetables and fruits')
    print(f"+ Task added successfully! (ID: {task1.id})")
    print()

    # Add second task
    print("1")
    print("Title: Finish project report")
    print("Description (optional): Complete the final draft for submission")
    print()

    task2 = manager.add_task('Finish project report', 'Complete the final draft for submission')
    print(f"+ Task added successfully! (ID: {task2.id})")
    print()

    # Add third task
    print("1")
    print("Title: Call mom")
    print("Description (optional): Check in and talk about weekend plans")
    print()

    task3 = manager.add_task('Call mom', 'Check in and talk about weekend plans')
    print(f"+ Task added successfully! (ID: {task3.id})")
    print()

    # Demonstrate Option 2: View All Tasks
    print("2")
    print()
    print("--- Task List ---")
    display_tasks(manager.get_all_tasks())
    print("-----------------")
    print()

    # Demonstrate Option 3: Update Task
    print("3")
    print("Enter task number to update: 3")
    print("New Title: Call dad")
    print("New Description (optional): Discuss plans for next week")
    print()

    updated_task = manager.update_task(3, 'Call dad', 'Discuss plans for next week')
    print(f"+ Task {updated_task.id} updated successfully!")
    print()

    # View tasks after update
    print("2")
    print()
    print("--- Task List ---")
    display_tasks(manager.get_all_tasks())
    print("-----------------")
    print()

    # Demonstrate Option 5: Mark Task Complete
    print("5")
    print("Enter task number to mark complete: 1")
    print()

    manager.mark_task_complete(1)
    print(f"+ Task 1 marked as complete!")
    print()

    # View tasks after marking complete
    print("2")
    print()
    print("--- Task List ---")
    display_tasks(manager.get_all_tasks())
    print("-----------------")
    print()

    # Demonstrate Option 4: Delete Task
    print("4")
    print("Enter task number to delete: 2")
    print()

    manager.delete_task(2)
    print(f"+ Task 2 deleted successfully!")
    print()

    # View tasks after deletion
    print("2")
    print()
    print("--- Task List ---")
    display_tasks(manager.get_all_tasks())
    print("-----------------")
    print()

    # Demonstrate Option 6: Mark Task Incomplete
    print("6")
    print("Enter task number to mark incomplete: 1")
    print()

    manager.mark_task_incomplete(1)
    print(f"+ Task 1 marked as incomplete!")
    print()

    # Final view
    print("2")
    print()
    print("--- Task List ---")
    display_tasks(manager.get_all_tasks())
    print("-----------------")
    print()

    # Demonstrate Option 7: Exit
    print("7")
    print()
    print("Goodbye! Your tasks will not be saved.")

if __name__ == "__main__":
    demonstrate_todo_app()