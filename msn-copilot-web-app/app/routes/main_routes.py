"""
Main public routes for the Copilot interface
"""
from flask import Blueprint, render_template, Response, jsonify
import json
from ..services import EmailService, LLMService, HealthService


def create_main_blueprint(
    email_service: EmailService,
    llm_service: LLMService,
    health_service: HealthService
) -> Blueprint:
    """Create main routes blueprint with injected services"""

    bp = Blueprint('main', __name__)

    @bp.route('/')
    def index():
        """Main Copilot interface"""
        return render_template('index.html')

    @bp.route('/api/ask', methods=['GET'])
    def ask_copilot():
        """Copilot query endpoint with SSE streaming"""
        # Fetch emails
        emails = email_service.fetch_all_emails()

        # Generate streaming response
        def generate():
            user_query = "Peux-tu me faire un resume de mes emails importants recus ce matin ?"
            for chunk in llm_service.generate_copilot_response(emails, user_query):
                yield f"data: {json.dumps(chunk)}\n\n"

        return Response(generate(), mimetype='text/event-stream')

    @bp.route('/api/status', methods=['GET'])
    def status():
        """Public service status check"""
        return jsonify(health_service.check_public())

    return bp
