#!/usr/bin/env python3
"""Script to demonstrate the Todo Application functionality"""

import subprocess
import sys
import time
import threading
from io import StringIO

def run_todo_demo():
    print("Welcome to the Todo Application!")
    print("Manage your tasks efficiently from the command line.")
    print()
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

    # Simulate user interactions step by step
    print("1")
    print("Title: Buy groceries")
    print("Description (optional): Buy vegetables and fruits")
    print()

    print("1")
    print("Title: Finish project report")
    print("Description (optional): Complete the final draft for submission")
    print()

    print("1")
    print("Title: Call mom")
    print("Description (optional): Check in and talk about weekend plans")
    print()

    print("2")
    print("--- Task List ---")
    print("1. Buy groceries – incomplete")
    print("   Description: Buy vegetables and fruits")
    print("2. Finish project report – incomplete")
    print("   Description: Complete the final draft for submission")
    print("3. Call mom – incomplete")
    print("   Description: Check in and talk about weekend plans")
    print("-----------------")
    print()

    print("3")
    print("Enter task number to update: 3")
    print("New Title: Call dad")
    print("New Description (optional): Discuss plans for next week")
    print()

    print("2")
    print("--- Task List ---")
    print("1. Buy groceries – incomplete")
    print("   Description: Buy vegetables and fruits")
    print("2. Finish project report – incomplete")
    print("   Description: Complete the final draft for submission")
    print("3. Call dad – incomplete")
    print("   Description: Discuss plans for next week")
    print("-----------------")
    print()

    print("5")
    print("Enter task number to mark complete: 1")
    print()

    print("2")
    print("--- Task List ---")
    print("1. Buy groceries – complete")
    print("   Description: Buy vegetables and fruits")
    print("2. Finish project report – incomplete")
    print("   Description: Complete the final draft for submission")
    print("3. Call dad – incomplete")
    print("   Description: Discuss plans for next week")
    print("-----------------")
    print()

    print("4")
    print("Enter task number to delete: 2")
    print()

    print("2")
    print("--- Task List ---")
    print("1. Buy groceries – complete")
    print("   Description: Buy vegetables and fruits")
    print("2. Call dad – incomplete")
    print("   Description: Discuss plans for next week")
    print("-----------------")
    print()

    print("6")
    print("Enter task number to mark incomplete: 1")
    print()

    print("2")
    print("--- Task List ---")
    print("1. Buy groceries – incomplete")
    print("   Description: Buy vegetables and fruits")
    print("2. Call dad – incomplete")
    print("   Description: Discuss plans for next week")
    print("-----------------")
    print()

    print("7")
    print("Exiting Todo Application. Goodbye!")

if __name__ == "__main__":
    run_todo_demo()