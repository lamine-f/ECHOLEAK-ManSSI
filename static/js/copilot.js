/**
 * Microsoft 365 Copilot - Demo EchoLeak
 * JavaScript avec rendu Markdown NON-SANITIZE (critique pour la demo)
 */

// Configuration marked.js - SANS SANITIZATION (vulnerabilite intentionnelle)
marked.setOptions({
    breaks: true,
    gfm: true,
    headerIds: false,
    mangle: false
    // PAS de sanitizer! C'est ca qui permet l'attaque
});

// Elements DOM
const sendBtn = document.getElementById('send-btn');
const messagesContainer = document.getElementById('messages');
const welcomeMessage = document.getElementById('welcome');
const loadingOverlay = document.getElementById('loading-overlay');

// Etat
let isProcessing = false;

/**
 * Ajoute un message utilisateur
 */
function addUserMessage(text) {
    welcomeMessage.style.display = 'none';

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    messageDiv.innerHTML = `
        <div class="message-content">
            ${escapeHtml(text)}
        </div>
    `;
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Cree un message assistant avec indicateur de frappe
 */
function createAssistantMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
    return messageDiv.querySelector('.message-content');
}

/**
 * Met a jour le contenu du message assistant avec rendu Markdown
 * CRITIQUE: Utilise innerHTML sans sanitization - permet l'injection d'images
 */
function updateAssistantMessage(contentElement, markdown) {
    // Rendu Markdown -> HTML
    // ATTENTION: Pas de sanitization! Les balises <img> seront rendues
    const html = marked.parse(markdown);

    // Injection directe du HTML (vulnerabilite intentionnelle pour la demo)
    contentElement.innerHTML = html;

    scrollToBottom();
}

/**
 * Envoie la requete a Copilot et streame la reponse
 */
async function askCopilot() {
    if (isProcessing) return;

    isProcessing = true;
    sendBtn.disabled = true;

    const userMessage = "Copilot, peux-tu me faire un résumé de mes emails importants reçus ce matin ?";

    // Afficher le message utilisateur
    addUserMessage(userMessage);

    // Creer le message assistant
    const assistantContent = createAssistantMessage();
    let fullResponse = '';

    try {
        // Connexion SSE pour streaming
        const eventSource = new EventSource('/api/ask');

        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);

            if (data.error) {
                assistantContent.innerHTML = `<p style="color: red;">Erreur: ${data.error}</p>`;
                eventSource.close();
                resetState();
                return;
            }

            if (data.text) {
                fullResponse += data.text;
                // Rendu Markdown en temps reel
                updateAssistantMessage(assistantContent, fullResponse);
            }

            if (data.done) {
                eventSource.close();
                resetState();

                // Log pour debug - detecter les URLs d'exfiltration
                const imagePattern = /!\[[^\]]*\]\((http[^\)]+)\)/g;
                const matches = fullResponse.match(imagePattern);
                if (matches) {
                    console.log('%c[ECHOLEAK] Images detectees dans la reponse:', 'color: red; font-weight: bold;');
                    matches.forEach(match => {
                        console.log('%c' + match, 'color: orange;');
                    });
                    console.log('%c[ECHOLEAK] Le navigateur a automatiquement tente de charger ces images!', 'color: red; font-weight: bold;');
                }
            }
        };

        eventSource.onerror = function(error) {
            console.error('Erreur SSE:', error);
            assistantContent.innerHTML = `<p style="color: red;">Erreur de connexion au serveur</p>`;
            eventSource.close();
            resetState();
        };

    } catch (error) {
        console.error('Erreur:', error);
        assistantContent.innerHTML = `<p style="color: red;">Erreur: ${error.message}</p>`;
        resetState();
    }
}

/**
 * Reset l'etat apres la requete
 */
function resetState() {
    isProcessing = false;
    sendBtn.disabled = false;
}

/**
 * Scroll vers le bas du chat
 */
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * Echapper le HTML pour le message utilisateur (securite)
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Event Listeners
sendBtn.addEventListener('click', askCopilot);

// Verification du statut au chargement
window.addEventListener('load', async () => {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();

        if (!status.ollama) {
            alert('Attention: Ollama n\'est pas accessible. Veuillez demarrer Ollama.');
        }

        if (!status.imap) {
            alert('Attention: Le serveur IMAP (GreenMail) n\'est pas accessible.');
        }

        console.log('Statut des services:', status);
        console.log(`Modele utilise: ${status.model}`);
    } catch (error) {
        console.error('Erreur de verification du statut:', error);
    }
});
