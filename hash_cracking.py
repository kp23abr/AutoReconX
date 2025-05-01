#!/usr/bin/env python3
# by Kumar
"""
Password Cracking Tool
Supports: hash-identifier, hashcat, john
Each runs in its own tmux session.
Prompt sequence for each tool:
 1. For all: ask output filename & directory (blank → auto timestamped folder)
 2. For hashcat/john: ask hash input type, then value/path, then wordlist/mode
Hash-identifier runs interactively in tmux (user types hash there).
All output is both live in tmux and saved via tee.
"""
import subprocess
import os
import shutil
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt

console = Console()

# Banner
console.print("[bold bright_cyan]╔══════════════════════════════╗[/bold bright_cyan]")
console.print("[bold bright_cyan]║ Password Cracking Tool       ║[/bold bright_cyan]")
console.print("[bold bright_cyan]║ by Kumar                     ║[/bold bright_cyan]")
console.print("[bold bright_cyan]╚══════════════════════════════╝[/bold bright_cyan]")

TMUX = shutil.which("tmux")
if not TMUX:
    console.print("[bold red]Error:[/bold red] tmux is not installed.")
    exit(1)

def ask_output_manual(tool):
    fn = Prompt.ask(f"💾 Enter output filename (without extension) for {tool}", default="").strip()
    d  = Prompt.ask("📂 Enter output directory (leave blank for auto)", default="").strip()
    return fn, d

def make_auto_folder(base):
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder = f"{base.replace('.', '_')}_{ts}"
    os.makedirs(folder, exist_ok=True)
    return folder

def run_identifier():
    # 1) ask output naming
    fn, d = ask_output_manual("hash-identifier")
    if fn == "" and d == "":
        folder = make_auto_folder("identifier")
        out = os.path.join(folder, "identifier.txt")
    else:
        folder = d or "."
        os.makedirs(folder, exist_ok=True)
        out = os.path.join(folder, f"{fn or 'identifier'}.txt")

    # 2) launch tmux session: user types hash interactively
    session = "hash-identifier_session"
    subprocess.call([TMUX, "kill-session", "-t", session], stderr=subprocess.DEVNULL)
    # tee captures all output, read pauses at end
    full = f"hash-identifier 2>&1 | tee {out}; read -p 'Press enter to return...'"
    subprocess.call([TMUX, "new-session", "-s", session, "sh", "-c", full])
    console.print(f"[green]Logs & results saved to {out}[/green]")

def run_hashcat():
    # 1) select hash input
    kind = Prompt.ask("💬 Provide hash or file?", choices=["hash","file"], default="hash")
    if kind == "hash":
        hv = Prompt.ask("🔑 Enter the hash value").strip()
        tmp = ".hc_tmp_hash"
        with open(tmp, "w") as f:
            f.write(hv + "\n")
        target = tmp
        base = hv
    else:
        target = Prompt.ask("📂 Enter path to hash file").strip()
        base = os.path.splitext(os.path.basename(target))[0]

    # 2) wordlist & mode
    wl   = Prompt.ask("🔑 Enter path to wordlist", default="/usr/share/wordlists/rockyou.txt").strip()
    mode = Prompt.ask("🔑 Enter hashcat mode (e.g. 0 for MD5)", default="0").strip()

    # 3) output naming
    fn, d = ask_output_manual("hashcat")
    if fn == "" and d == "":
        folder = make_auto_folder(base)
        out = os.path.join(folder, f"hashcat_{base}.txt")
    else:
        folder = d or "."
        os.makedirs(folder, exist_ok=True)
        out = os.path.join(folder, f"{fn or 'hashcat'} .txt".replace(" .txt",".txt"))

    # 4) build & run
    crack = f"hashcat -m {mode} -a 0 {target} {wl} -o {out}"
    show  = f"hashcat -m {mode} -a 0 {target} {wl} --show >> {out}"
    cmd   = f"{crack} && {show}"
    session = "hashcat_session"
    subprocess.call([TMUX, "kill-session", "-t", session], stderr=subprocess.DEVNULL)
    full = f"{cmd} 2>&1 | tee -a {out}; read -p 'Press enter to return...'"
    subprocess.call([TMUX, "new-session", "-s", session, "sh", "-c", full])
    console.print(f"[green]Logs & results saved to {out}[/green]")

def run_john():
    # 1) select hash input
    kind = Prompt.ask("💬 Provide hash or file?", choices=["hash","file"], default="hash")
    if kind == "hash":
        hv = Prompt.ask("🔑 Enter the hash value").strip()
        tmp = ".john_tmp_hash"
        with open(tmp, "w") as f:
            f.write(hv + "\n")
        target = tmp
        base = hv
    else:
        target = Prompt.ask("📂 Enter path to hash file").strip()
        base = os.path.splitext(os.path.basename(target))[0]

    # 2) wordlist
    wl = Prompt.ask("🔑 Enter path to wordlist", default="/usr/share/wordlists/rockyou.txt").strip()

    # 3) output naming
    fn, d = ask_output_manual("john")
    if fn == "" and d == "":
        folder = make_auto_folder(base)
        out = os.path.join(folder, f"john_{base}.txt")
    else:
        folder = d or "."
        os.makedirs(folder, exist_ok=True)
        out = os.path.join(folder, f"{fn or 'john'}.txt")

    # 4) build & run
    crack = f"john --wordlist={wl} --format=raw-md5 {target}"
    show  = f"john --show --format=raw-md5 {target} >> {out}"
    cmd   = f"{crack} && {show}"
    session = "john_session"
    subprocess.call([TMUX, "kill-session", "-t", session], stderr=subprocess.DEVNULL)
    full = f"{cmd} 2>&1 | tee -a {out}; read -p 'Press enter to return...'"
    subprocess.call([TMUX, "new-session", "-s", session, "sh", "-c", full])
    console.print(f"[green]Logs & results saved to {out}[/green]")

def main():
    while True:
        console.print("\n[bold magenta]=== Password Cracking Menu ===[/bold magenta]")
        console.print("[cyan]\n[1][/cyan] hash-identifier")
        console.print("[cyan]\n[2][/cyan] hashcat")
        console.print("[cyan]\n[3][/cyan] john")
        console.print("[cyan]\n[4][/cyan] Exit\n")
        choice = Prompt.ask("👉 Select an option", choices=["1","2","3","4"], default="1")
        if choice == "1":
            run_identifier()
        elif choice == "2":
            run_hashcat()
        elif choice == "3":
            run_john()
        else:
            console.print("[bold green]Exiting...[/bold green]")
            break

if __name__ == "__main__":
    main()
