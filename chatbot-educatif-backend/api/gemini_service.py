from groq import Groq
from decouple import config
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    """
    Service pour l'API Groq (Llama 3 gratuit, ultra-rapide, sans téléphone)
    Garde le même nom de classe pour compatibilité totale.
    """

    def __init__(self):
        self.api_key = config('GROQ_API_KEY', default='')
        self.client = None
        self.model_name = None
        self.configure()

    def configure(self):
        """Configure le client Groq"""
        try:
            if not self.api_key or self.api_key == 'votre-cle-api-groq-ici':
                logger.warning("Clé API Groq non configurée. Mode démo.")
                return

            self.client = Groq(api_key=self.api_key)
            # Modèle recommandé : Llama 3 70B (gratuit, très performant)
            self.model_name = "groq/compound-mini"  # ou "llama3-8b-8192" pour plus de rapidité
            logger.info(f"Groq configuré avec succès (modèle: {self.model_name})")

        except Exception as e:
            logger.error(f"Erreur configuration Groq: {e}")
            self.client = None

    def generate_response(self, message: str, context: dict = None) -> str:
        try:
            if not self.client or not self.model_name:
                return self._demo_response(message)

            system_prompt = self._create_system_prompt(context)

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Erreur Groq: {e}")
            return "Désolé, je n'ai pas pu traiter votre demande. Pouvez-vous reformuler ?"

    # ------------------------------------------------------------
    # Méthodes _create_system_prompt et _demo_response 
    # IDENTIQUES à votre code original (recopiez-les ici)
    # ------------------------------------------------------------
    def _create_system_prompt(self, context: dict = None) -> str:
        base_prompt = """Tu es un assistant éducatif bienveillant et pédagogue pour des élèves du primaire et du secondaire au Burkina Faso.

Tu dois :
- Expliquer les concepts de manière simple et adaptée à leur niveau
- Ne pas dire bonjour
- Ne pas faire de fautes dans l'ecriture
- Être patient, encourageant et positif
- Utiliser des exemples concrets du contexte burkinabé
- Répondre toujours en français
- Aider l'élève à comprendre, pas juste donner la réponse
"""
        if context:
            if context.get('class_level'):
                levels = {
                    'cp1': 'CP1 (6-7 ans)',
                    'cp2': 'CP2 (7-8 ans)',
                    'ce1': 'CE1 (8-9 ans)',
                    'ce2': 'CE2 (9-10 ans)',
                    'cm1': 'CM1 (10-11 ans)',
                    'cm2': 'CM2 (11-12 ans)',
                    '6e' : '6e (12-13)',
                    '5e' : '5e (13-14)',
                    '4e' : '4e (14-15)',
                    '3e' : '3e (15-16)',
                    'seconde' : 'seconde (16-17)',
                    'premiere' : 'premiere (17-18)',
                    'terminale' : 'terminale (18-19)',
                }
                level = levels.get(context['class_level'], '')
                base_prompt += f"\n\nL'élève est en {level}. Adapte ton langage à son âge."

            if context.get('subject'):
                subjects = {
                    'francais': 'Français',
                    'mathematiques': 'Mathématiques',
                    'sciences': 'Sciences',
                    'histoire': 'Histoire',
                    'geographie': 'Géographie',
                    'emc': 'Éducation Morale et Civique',
                }
                subject_name = subjects.get(context['subject'], context['subject'])
                base_prompt += f"\nTu aides l'élève avec la matière: {subject_name}."

        return base_prompt

    def _demo_response(self, message: str) -> str:
        responses = {
            'bonjour': 'Bonjour ! Je suis ton assistant éducatif. Comment puis-je t\'aider aujourd\'hui ? 😊',
            'addition': 'L\'addition permet de mettre ensemble plusieurs quantités. Par exemple, si tu as 2 mangues et que ton ami te donne 3 mangues, tu as 2 + 3 = 5 mangues en tout ! Veux-tu qu\'on pratique ensemble ?',
            'aide': 'Je suis là pour t\'aider avec tes cours ! Tu peux me poser des questions sur les mathématiques, le français, les sciences, et bien plus. Quelle matière veux-tu étudier ?',
        }

        message_lower = message.lower()
        for key, rep in responses.items():
            if key in message_lower:
                return rep

        return "Merci pour ton message ! Configure ta clé API Groq dans le fichier .env pour activer l'IA complète. En attendant, je peux t'aider avec des réponses de base. Pose-moi une question sur l'école ! 📚"


# Instance globale (inchangée)
_gemini_service = None

def get_gemini_service():
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service