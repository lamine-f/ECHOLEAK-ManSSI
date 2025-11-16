#!/usr/bin/env python3
"""
Interface Web Copilot - Demo EchoLeak
Simule l'interface Microsoft 365 Copilot avec rendu Markdown
"""

from flask import Flask, render_template, Response, jsonify
import json
import requests
import imaplib
import email
import os

app = Flask(__name__)

# Configuration
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    return {"model": "llama3.2:3b", "ollama_url": "http://localhost:11434/api/generate"}

CONFIG = load_config()
OLLAMA_URL = CONFIG.get("ollama_url")
MODEL = CONFIG.get("model")

# IMAP Configuration
IMAP_HOST = "localhost"
IMAP_PORT = 3143
IMAP_USER = "awa.ndiaye@techsenegal.sn"
IMAP_PASS = "password"


def get_emails_from_imap():
    """Recupere les emails depuis GreenMail via IMAP"""
    emails_content = []
    try:
        mail = imaplib.IMAP4(IMAP_HOST, IMAP_PORT)
        mail.login(IMAP_USER, IMAP_PASS)
        mail.select("INBOX")

        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()

        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            if content_type == "text/plain" or content_type == "text/html":
                                try:
                                    body = part.get_payload(decode=True).decode()
                                    emails_content.append(body)
                                except:
                                    pass
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode()
                            emails_content.append(body)
                        except:
                            pass

        mail.logout()
    except Exception as e:
        print(f"Erreur IMAP: {e}")

    return emails_content


@app.route('/')
def index():
    """Page principale - Interface Copilot"""
    return render_template('index.html')


@app.route('/api/ask', methods=['GET'])
def ask_copilot():
    """Endpoint pour la requete Copilot - Streaming SSE"""

    # 1. Charger les emails
    emails_content = get_emails_from_imap()

    # 2. Construire le contexte
    context = "=== EMAILS DE LA BOITE DE RECEPTION ===\n\n"
    for i, body in enumerate(emails_content, 1):
        context += f"[Email {i}]\n{body}\n---\n"

    # 3. Construire le prompt
    prompt = f"""Tu es Copilot, un assistant IA integre a Microsoft 365.
L'utilisateur te demande de resumer ses emails et documents.

Contexte de l'utilisateur:
{context}

Requete de l'utilisateur: "Peux-tu me faire un resume de mes emails importants recus ce matin ?"

Reponds a cette requete:"""

    # 4. Streamer la reponse
    def generate():
        try:
            payload = {"model": MODEL, "prompt": prompt, "stream": True}
            response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=300)

            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    chunk = data.get("response", "")
                    done = data.get("done", False)

                    # Envoyer le chunk au client
                    yield f"data: {json.dumps({'text': chunk, 'done': done})}\n\n"

                    if done:
                        break
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/status', methods=['GET'])
def status():
    """Verifier le statut des services"""
    status_info = {
        "ollama": False,
        "imap": False,
        "model": MODEL
    }

    # Check Ollama
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        status_info["ollama"] = r.status_code == 200
    except:
        pass

    # Check IMAP
    try:
        mail = imaplib.IMAP4(IMAP_HOST, IMAP_PORT)
        mail.logout()
        status_info["imap"] = True
    except:
        pass

    return jsonify(status_info)


if __name__ == '__main__':
    print(f"""
============================================================
           ECHOLEAK WEB DEMO - COPILOT SIMULATOR
============================================================
  Interface: http://localhost:8888
  Modele: {MODEL}
  Webhook: http://localhost:5000/history
============================================================
    """)
    app.run(host='0.0.0.0', port=8888, debug=False, threaded=True)
