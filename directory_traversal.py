#!/usr/bin/env python3
"""
directory_traversal.py

Automates directory enumeration tools (Gobuster, ffuf, Feroxbuster, dirb) using tmux.
Each tool’s output can be:
  1) Saved to a custom path/filename you specify, or
  2) Auto-saved into <target>_<YYYY-MM-DD_HH-MM-SS>/<tool>_<target>.txt
     when you leave both prompts blank.
"""
import subprocess
import sys
import shutil
import os
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

console = Console()

# Best default wordlists
DEFAULT_WORDLISTS = {
    "gobuster":     "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt",
    "ffuf":         "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt",
    "feroxbuster":  "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt",
    "dirb":         "/usr/share/wordlists/dirb/common.txt",
}

# Ensure tmux is installed
TMUX_CMD = shutil.which("tmux")
if not TMUX_CMD:
    console.print("[bold red]Error:[/bold red] tmux is not installed. Install with 'sudo apt install tmux'.")
    sys.exit(1)

def show_banner():
    panel = Panel(
        "[bold cyan]Directory Traversal Automation Tool[/bold cyan]\n[italic yellow]by Kumar[/italic yellow]",
        expand=False, box=box.DOUBLE
    )
    console.print(panel)

def ask_target_and_wordlist(tool_name):
    """Prompt for target, port, and wordlist."""
    try:
        target = Prompt.ask("📍 [cyan]Target IP/Host[/cyan]", default="10.10.10.10").strip()
        port   = Prompt.ask("🌐 [cyan]Port[/cyan]", default="80").strip()
        use_default = Confirm.ask(f"📂 [cyan]Use default wordlist for {tool_name}?[/cyan]", default=True)
        if use_default:
            wordlist = DEFAULT_WORDLISTS[tool_name]
        else:
            wordlist = Prompt.ask("📄 [cyan]Path to your custom wordlist[/cyan]").strip()
        return target, port, wordlist
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Cancelled.[/bold yellow] Returning to main menu.")
        return None, None, None

def ask_output_manual():
    """
    Prompt for manual filename and directory.
    If both are left blank, caller will switch to auto-mode.
    Returns (filename_without_ext, directory).
    """
    filename = Prompt.ask(
        "💾 [cyan]Enter output filename (without extension)[/cyan]",
        default=""
    ).strip()
    directory = Prompt.ask(
        "📂 [cyan]Enter output directory (leave blank for auto)<[/cyan]",
        default=""
    ).strip()
    return filename, directory

def make_auto_folder(target):
    """Create and return auto-naming folder like <target>_<YYYY-MM-DD_HH-MM-SS>."""
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder = f"{target.replace('.', '_')}_{ts}"
    os.makedirs(folder, exist_ok=True)
    return folder

def launch_in_tmux(tool_name, cmd):
    """Spawn the given command inside a tmux session."""
    session = f"{tool_name}_session"
    subprocess.call(["tmux", "kill-session", "-t", session], stderr=subprocess.DEVNULL)
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as p:
        p.add_task("Spawning tmux session...", total=None)
        time.sleep(1)
    subprocess.call(["tmux", "new-session", "-s", session, "sh", "-c", cmd])
    console.print(f"\n✅ [green]{tool_name} session ended.[/green] Returning to menu...\n")

def prepare_and_run(tool_name, build_cmd):
    """
    Common flow for each tool:
      1) Ask target/wordlist
      2) Ask manual filename & directory
      3) Decide auto vs manual paths
      4) Build final command and launch
    """
    target, port, wordlist = ask_target_and_wordlist(tool_name)
    if not target:
        return

    filename, directory = ask_output_manual()
    # Determine final folder and file name
    if filename == "" and directory == "":
        # Auto-mode
        directory = make_auto_folder(target)
        filename = f"{tool_name}_{target}"
    else:
        # Manual-mode: ensure directory exists
        if directory:
            os.makedirs(directory, exist_ok=True)
        else:
            directory = "."
        if filename == "":
            filename = f"{tool_name}_output"
    output_path = os.path.join(directory, f"{filename}.txt")

    cmd = build_cmd(target, port, wordlist, output_path)
    launch_in_tmux(tool_name, cmd)

def run_gobuster():
    prepare_and_run("gobuster",
        lambda tgt, prt, wl, out: (
            f"gobuster dir -u http://{tgt}:{prt} -w {wl} -o {out}; "
            "read -p 'Press enter to return to menu...'"
        )
    )

def run_ffuf():
    prepare_and_run("ffuf",
        lambda tgt, prt, wl, out: (
            f"ffuf -u http://{tgt}:{prt}/FUZZ -w {wl} -o {out} -of md; "
            "read -p 'Press enter to return to menu...'"
        )
    )

def run_feroxbuster():
    prepare_and_run("feroxbuster",
        lambda tgt, prt, wl, out: (
            f"feroxbuster -u http://{tgt}:{prt} -w {wl} -o {out}; "
            "read -p 'Press enter to return to menu...'"
        )
    )

def run_dirb():
    prepare_and_run("dirb",
        lambda tgt, prt, wl, out: (
            f"dirb http://{tgt}:{prt} {wl} -o {out}; "
            "read -p 'Press enter to return to menu...'"
        )
    )

def main():
    options = {
        "1": ("Gobuster",     run_gobuster),
        "2": ("ffuf",         run_ffuf),
        "3": ("Feroxbuster",  run_feroxbuster),
        "4": ("dirb",         run_dirb),
        "5": ("Exit",         None),
    }

    show_banner()
    while True:
        console.print("\n[bold magenta]=== Directory Traversal Automation ===[/bold magenta]")
        for key, (name, _) in options.items():
            console.print(f"[cyan][{key}][/cyan] {name}")
        choice = Prompt.ask("👉 Select an option", default="1").strip()
        if choice == "5":
            console.print("[bold green]Exiting...[/bold green]")
            break
        action = options.get(choice)
        if action:
            _, func = action
            func()
        else:
            console.print("[red]Invalid selection, please choose 1-5.[/red]")

if __name__ == "__main__":
    main()
