#!/usr/bin/env python3
"""
directory_traversal.py

Automates directory enumeration tools (Gobuster, ffuf, Feroxbuster, dirb) using tmux.
Tools run in new tmux sessions and automatically attach to them for user interaction.
After user exits tool with Ctrl+C or Enter, control returns to main menu.
Asks user to choose default or custom wordlist.
Ctrl+C at any time returns to the main menu.
"""
import subprocess
import sys
import shutil
import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

console = Console()

# Best default wordlists for each tool
DEFAULT_WORDLISTS = {
    "gobuster": "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt",
    "ffuf": "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt",
    "feroxbuster": "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt",
    "dirb": "/usr/share/wordlists/dirb/common.txt",
}

# Check if tmux is available
TMUX_CMD = shutil.which("tmux")
if not TMUX_CMD:
    console.print("[bold red]Error:[/bold red] tmux is not installed. Install it with 'sudo apt install tmux'.")
    sys.exit(1)

def show_banner():
    banner_text = "[bold cyan]Directory Traversal Automation Tool[/bold cyan]\n[italic yellow]by Kumar[/italic yellow]"
    panel = Panel(banner_text, expand=False, box=box.DOUBLE)
    console.print(panel)

def ask_target_info(tool):
    try:
        target = Prompt.ask("\U0001F4CD [cyan]Target IP/Host[/cyan]", default="10.10.10.10")
        port = Prompt.ask("\U0001F310 [cyan]Port[/cyan]", default="80")
        use_default = Confirm.ask("\U0001F4C2 [cyan]Use default wordlist?[/cyan]", default=True)

        if use_default:
            wordlist = DEFAULT_WORDLISTS[tool]
        else:
            wordlist = Prompt.ask("\U0001F4C4 [cyan]Enter full path to your wordlist[/cyan]").strip()

        output_file = Prompt.ask("\U0001F4BE [cyan]Enter output filename (without extension)[/cyan]", default=f"{tool}_output")
        output_path = Prompt.ask("\U0001F4C1 [cyan]Enter output directory (leave blank for current)[/cyan]", default="").strip()

        if output_path:
            os.makedirs(output_path, exist_ok=True)
            output_full_path = os.path.join(output_path, f"{output_file}.txt")
        else:
            output_full_path = f"{output_file}.txt"

        return target.strip(), port.strip(), wordlist, output_full_path
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Cancelled.[/bold yellow] Returning to main menu.")
        return None, None, None, None

def launch_in_tmux(tool_name, command):
    try:
        session_name = f"{tool_name}_session"
        subprocess.call(["tmux", "kill-session", "-t", session_name], stderr=subprocess.DEVNULL)

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            progress.add_task("Spawning tmux session...", total=None)
            time.sleep(1)
            progress.stop()

        subprocess.call(["tmux", "new-session", "-s", session_name, command])
        console.print(f"\n✅ [green]Exited {tool_name} session.[/green] Returning to main menu...\n")
    except Exception as e:
        console.print(f"[bold red]Failed to launch '{tool_name}':[/bold red] {e}")

def run_gobuster():
    target, port, wordlist, output = ask_target_info("gobuster")
    if not target:
        return
    cmd = f"gobuster dir -u http://{target}:{port} -w {wordlist} -o {output}; read -p 'Press enter to return to menu...'"
    launch_in_tmux("gobuster", cmd)

def run_ffuf():
    target, port, wordlist, output = ask_target_info("ffuf")
    if not target:
        return
    cmd = f"ffuf -u http://{target}:{port}/FUZZ -w {wordlist} -o {output} -of md; read -p 'Press enter to return to menu...'"
    launch_in_tmux("ffuf", cmd)

def run_feroxbuster():
    target, port, wordlist, output = ask_target_info("feroxbuster")
    if not target:
        return
    cmd = f"feroxbuster -u http://{target}:{port} -w {wordlist} -o {output}; read -p 'Press enter to return to menu...'"
    launch_in_tmux("feroxbuster", cmd)

def run_dirb():
    target, port, wordlist, output = ask_target_info("dirb")
    if not target:
        return
    url = f"http://{target}:{port}"
    cmd = f"dirb {url} {wordlist} -o {output}; read -p 'Press enter to return to menu...'"
    launch_in_tmux("dirb", cmd)

def main():
    options = {
        "1": ("Gobuster", run_gobuster),
        "2": ("ffuf", run_ffuf),
        "3": ("Feroxbuster", run_feroxbuster),
        "4": ("dirb", run_dirb),
        "5": ("Exit", None),
    }

    show_banner()

    while True:
        console.print("\n[bold magenta]=== Directory Traversal Automation ===[/bold magenta]")
        for key, (name, _) in options.items():
            console.print(f"[cyan][{key}][/cyan] {name}")
        try:
            choice = Prompt.ask("\U0001F449 Select an option", default="1").strip()
        except KeyboardInterrupt:
            console.print("\n[yellow]Pressed Ctrl+C. Returning to main menu.[/yellow]")
            continue

        if choice == "5":
            console.print("[bold green]Exiting...[/bold green]")
            break

        action = options.get(choice)
        if action:
            _, func = action
            try:
                func()
            except KeyboardInterrupt:
                console.print("\n[bold yellow]Operation interrupted.[/bold yellow] Returning to main menu.")
        else:
            console.print("[red]Invalid selection, please choose 1-5.[/red]")

if __name__ == "__main__":
    main()
