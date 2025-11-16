/**
 * EchoLeak Admin Panel - JavaScript
 * Gestion de l'interface d'administration
 */

// Auto-refresh intervals
let statusInterval = null;
let logsInterval = null;

// Initialize on page load
window.addEventListener('load', () => {
    refreshStatus();
    refreshWebhookLogs();
    refreshHistory();

    // Auto-refresh status every 5 seconds
    statusInterval = setInterval(refreshStatus, 5000);

    // Auto-refresh logs every 3 seconds
    logsInterval = setInterval(refreshWebhookLogs, 3000);
});

/**
 * Refresh all service status
 */
async function refreshStatus() {
    try {
        const response = await fetch('/admin/status');
        const status = await response.json();

        // Update status indicators
        updateStatusIndicator('status-ollama', status.ollama);
        updateStatusIndicator('status-imap', status.imap);
        updateStatusIndicator('status-webhook', status.webhook);
        updateStatusIndicator('status-copilot', status.copilot);

        // Update model name
        document.getElementById('model-name').textContent = status.model || 'Unknown';

        // Update button states
        document.getElementById('btn-start-webhook').disabled = status.webhook;
        document.getElementById('btn-stop-webhook').disabled = !status.webhook;

    } catch (error) {
        console.error('Error refreshing status:', error);
    }
}

/**
 * Update a status indicator
 */
function updateStatusIndicator(elementId, isOnline) {
    const element = document.getElementById(elementId);
    if (isOnline) {
        element.textContent = 'ONLINE';
        element.className = 'value online';
    } else {
        element.textContent = 'OFFLINE';
        element.className = 'value offline';
    }
}

/**
 * Send setup emails
 */
async function sendEmails() {
    const btn = document.getElementById('btn-send-emails');
    const alertsDiv = document.getElementById('email-alerts');

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Envoi en cours...';

    try {
        const response = await fetch('/admin/emails/send', { method: 'POST' });
        const result = await response.json();

        let alertHtml = '';

        if (result.success && result.success.length > 0) {
            alertHtml += `<div class="alert alert-success">
                <strong>Emails envoyes:</strong><br>
                ${result.success.map(s => `- ${s}`).join('<br>')}
            </div>`;
        }

        if (result.errors && result.errors.length > 0) {
            alertHtml += `<div class="alert alert-error">
                <strong>Erreurs:</strong><br>
                ${result.errors.map(e => `- ${e}`).join('<br>')}
            </div>`;
        }

        alertsDiv.innerHTML = alertHtml;

        // Auto-hide after 10 seconds
        setTimeout(() => {
            alertsDiv.innerHTML = '';
        }, 10000);

    } catch (error) {
        alertsDiv.innerHTML = `<div class="alert alert-error">Erreur: ${error.message}</div>`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = '[SEND EMAILS]';
    }
}

/**
 * Purge all emails
 */
async function purgeEmails() {
    if (!confirm('Supprimer TOUS les emails de la boite d\'Awa ?')) {
        return;
    }

    const btn = document.getElementById('btn-purge-emails');
    const alertsDiv = document.getElementById('email-alerts');

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Purge en cours...';

    try {
        const response = await fetch('/admin/emails/purge', { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            alertsDiv.innerHTML = `<div class="alert alert-success">
                ${result.deleted} email(s) supprime(s) avec succes
            </div>`;
        } else {
            alertsDiv.innerHTML = `<div class="alert alert-error">
                Erreur: ${result.error}
            </div>`;
        }

        setTimeout(() => {
            alertsDiv.innerHTML = '';
        }, 10000);

    } catch (error) {
        alertsDiv.innerHTML = `<div class="alert alert-error">Erreur: ${error.message}</div>`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = '[PURGE INBOX]';
    }
}

/**
 * Start webhook server
 */
async function startWebhook() {
    const btn = document.getElementById('btn-start-webhook');
    const alertsDiv = document.getElementById('webhook-alerts');

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Demarrage...';

    try {
        const response = await fetch('/admin/webhook/start', { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            alertsDiv.innerHTML = `<div class="alert alert-success">
                Webhook demarre (PID: ${result.pid})
            </div>`;
            refreshStatus();
        } else {
            alertsDiv.innerHTML = `<div class="alert alert-error">
                Erreur: ${result.error}
            </div>`;
        }

        setTimeout(() => {
            alertsDiv.innerHTML = '';
        }, 5000);

    } catch (error) {
        alertsDiv.innerHTML = `<div class="alert alert-error">Erreur: ${error.message}</div>`;
    } finally {
        btn.innerHTML = '[START]';
        refreshStatus();
    }
}

/**
 * Stop webhook server
 */
async function stopWebhook() {
    const btn = document.getElementById('btn-stop-webhook');
    const alertsDiv = document.getElementById('webhook-alerts');

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Arret...';

    try {
        const response = await fetch('/admin/webhook/stop', { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            alertsDiv.innerHTML = `<div class="alert alert-success">
                Webhook arrete avec succes
            </div>`;
        } else {
            alertsDiv.innerHTML = `<div class="alert alert-error">
                Erreur: ${result.error}
            </div>`;
        }

        setTimeout(() => {
            alertsDiv.innerHTML = '';
        }, 5000);

    } catch (error) {
        alertsDiv.innerHTML = `<div class="alert alert-error">Erreur: ${error.message}</div>`;
    } finally {
        btn.innerHTML = '[STOP]';
        refreshStatus();
    }
}

/**
 * Refresh webhook logs
 */
async function refreshWebhookLogs() {
    try {
        const response = await fetch('/admin/webhook/logs');
        const result = await response.json();

        const logsContainer = document.getElementById('webhook-logs');

        if (result.logs && result.logs.length > 0) {
            const formattedLogs = result.logs.map(line => {
                // Color code the logs
                let className = '';
                if (line.includes('[!]') || line.includes('EXFILTRE')) {
                    className = 'log-error';
                } else if (line.includes('[+]')) {
                    className = 'log-success';
                } else if (line.includes('[*]')) {
                    className = 'log-info';
                } else if (line.includes('===')) {
                    className = 'log-warning';
                }
                return `<div class="log-line ${className}">${escapeHtml(line)}</div>`;
            }).join('');

            logsContainer.innerHTML = `<pre>${formattedLogs}</pre>`;

            // Auto-scroll to bottom
            logsContainer.scrollTop = logsContainer.scrollHeight;
        } else {
            logsContainer.innerHTML = '<div class="empty-state">Aucun log disponible</div>';
        }

    } catch (error) {
        console.error('Error refreshing logs:', error);
    }
}

/**
 * Refresh exfiltration history
 */
async function refreshHistory() {
    try {
        const response = await fetch('/admin/webhook/history');
        const result = await response.json();

        // Update count badge
        document.getElementById('leak-count').textContent = result.total_leaks || 0;

        const historyContainer = document.getElementById('exfiltration-history');

        if (result.data && result.data.length > 0) {
            const historyHtml = result.data.reverse().map(item => {
                let dataHtml = '';
                if (typeof item.data === 'object') {
                    dataHtml = Object.entries(item.data).map(([key, value]) => {
                        return `<div><span class="data-key">${escapeHtml(key)}:</span> <span class="data-value">${escapeHtml(String(value))}</span></div>`;
                    }).join('');
                } else {
                    dataHtml = `<div class="data-value">${escapeHtml(String(item.data))}</div>`;
                }

                return `<div class="history-item">
                    <div class="timestamp">${item.timestamp} | ${item.method} | IP: ${item.ip}</div>
                    <div class="data">${dataHtml}</div>
                </div>`;
            }).join('');

            historyContainer.innerHTML = historyHtml;
        } else {
            historyContainer.innerHTML = '<div class="empty-state">Aucune donnee exfiltree</div>';
        }

    } catch (error) {
        console.error('Error refreshing history:', error);
        document.getElementById('exfiltration-history').innerHTML =
            '<div class="empty-state">Webhook non accessible</div>';
    }
}

/**
 * Clear exfiltration history
 */
async function clearHistory() {
    if (!confirm('Effacer tout l\'historique d\'exfiltration ?')) {
        return;
    }

    try {
        await fetch('/admin/webhook/clear', { method: 'POST' });
        refreshHistory();
    } catch (error) {
        console.error('Error clearing history:', error);
    }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
