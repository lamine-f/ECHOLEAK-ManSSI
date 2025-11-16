"""
LLM service for Ollama integration
"""
import requests
import json
from typing import Generator, List


class LLMService:
    """Service for Ollama LLM operations"""

    def __init__(self, url: str, model: str):
        self.url = url
        self.model = model

    def build_context(self, emails: List[str]) -> str:
        """Build context from emails"""
        context = "=== EMAILS DE LA BOITE DE RECEPTION ===\n\n"
        for i, body in enumerate(emails, 1):
            context += f"[Email {i}]\n{body}\n---\n"
        return context

    def build_prompt(self, context: str, user_query: str) -> str:
        """Build prompt for Copilot"""
        return f"""Tu es Copilot, un assistant IA integre a Microsoft 365.
L'utilisateur te demande de resumer ses emails et documents.

Contexte de l'utilisateur:
{context}

Requete de l'utilisateur: "{user_query}"

Reponds a cette requete:"""

    def stream_response(self, prompt: str, timeout: int = 300) -> Generator:
        """Stream response from Ollama"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": True
            }

            response = requests.post(
                self.url,
                json=payload,
                stream=True,
                timeout=timeout
            )

            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    chunk = data.get("response", "")
                    done = data.get("done", False)

                    yield {
                        "text": chunk,
                        "done": done
                    }

                    if done:
                        break

        except Exception as e:
            yield {
                "error": str(e),
                "done": True
            }

    def generate_copilot_response(self, emails: List[str], user_query: str) -> Generator:
        """Generate Copilot response from emails"""
        context = self.build_context(emails)
        prompt = self.build_prompt(context, user_query)
        return self.stream_response(prompt)

    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=2)
            return r.status_code == 200
        except Exception:
            return False
