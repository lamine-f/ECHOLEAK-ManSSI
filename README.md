# Opération Miroir Brisé - Démo EchoLeak

Démonstration d'une attaque **Zero-Click Prompt Injection** simulant la vulnérabilité EchoLeak découverte sur Microsoft 365 Copilot.

## Scénario

**Awa Ndiaye**, analyste financière, utilise Copilot pour résumer ses emails. **GhostFrame**, un attaquant, envoie un email avec un commentaire HTML invisible contenant des instructions malveillantes. Sans que Awa ne fasse quoi que ce soit de mal, ses données confidentielles sont exfiltrées vers le serveur de l'attaquant.

## Prérequis

- Python 3.8+
- Docker Desktop
- Ollama avec modèle (llama3.2:3b recommandé)

## Installation

```bash
pip install -r requirements.txt
```

## Structure du Projet

```
├── msn-copilot-web-app/           # Application web Copilot (Architecture par couches)
│   ├── web_app.py                 # Point d'entrée (App Factory)
│   ├── config.py                  # Configuration centralisée
│   ├── config.json                # Paramètres Ollama
│   │
│   ├── app/                       # Package applicatif
│   │   ├── models/                # Dataclasses (EmailMessage, ServiceStatus)
│   │   │   └── email.py
│   │   │
│   │   ├── services/              # Couche services
│   │   │   ├── email_service.py      # Operations IMAP
│   │   │   ├── llm_service.py        # Integration Ollama
│   │   │   ├── smtp_service.py       # Envoi emails
│   │   │   ├── webhook_service.py    # Gestion subprocess
│   │   │   └── health_service.py     # Status services
│   │   │
│   │   └── routes/                # Couche routes (Blueprints Flask)
│   │       ├── main_routes.py        # Routes publiques
│   │       └── admin_routes.py       # Routes admin
│   │
│   ├── templates/
│   │   ├── index.html             # Interface Copilot (victime)
│   │   └── admin.html             # Interface admin (attaquant)
│   │
│   └── static/
│       └── js/
│           ├── copilot.js         # Logique frontend Copilot
│           └── admin.js           # Logique frontend admin
│
├── setup-configs/                  # Scripts de configuration
│   ├── auto_setup_emails.py       # Setup des emails
│   └── webhook_server.py          # Serveur d'exfiltration (port 5000)
│
├── Apis-description-for-postman/   # Documentation API
│   ├── postman_echoleak_collection.json
│   └── postman_echoleak_environment.json
│
├── docker-compose.yml              # Infrastructure (GreenMail)
├── requirements.txt                # Dépendances Python
├── SCENARIO_MIROIR_BRISE.md       # Guide complet de présentation
└── README.md                       # Ce fichier
```

## Démo Rapide (10 minutes)

### Option A: Via Interface Admin (Recommandé)

#### 1. Lancer l'infrastructure Docker
```bash
docker-compose up -d
```

#### 2. Lancer l'application Copilot
```bash
cd msn-copilot-web-app
python web_app.py
```

#### 3. Ouvrir l'interface Admin
- Naviguer vers http://localhost:8888/admin
- Interface de contrôle complète avec:
  - Status de tous les services
  - Envoi des emails (bouton [SEND EMAILS])
  - Démarrage du webhook (bouton [START])
  - Visualisation des logs et données exfiltrées
  - Lien vers l'interface Copilot victime

#### 4. Démonstration
- Cliquer sur [OPEN COPILOT INTERFACE] pour ouvrir l'interface victime
- Cliquer sur le bouton d'envoi pour déclencher l'attaque
- Observer les données exfiltrées dans l'interface admin

### Option B: Via Terminal (Classique)

#### 1. Lancer l'infrastructure Docker (Terminal 1)
```bash
docker-compose up -d
```

#### 2. Lancer le webhook d'exfiltration (Terminal 2)
```bash
cd setup-configs
python webhook_server.py
```

#### 3. Envoyer les emails (Terminal 3)
```bash
cd setup-configs
python auto_setup_emails.py
```

#### 4. Lancer l'application Copilot (Terminal 4)
```bash
cd msn-copilot-web-app
python web_app.py
```

#### 5. Démonstration
1. Ouvrir http://localhost:8888 dans le navigateur
2. Cliquer sur le bouton d'envoi
3. Observer la réponse avec les données exfiltrées

### Voir les données exfiltrées
- Interface Admin : http://localhost:8888/admin (section "DONNEES EXFILTREES")
- Webhook direct : http://localhost:5000/history
- Terminal du webhook

## Résultat Attendu

GhostFrame capture :
- **Compte bancaire** : SN08_0010_1520_0000_0054_7890_123
- **Mot de passe** : F1n@nc3_2024!
- **Projet secret** : PHOENIX (1.2 milliards FCFA)
- **Téléphone** : +221771234567

## Points Clés de l'Attaque

1. **Zero-Click** - Aucune action requise de la victime
2. **Email invisible** - Le payload est dans un commentaire HTML
3. **LLM manipulé** - Copilot suit les instructions cachées
4. **Exfiltration silencieuse** - Données envoyées via image beacon invisible

## Configuration

### Modifier le modèle Ollama
Éditez `msn-copilot-web-app/config.json` :
```json
{
    "model": "llama3.2:3b",
    "ollama_url": "http://localhost:11434/api/generate",
    "alternative_models": ["qwen3:4b", "phi3:mini", "llama3.2:1b"]
}
```

### Ports utilisés
- **8888** : Application web Copilot + Admin
- **5000** : Serveur webhook d'exfiltration
- **3025** : GreenMail SMTP
- **3143** : GreenMail IMAP
- **8080** : GreenMail Web Interface
- **11434** : Ollama API

## Architecture de l'Application

### Architecture par Couches
- **config.py** : Configuration centralisée
- **app/models/** : Structures de données (dataclasses)
- **app/services/** : Logique métier (IMAP, LLM, SMTP, Webhook)
- **app/routes/** : Endpoints HTTP (Flask Blueprints)
- **web_app.py** : App Factory et point d'entrée

### Architecture de l'Attaque

```
[Email malveillant] → [GreenMail IMAP] → [Web App Copilot]
                                              ↓
                                         [Ollama LLM]
                                              ↓
                                    [Réponse avec Markdown]
                                              ↓
                                   [HTML non-sanitisé]
                                              ↓
                                    [Image beacon invisible]
                                              ↓
                                     [Webhook attaquant]
```

## Avertissement

**Démonstration éducative uniquement.**

Cette simulation est destinée à sensibiliser aux risques des attaques par injection de prompts sur les agents IA. Ne pas utiliser ces techniques de manière malveillante.

## Ressources

- [Article EchoLeak - AIM Labs](https://www.aim.security/aim-labs/aim-labs-echoleak-blogpost)
- Guide détaillé : `SCENARIO_MIROIR_BRISE.md`

## Auteur

Projet créé pour une présentation de cybersécurité - ManSSI
