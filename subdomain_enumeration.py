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
from datetime import datetime
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
        host = Prompt.ask("🌐 [cyan]Enter target Host/IP[/cyan]").strip()
        port = Prompt.ask("🔗 [cyan]Port[/cyan]", default="80").strip()
        use_default = Confirm.ask("📂 [cyan]Use default wordlist?[/cyan]", default=True)
        wordlist = DEFAULT_WORDLIST if use_default else Prompt.ask("📄 [cyan]Path to your custom wordlist[/cyan]").strip()
        return host, port, wordlist
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Cancelled.[/bold yellow] Returning to main menu.")
        return None, None, None

def ask_filter_options():
    fs = Prompt.ask("[cyan]Enter -fs (filter size) if needed[/cyan]", default="", show_default=False).strip()
    fw = Prompt.ask("[cyan]Enter -fw (filter words) if needed[/cyan]", default="", show_default=False).strip()
    return fs, fw

# --- NEW: manual vs auto output ---
def ask_output_manual(tool):
    filename = Prompt.ask(f"💾 Enter output filename (without extension) for {tool}", default="").strip()
    directory = Prompt.ask("📂 Enter output directory (leave blank for auto)", default="").strip()
    return filename, directory

def make_auto_folder(name):
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder = f"{name.replace('.', '_')}_{ts}"
    os.makedirs(folder, exist_ok=True)
    return folder
# --------------------------------------

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
    fn, dir_ = ask_output_manual("ffuf")
    if fn == "" and dir_ == "":
        folder = make_auto_folder(host)
        output_path = os.path.join(folder, f"ffuf_{host}.txt")
    else:
        if dir_:
            os.makedirs(dir_, exist_ok=True)
        else:
            dir_ = "."
        output_path = os.path.join(dir_, f"{fn or 'ffuf_output'}.txt")

    filter_flags = f"-fs {fs}" if fs else (f"-fw {fw}" if fw else "")
    cmd = f"ffuf -w {wordlist} -u http://{host}:{port} -H \"Host: FUZZ.{host}\" {filter_flags}"
    launch_in_tmux("ffuf", cmd, output_path)

def run_sublist3r():
    host = Prompt.ask("🌐 [cyan]Enter domain name for Sublist3r[/cyan]").strip()
    if not host:
        return
    fn, dir_ = ask_output_manual("sublist3r")
    if fn == "" and dir_ == "":
        folder = make_auto_folder(host)
        output_path = os.path.join(folder, f"sublist3r_{host}.txt")
    else:
        if dir_:
            os.makedirs(dir_, exist_ok=True)
        else:
            dir_ = "."
        output_path = os.path.join(dir_, f"{fn or 'sublist3r_output'}.txt")

    cmd = f"sublist3r -d {host} -o {output_path}"
    launch_in_tmux("sublist3r", cmd)

def run_subfinder():
    host = Prompt.ask("🌐 [cyan]Enter domain name for Subfinder[/cyan]").strip()
    if not host:
        return
    fn, dir_ = ask_output_manual("subfinder")
    if fn == "" and dir_ == "":
        folder = make_auto_folder(host)
        output_path = os.path.join(folder, f"subfinder_{host}.txt")
    else:
        if dir_:
            os.makedirs(dir_, exist_ok=True)
        else:
            dir_ = "."
        output_path = os.path.join(dir_, f"{fn or 'subfinder_output'}.txt")

    cmd = f"subfinder -d {host} -o {output_path}"
    launch_in_tmux("subfinder", cmd)

def run_gobuster():
    host, port, wordlist = ask_common_inputs("gobuster")
    if not host:
        return
    fn, dir_ = ask_output_manual("gobuster")
    if fn == "" and dir_ == "":
        folder = make_auto_folder(host)
        output_path = os.path.join(folder, f"gobuster_{host}.txt")
    else:
        if dir_:
            os.makedirs(dir_, exist_ok=True)
        else:
            dir_ = "."
        output_path = os.path.join(dir_, f"{fn or 'gobuster_output'}.txt")

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
