#!/usr/bin/env python3

import subprocess
from rich.console import Console
from rich.prompt import Prompt
import sys

console = Console()

def print_banner():
    banner = (
        "[bold cyan]"
        "╔══════════════════════════════════════════╗\n"
        "║  Reconnaissance Automation Tool - Main   ║\n"
        "║        Developed by Kumar Pachiyappan    ║\n"
        "╚══════════════════════════════════════════╝"
        "[/bold cyan]"
    )
    console.print(banner)

def run_script(script_name):
    try:
        subprocess.call(["python3", script_name])
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted. Returning to main menu.[/yellow]")
    except Exception as e:
        console.print(f"[red]Failed to launch {script_name}: {e}[/red]")

def main_menu():
    tools = {
        "1": ("Subdomain Enumeration", "subdomain_enumeration.py"),
        "2": ("Network Mapping", "network_mapping.py"),
        "3": ("Directory Traversal", "directory_traversal.py"),
        "4": ("Vulnerability Assessment", "vulnerability_assessment.py"),
        "5": ("Hash Cracking", "hash_cracking.py"),
        "6": ("Exit", None)
    }

    print_banner()

    while True:
        console.print("\n[bold magenta]=== Main Menu ===[/bold magenta]")
        for key, (name, _) in tools.items():
            console.print(f"[cyan][{key}][/cyan] {name}")

        choice = Prompt.ask("👉 Select an option", default="1").strip()

        if choice == "6":
            console.print("[bold green]Exiting Recon Automation Tool. Goodbye![/bold green]")
            break

        selected = tools.get(choice)
        if selected:
            _, script = selected
            run_script(script)
        else:
            console.print("[red]Invalid selection. Choose a number from the menu.[/red]")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[bold red]Exiting...[/bold red]")
        sys.exit(0)
