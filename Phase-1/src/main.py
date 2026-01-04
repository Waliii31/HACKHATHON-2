"""Main entry point for the Todo CLI application.

This module provides the command-line interface for interacting with the
TodoManager. It displays a menu, handles user input, and calls appropriate
TodoManager methods to perform CRUD operations on tasks.
"""

import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path to allow imports to work
# when running as 'python src/main.py'
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.manager import TodoManager
from src.models import Task, TaskStatus


def display_tasks(tasks: list[Task]) -> None:
    """Display all tasks in a formatted table.
    
    Formats tasks as a table with columns for ID, Title, Status, and Description.
    Long descriptions are truncated to 80 characters with "..." appended.
    Displays "No tasks found." if the task list is empty.
    
    Args:
        tasks: List of Task instances to display.
    
    Example:
        >>> manager = TodoManager()
        >>> manager.add_task("Buy groceries", "Milk, eggs")
        >>> manager.add_task("Call dentist")
        >>> tasks = manager.get_all_tasks()
        >>> display_tasks(tasks)
        
        ID   | Title           | Status       | Description
        -------------------------------------------------------
        1    | Buy groceries   | incomplete   | Milk, eggs
        2    | Call dentist    | incomplete   |
    """
    if not tasks:
        print("\nNo tasks found.\n")
        return
    
    # Calculate column widths dynamically
    id_width = 4
    title_width = max(len(task.title) for task in tasks) + 2
    title_width = max(title_width, 20)  # Minimum width
    status_width = 12
    
    # Print header
    print(f"\n{'ID':<{id_width}} | {'Title':<{title_width}} | {'Status':<{status_width}} | Description")
    print("-" * (id_width + title_width + status_width + 50))
    
    # Print each task row
    for task in tasks:
        desc = task.description or ""
        # Truncate long descriptions for table display
        desc_display = desc[:80] + "..." if len(desc) > 80 else desc
        print(f"{task.id:<{id_width}} | {task.title:<{title_width}} | {task.status.value:<{status_width}} | {desc_display}")
    
    print()  # Blank line after table


def show_menu() -> None:
    """Display the main menu options.
    
    Shows a numbered list of all available commands including:
    - Add Task
    - View All Tasks
    - Update Task
    - Delete Task
    - Mark Task Complete
    - Mark Task Incomplete
    - Exit
    """
    print("\n=== Todo Application ===")
    print("1. Add Task")
    print("2. View All Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Mark Task Complete")
    print("6. Mark Task Incomplete")
    print("7. Exit")
    print("========================\n")


def handle_add_task(manager: TodoManager) -> None:
    """Handle the add task command.
    
    Prompts the user for task title and optional description, then
    calls manager.add_task(). Displays success message with task ID,
    or error message if validation fails.
    
    Args:
        manager: TodoManager instance to add the task to.
    """
    title = input("Enter task title: ").strip()
    description = input("Enter task description (optional): ").strip()
    
    # Convert empty description to None
    description = description if description else None
    
    try:
        task = manager.add_task(title, description)
        print(f"\n+ Task added successfully! (ID: {task.id})")
    except ValueError as e:
        print(f"\n- Error: {e}")


def handle_view_tasks(manager: TodoManager) -> None:
    """Handle the view tasks command.
    
    Retrieves all tasks from the manager and displays them in a
    formatted table.
    
    Args:
        manager: TodoManager instance to retrieve tasks from.
    """
    tasks = manager.get_all_tasks()
    display_tasks(tasks)


def handle_update_task(manager: TodoManager) -> None:
    """Handle the update task command.
    
    Prompts for task ID and new title/description. Allows updating
    either field individually or both together. Pressing Enter without
    input skips that field.
    
    Args:
        manager: TodoManager instance to update the task in.
    """
    try:
        task_id_str = input("Enter task ID to update: ")
        task_id = int(task_id_str)
        
        title = input("Enter new title (press Enter to skip): ").strip()
        description = input("Enter new description (press Enter to skip): ").strip()
        
        # None means "don't update", empty string after strip means update to empty
        title = title if title else None
        description = description if description else None
        
        if title is None and description is None:
            print("\n! No changes specified.")
            return
        
        task = manager.update_task(task_id, title, description)
        print(f"\n+ Task {task.id} updated successfully!")
        
    except ValueError as e:
        print(f"\n- Error: {e}")


def handle_delete_task(manager: TodoManager) -> None:
    """Handle the delete task command.
    
    Prompts for task ID and deletes the corresponding task.
    Displays success message or error if task not found.
    
    Args:
        manager: TodoManager instance to delete the task from.
    """
    try:
        task_id_str = input("Enter task ID to delete: ")
        task_id = int(task_id_str)
        
        manager.delete_task(task_id)
        print(f"\n+ Task {task_id} deleted successfully!")
        
    except ValueError as e:
        print(f"\n- Error: {e}")


def handle_mark_complete(manager: TodoManager) -> None:
    """Handle the mark task complete command.
    
    Prompts for task ID and marks the task as complete.
    Displays success message or error if task not found.
    
    Args:
        manager: TodoManager instance to mark the task in.
    """
    try:
        task_id_str = input("Enter task ID to mark complete: ")
        task_id = int(task_id_str)
        
        manager.mark_task_complete(task_id)
        print(f"\n+ Task {task_id} marked as complete!")
        
    except ValueError as e:
        print(f"\n- Error: {e}")


def handle_mark_incomplete(manager: TodoManager) -> None:
    """Handle the mark task incomplete command.
    
    Prompts for task ID and marks the task as incomplete.
    Displays success message or error if task not found.
    
    Args:
        manager: TodoManager instance to mark the task in.
    """
    try:
        task_id_str = input("Enter task ID to mark incomplete: ")
        task_id = int(task_id_str)
        
        manager.mark_task_incomplete(task_id)
        print(f"\n+ Task {task_id} marked as incomplete!")
        
    except ValueError as e:
        print(f"\n- Error: {e}")


def main() -> None:
    """Main application entry point.
    
    Creates a TodoManager instance and runs an infinite loop that:
    1. Displays the menu
    2. Gets user input
    3. Dispatches to appropriate handler function
    4. Repeats until user selects Exit (option 7)
    
    All task data is stored in memory for the duration of the session.
    """
    manager = TodoManager()
    
    print("\nWelcome to the Todo Application!")
    print("Manage your tasks efficiently from the command line.\n")
    
    while True:
        show_menu()
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == "1":
            handle_add_task(manager)
        elif choice == "2":
            handle_view_tasks(manager)
        elif choice == "3":
            handle_update_task(manager)
        elif choice == "4":
            handle_delete_task(manager)
        elif choice == "5":
            handle_mark_complete(manager)
        elif choice == "6":
            handle_mark_incomplete(manager)
        elif choice == "7":
            print("\nGoodbye! Your tasks will not be saved.\n")
            break
        else:
            print("\n- Invalid choice. Please enter a number between 1 and 7.\n")


if __name__ == "__main__":
    main()
