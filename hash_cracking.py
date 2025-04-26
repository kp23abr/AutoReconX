#!/usr/bin/env python3
# by Kumar
import subprocess
import os
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
import shutil

console = Console()

# Banner
console.print("[bold bright_cyan]╔══════════════════════════════╗[/bold bright_cyan]")
console.print("[bold bright_cyan]║ Password Cracking Tool       ║[/bold bright_cyan]")
console.print("[bold bright_cyan]║ by Kumar                     ║[/bold bright_cyan]")
console.print("[bold bright_cyan]╚══════════════════════════════╝[/bold bright_cyan]")

DEFAULT_OUTPUT = "crack_output.txt"
TMUX_CMD = shutil.which("tmux")
if not TMUX_CMD:
    console.print("[bold red]Error:[/bold red] tmux is not installed.")
    exit(1)

def ask_common_inputs_for_hashcat_john():
    try:
        hash_or_file = Prompt.ask(
            "💬 Do you want to provide a hash file path or a hash value? (Enter 'file' or 'hash')",
            choices=["file", "hash"],
            default="hash"
        )
        if hash_or_file == "hash":
            hash_value = Prompt.ask("🔑 Enter the hash value directly")
            return hash_value.strip(), None
        else:
            hash_file = Prompt.ask("📂 Enter the path to the hash file")
            return None, hash_file.strip()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Cancelled.[/bold yellow] Returning to main menu.")
        return None, None

def ask_wordlist_and_mode():
    wordlist = Prompt.ask("🔑 Enter the path to the wordlist", default="/usr/share/wordlists/rockyou.txt")
    mode     = Prompt.ask("🔑 Enter the hash mode (default MD5, 0 for MD5)", default="0")
    return wordlist.strip(), mode.strip()

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
# ----------------------------------------

def launch_in_tmux(tool_name, command, output_path=None):
    try:
        session_name = f"{tool_name}_session"
        subprocess.call(["tmux", "kill-session", "-t", session_name], stderr=subprocess.DEVNULL)
        if output_path:
            command += f" > {output_path} 2>&1; read -p 'Press enter to return to menu...'"
        else:
            command += "; read -p 'Press enter to return to menu...'"
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            progress.add_task("Spawning tmux session...", total=None)
        subprocess.call(["tmux", "new-session", "-s", session_name, "sh", "-c", command])
        console.print(f"\n✅ {tool_name} session ended. Returning to menu...\n")
    except Exception as e:
        console.print(f"[bold red]Error launching '{tool_name}':[/bold red] {e}")

def run_hashcat():
    hash_value, hash_file = ask_common_inputs_for_hashcat_john()
    if not hash_value and not hash_file:
        return
    wordlist, mode = ask_wordlist_and_mode()

    fn, dir_ = ask_output_manual("hashcat")
    if fn == "" and dir_ == "":
        target = "temp_hash" if hash_value else os.path.splitext(os.path.basename(hash_file))[0]
        folder = make_auto_folder(target)
        output_path = os.path.join(folder, f"hashcat_{target}.txt")
    else:
        if dir_:
            os.makedirs(dir_, exist_ok=True)
        else:
            dir_ = "."
        output_path = os.path.join(dir_, f"{fn or 'hashcat_output'}.txt")

    if hash_value:
        cmd = f"echo '{hash_value}' > temp_hash.txt && hashcat -m {mode} temp_hash.txt {wordlist} -o {output_path}"
    else:
        cmd = f"hashcat -m {mode} -a 0 -o {output_path} {hash_file} {wordlist}"

    launch_in_tmux("hashcat", cmd, output_path)

def run_john():
    hash_value, hash_file = ask_common_inputs_for_hashcat_john()
    if not hash_value and not hash_file:
        return
    wordlist, _ = ask_wordlist_and_mode()

    fn, dir_ = ask_output_manual("john")
    if fn == "" and dir_ == "":
        target = "temp_hash" if hash_value else os.path.splitext(os.path.basename(hash_file))[0]
        folder = make_auto_folder(target)
        output_path = os.path.join(folder, f"john_{target}.txt")
    else:
        if dir_:
            os.makedirs(dir_, exist_ok=True)
        else:
            dir_ = "."
        output_path = os.path.join(dir_, f"{fn or 'john_output'}.txt")

    if hash_value:
        with open("temp_hash.txt", "w") as f:
            f.write(hash_value + "\n")
        cmd = f"john --wordlist={wordlist} --format=raw-md5 temp_hash.txt && john --show --format=raw-md5 temp_hash.txt > {output_path}"
    else:
        cmd = f"john --wordlist={wordlist} --format=raw-md5 {hash_file} && john --show --format=raw-md5 {hash_file} > {output_path}"

    launch_in_tmux("john", cmd, output_path)

def main():
    while True:
        console.print("\n[bold magenta]=== Password Cracking Menu ===[/bold magenta]")
        console.print("[cyan][1][/cyan] hash-identifier")
        console.print("[cyan][2][/cyan] hashcat")
        console.print("[cyan][3][/cyan] john")
        console.print("[cyan][4][/cyan] Exit")

        choice = Prompt.ask("👉 Select an option", default="1").strip()

        if choice == "1":
            console.print("[bold green]Running hash-identifier...[/bold green]")
            cmd = "hash-identifier"
            launch_in_tmux("hash-identifier", cmd)
        elif choice == "2":
            run_hashcat()
        elif choice == "3":
            run_john()
        elif choice == "4":
            console.print("[bold green]Exiting...[/bold green]")
            break
        else:
            console.print("[red]Invalid selection. Choose between 1-4.[/red]")

if __name__ == "__main__":
    main()
