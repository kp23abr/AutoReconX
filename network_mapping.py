#!/usr/bin/env python3

import subprocess
import sys
import os
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich import box

console = Console()

def print_banner():
    banner_text = "[bold cyan]Network Mapping Tool[/bold cyan]\n[italic yellow]by Kumar Pachiyappan[/italic yellow]"
    panel = Panel(banner_text, expand=False, box=box.DOUBLE)
    console.print(panel)

def run_command(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except FileNotFoundError:
        return f"Error: {cmd[0]} not found. Ensure it is installed and in your PATH."
    except subprocess.CalledProcessError as e:
        return f"Error running {' '.join(cmd)}:\n{e.stdout}\n{e.stderr}"

def run_nmap(target, mode):
    return run_command(['nmap', '-T4', '-F', target] if mode == 'fast' else ['nmap', target, '-sV', '-sC', '-A'])

def run_traceroute(target, mode):
    return run_command(['traceroute', '-n', '-q', '1', target] if mode == 'fast' else ['traceroute', target])

def extract_whois_server(output):
    for line in output.splitlines():
        if 'Whois Server:' in line or 'Registrar WHOIS Server:' in line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                return parts[1].strip()
    return None

def run_whois(target, mode):
    first = run_command(['whois', target])
    if mode == 'fast':
        return first
    server = extract_whois_server(first)
    return f"{first}\n{run_command(['whois', '-h', server, target])}" if server else first

def run_dnsrecon(target, mode):
    return run_command(['dnsrecon', '-d', target] if mode == 'fast' else ['dnsrecon', '-d', target, '-a'])

def run_arp_scan(_, mode):
    return run_command(['sudo', 'arp-scan', '-l'] if mode == 'fast' else ['sudo', 'arp-scan', '--localnet', '--retry', '3', '--verbose'])

def run_netdiscover(target, mode):
    return run_command(['netdiscover', '-r', target] if mode == 'fast' else ['netdiscover', '-r', target, '-P'])

def run_hping3(target, mode):
    return run_command(['hping3', '-S', target, '-p', '1-1024', '-c', '100'] if mode == 'fast' else ['hping3', '--flood', '-S', '-V', '-p', '1-65535', target])

def run_tshark(target, mode):
    return run_command(['tshark', '-c', '100', '-f', f'host {target}'] if mode == 'fast' else ['tshark', '-w', 'capture.pcap', '-f', f'host {target}'])

def run_sslscan(target, mode):
    return run_command(['sslscan', f'{target}:443'] if mode == 'fast' else ['sslscan', '--no-failed', f'{target}:443'])

def run_snmpwalk(target, mode):
    return run_command(['snmpwalk', '-v1', '-c', 'public', target] if mode == 'fast' else ['snmpwalk', '-v2c', '-c', 'public', target])

def save_to_file(folder, filename, content):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    try:
        with open(path, 'w') as f:
            f.write(content)
        console.print(f"[green]✅ Results saved to[/green] [bold]{path}[/bold]")
    except Exception as e:
        console.print(f"[red]❌ Failed to save {path}: {e}[/red]")

def individual_scan(choice, target, mode, folder):
    tools = {
        '1': ('nmap', run_nmap),
        '2': ('traceroute', run_traceroute),
        '3': ('whois', run_whois),
        '4': ('dnsrecon', run_dnsrecon),
        '5': ('arp-scan', run_arp_scan),
        '6': ('netdiscover', run_netdiscover),
        '7': ('hping3', run_hping3),
        '8': ('tshark', run_tshark),
        '9': ('sslscan', run_sslscan),
        '10': ('snmpwalk', run_snmpwalk)
    }
    tool, func = tools.get(choice, (None, None))
    if not func:
        console.print("[red]Invalid option.[/red]")
        return
    console.print(f"[cyan]🔍 Running [bold]{tool}[/bold] against {target} in {mode} mode...[/cyan]")
    output = func(target, mode)
    console.print(f"\n[white]{output}[/white]")
    save_to_file(folder, f"{tool}_{target}.txt", output)

def network_mapping_menu():
    print_banner()
    while True:
        console.print("\n[bold magenta]=== Network Mapping Menu ===[/bold magenta]")
        console.print("[cyan][1][/cyan] nmap")
        console.print("[cyan][2][/cyan] traceroute")
        console.print("[cyan][3][/cyan] whois")
        console.print("[cyan][4][/cyan] dnsrecon")
        console.print("[cyan][5][/cyan] arp-scan")
        console.print("[cyan][6][/cyan] netdiscover")
        console.print("[cyan][7][/cyan] hping3")
        console.print("[cyan][8][/cyan] tshark")
        console.print("[cyan][9][/cyan] sslscan")
        console.print("[cyan][10][/cyan] snmpwalk")
        console.print("[cyan][0][/cyan] Exit")

        choice = Prompt.ask("👉 Select an option").strip()

        if choice == '0':
            console.print("[bold green]Exiting Network Mapping Module...[/bold green]")
            break
        if choice not in [str(i) for i in range(11)]:
            console.print("[red]❌ Invalid choice. Please try again.[/red]")
            continue

        try:
            target = Prompt.ask("🎯 Enter target (domain, IP, or network range)").strip()
            if not target:
                console.print("[red]Target cannot be empty.[/red]")
                continue
        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled. Returning to menu.[/yellow]")
            continue

        mode = Prompt.ask("⚙️ Select mode [fast/deep]", default="fast").strip().lower()
        if mode not in ['fast', 'deep']:
            console.print("[red]❌ Invalid mode. Defaulting to 'fast'.[/red]")
            mode = 'fast'

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        folder = f"{target.replace('.', '_')}_{timestamp}"

        individual_scan(choice, target, mode, folder)

if __name__ == '__main__':
    try:
        network_mapping_menu()
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted. Exiting.[/bold red]")
        sys.exit(0)
