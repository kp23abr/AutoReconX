#!/usr/bin/env python3
"""
subdomain_enumeration.py

CLI-based subdomain enumeration automation tool with animations and output saving.
Supports ffuf, sublist3r, subfinder, gobuster.
Each tool runs in its own tmux session with optional custom wordlist, port, and filter options.
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

DEFAULT_WORDLIST = "/usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt"

TMUX_CMD = shutil.which("tmux")
if not TMUX_CMD:
    console.print("[bold red]Error:[/bold red] tmux is not installed.")
    sys.exit(1)

def show_banner():
    banner_text = "[bold cyan]Subdomain Enumeration Tool[/bold cyan]\n[italic yellow]by Kumar[/italic yellow]"
    panel = Panel(banner_text, expand=False, box=box.DOUBLE)
    console.print(panel)

def ask_common_inputs(tool):
    try:
        host = Prompt.ask("🌐 [cyan]Enter target Host/IP[/cyan]")
        port = Prompt.ask("🔗 [cyan]Port[/cyan]", default="80")
        use_default = Confirm.ask("📂 [cyan]Use default wordlist?[/cyan]", default=True)
        if use_default:
            wordlist = DEFAULT_WORDLIST
        else:
            wordlist = Prompt.ask("📄 [cyan]Path to your custom wordlist[/cyan]")
        return host.strip(), port.strip(), wordlist.strip()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Cancelled.[/bold yellow] Returning to main menu.")
        return None, None, None

def ask_filter_options():
    fs = Prompt.ask("[cyan]Enter -fs (filter size) if needed[/cyan]", default="", show_default=False)
    fw = Prompt.ask("[cyan]Enter -fw (filter words) if needed[/cyan]", default="", show_default=False)
    return fs.strip(), fw.strip()

def ask_output_path(tool):
    filename = Prompt.ask("📅 [green]Enter output filename[/green]", default=f"{tool}_output.txt")
    path = Prompt.ask("📁 [cyan]Enter output directory[/cyan] (leave blank for current directory)", default="")
    return os.path.join(path.strip() or ".", filename.strip())

def launch_in_tmux(tool_name, command, output_path=None):
    try:
        session_name = f"{tool_name}_session"
        subprocess.call(["tmux", "kill-session", "-t", session_name], stderr=subprocess.DEVNULL)
        if output_path:
            command += f" | tee {output_path}; read -p 'Press enter to return to menu...'"
        else:
            command += "; read -p 'Press enter to return to menu...'"

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            progress.add_task("Spawning tmux session...", total=None)
            time.sleep(1)

        subprocess.call(["tmux", "new-session", "-s", session_name, "sh", "-c", command])
        console.print(f"\n✅ [green]{tool_name} session ended.[/green] Returning to menu...\n")
    except Exception as e:
        console.print(f"[bold red]Error launching '{tool_name}':[/bold red] {e}")

def run_ffuf():
    host, port, wordlist = ask_common_inputs("ffuf")
    if not host:
        return
    fs, fw = ask_filter_options()
    output_path = ask_output_path("ffuf")
    filter_flags = f"-fs {fs}" if fs else (f"-fw {fw}" if fw else "")
    cmd = f"ffuf -w {wordlist} -u http://{host}:{port} -H \"Host: FUZZ.{host}\" {filter_flags}"
    launch_in_tmux("ffuf", cmd, output_path)

def run_sublist3r():
    host = Prompt.ask("🌐 [cyan]Enter domain name for Sublist3r[/cyan]")
    output_path = ask_output_path("sublist3r")
    cmd = f"sublist3r -d {host} -o {output_path}"
    launch_in_tmux("sublist3r", cmd)

def run_subfinder():
    host = Prompt.ask("🌐 [cyan]Enter domain name for Subfinder[/cyan]")
    output_path = ask_output_path("subfinder")
    cmd = f"subfinder -d {host} -o {output_path}"
    launch_in_tmux("subfinder", cmd)

def run_gobuster():
    host, port, wordlist = ask_common_inputs("gobuster")
    if not host:
        return
    output_path = ask_output_path("gobuster")
    cmd = f"gobuster dns -d {host} -w {wordlist} -o {output_path}"
    launch_in_tmux("gobuster", cmd)

def main():
    options = {
        "1": ("ffuf", run_ffuf),
        "2": ("sublist3r", run_sublist3r),
        "3": ("subfinder", run_subfinder),
        "4": ("gobuster", run_gobuster),
        "5": ("Exit", None),
    }

    show_banner()

    while True:
        console.print("\n[bold magenta]=== Subdomain Enumeration Menu ===[/bold magenta]")
        for key, (name, _) in options.items():
            console.print(f"[cyan][{key}][/cyan] {name}")
        try:
            choice = Prompt.ask("👉 Select an option", default="1").strip()
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
                console.print("\n[bold yellow]Interrupted. Back to menu.[/bold yellow]")
        else:
            console.print("[red]Invalid selection. Choose between 1-5.[/red]")

if __name__ == "__main__":
    main()
