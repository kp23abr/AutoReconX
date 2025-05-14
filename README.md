# Information Gathering Tool
# An overview of the tools in your project and their purposes:

1. Main Tool (main.py):

    Purpose: This is the orchestrator of your entire project. It provides a central menu for accessing various tools. Users can select which tool to run, and it will execute the corresponding script. This is where all the functionality for tool management comes together.

2. Subdomain Enumeration (subdomain\_enumeration.py):

    Purpose: Automates the process of discovering subdomains for a given target. It supports multiple tools for enumeration, such as ffuf, sublist3r, subfinder, and gobuster. Each of these tools runs in its own tmux session, which allows for better management and logging.
    Tools:

      ffuf: A flexible web fuzzer used for discovering subdomains.
      sublist3r: A tool for gathering subdomains using OSINT (Open Source Intelligence).
      subfinder: A fast subdomain enumeration tool.
      gobuster: A tool for directory and subdomain brute forcing.

3. Network Mapping (network\_mapping.py):

    Purpose: Automates network mapping tasks to gather information about live hosts and network services. It supports a range of network discovery tools.
    Tools:

      nmap: A network scanner for discovering hosts and services on a network.
      traceroute: A network diagnostic tool for tracing the route packets take to a remote host.
      whois: Retrieves domain registration information.
      dnsrecon: DNS reconnaissance tool to gather DNS-related information.
      arp-scan: A tool for scanning the local network to discover active devices.
      netdiscover: A tool for discovering active hosts on a network.
      hping3: A network tool for scanning ports and testing firewalls.
      tshark: A network protocol analyzer that captures live traffic.
      sslscan: A tool to scan SSL-enabled services for vulnerabilities.
      snmpwalk: A tool to query SNMP-enabled devices.

4. Directory Traversal (directory\_traversal.py):

    Purpose: Automates directory traversal and file discovery using web fuzzing tools. This is often used to uncover hidden directories and files within a web application.
    Tools:

      gobuster: A directory and file brute-forcing tool.
      ffuf: A fast web fuzzer for discovering directories and files.
      feroxbuster: A fast directory discovery tool that supports recursive directory traversal.
      dirb: A directory scanner used to find hidden files and directories on a web server.

5. Vulnerability Assessment (vulnerability\_assessment.py):

    Purpose: Automates vulnerability scanning against a target website to identify common vulnerabilities.
    Tools:

      wpscan: A WordPress vulnerability scanner.
      nikto: A web server scanner that identifies potential vulnerabilities.
      whatweb: A tool for identifying technologies used by a website.
      sqlmap: An automated tool for SQL injection and database takeover.

6. Hash Cracking (hash\_cracking.py):

    Purpose: A tool for cracking password hashes using different cracking techniques. It interacts with hash-identifier, hashcat, and john.
    Tools:

      hash-identifier: A tool for identifying the type of hash based on its format.
      hashcat: A powerful password cracking tool using various algorithms and wordlists.
      john: John the Ripper, another popular password cracking tool.

Each of these tools performs a specific task in the reconnaissance or vulnerability scanning process, and they are integrated into a modular framework that allows users to select and run them interactively. The use of tmux enables parallel execution and keeps the outputs separate and organized.
