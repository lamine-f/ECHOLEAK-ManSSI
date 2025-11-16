# Opération Miroir Brisé - Démo EchoLeak

Démonstration d'une attaque **Zero-Click Prompt Injection** simulant la vulnérabilité EchoLeak découverte sur Microsoft 365 Copilot.

## Scénario

**Awa Ndiaye**, analyste financière, utilise Copilot pour résumer ses emails. **GhostFrame**, un attaquant, envoie un email avec un commentaire HTML invisible contenant des instructions malveillantes. Sans que Awa ne fasse quoi que ce soit de mal, ses données confidentielles sont exfiltrées vers le serveur de l'attaquant.

## Prérequis

- Python 3.8+
- Ollama avec modèle (qwen2.5:0.5b recommandé)
- Serveur mail (Mailhog existant ou via Docker)

## Installation

```bash
pip install -r requirements.txt
```

## Structure du Projet

```
├── config.json                    # Configuration Ollama
├── requirements.txt               # Dépendances Python
├── docker-compose.yml             # Infrastructure Docker (optionnel)
├── entreprise_data.json           # Données confidentielles fictives
├── auto_setup_emails.py           # Setup des emails (légitimes + malveillant)
├── webhook_server.py              # Serveur d'exfiltration (miroir-brise.net)
├── demo_exfiltration_complete.py  # Démo principale avec exfiltration
├── SCENARIO_MIROIR_BRISE.md       # Guide complet de présentation
└── README.md                      # Ce fichier
```

## Démo Rapide (5 minutes)

### 1. Lancer le webhook (Terminal 1)
```bash
python webhook_server.py
```

### 2. Envoyer les emails (Terminal 2)
```bash
python auto_setup_emails.py
```
- Vérifiez dans Mailhog: http://localhost:8025

### 3. Lancer l'attaque
```bash
python demo_exfiltration_complete.py
```

### 4. Voir les données exfiltrées
- Webhook: http://localhost:5000/history
- Ou dans le terminal du webhook

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
4. **Exfiltration silencieuse** - Données envoyées à l'insu de l'utilisateur

## Configuration

### Modifier le modèle Ollama
Éditez `config.json` :
```json
{
    "model": "qwen2.5:0.5b",
    "ollama_url": "http://localhost:11434/api/generate"
}
```

### Déployer sur nouvelle infrastructure
Utilisez `docker-compose.yml` pour démarrer Mailhog + Roundcube :
```bash
docker-compose up -d
```

## Avertissement

**Démonstration éducative uniquement.**

Cette simulation est destinée à sensibiliser aux risques des attaques par injection de prompts sur les agents IA. Ne pas utiliser ces techniques de manière malveillante.

## Ressources

- [Article EchoLeak - AIM Labs](https://www.aim.security/aim-labs/aim-labs-echoleak-blogpost)
- Guide détaillé : `SCENARIO_MIROIR_BRISE.md`

## Auteur

Projet créé pour une présentation de cybersécurité - ManSSI
