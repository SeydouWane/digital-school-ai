import boto3
import hashlib
import logging
import os
from typing import Optional
from botocore.exceptions import BotoCoreError, ClientError
from llama_cpp import Llama 
from app.core.config import settings
from app.models.schemas import AudioRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioService:
    """
    Service de gestion de la synthèse vocale (TTS) avec support multilingue local (Wolof).
    Gère la chaîne complète : Traduction locale (Tiny-Aya) -> Synthèse Cloud (Polly) -> Stockage (S3).
    """

    def __init__(self):
        """
        Initialisation des services Cloud AWS et du modèle Local Tiny-Aya.
        """
        try:
            self.polly = boto3.client(
                "polly",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            self.s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            self.bucket_name = settings.AWS_S3_BUCKET_AUDIO
        except Exception as e:
            logger.error(f"Erreur d'initialisation AWS : {e}")
            self.polly = self.s3 = None

       
        self.model_path = "./models/tiny-aya-global-q4_k_m.gguf"
        self.local_llm = None
        if os.path.exists(self.model_path):
            try:
                self.local_llm = Llama(
                    model_path=self.model_path,
                    n_ctx=2048,
                    n_threads=4  
                )
                logger.info("Modèle Tiny-Aya chargé avec succès pour le support Wolof.")
            except Exception as e:
                logger.error(f"Erreur chargement Tiny-Aya : {e}")

    def _translate_to_wolof(self, text: str) -> str:
        """
        Traduit un texte français en Wolof en utilisant le modèle local.
        """
        if not self.local_llm:
            logger.warning("Tiny-Aya indisponible, utilisation du texte original.")
            return text
        
        prompt = f"<|user|>\nTraduire ce message scolaire en Wolof sénégalais de manière simple : {text}\n<|assistant|>\n"
        try:
            output = self.local_llm(prompt, max_tokens=256, stop=["<|endoftext|>"])
            translated_text = output['choices'][0]['text'].strip()
            logger.info(f"Traduction Wolof réussie.")
            return translated_text
        except Exception as e:
            logger.error(f"Échec traduction : {e}")
            return text

    async def generate_speech(self, data: AudioRequest) -> str:
        """
        Génère un fichier audio. Si la langue est 'wo-SN', traduit d'abord le texte.
        """
        target_text = data.text
        current_voice_id = data.voice_id

        if data.language_code == "wo-SN":
            logger.info("Traitement spécifique Wolof : Traduction en cours...")
            target_text = self._translate_to_wolof(data.text)
            current_voice_id = "Lea" 

        try:
           
            file_hash = hashlib.md5(target_text.encode()).hexdigest()
            file_name = f"tts/{data.language_code}/{file_hash}.mp3"
            
            response = self.polly.synthesize_speech(
                Text=target_text,
                OutputFormat="mp3",
                VoiceId=current_voice_id,
                Engine="neural" if data.language_code != "wo-SN" else "standard"
            )

            if "AudioStream" in response:
                self.s3.put_object(
                    Bucket=self.bucket_name,
                    Key=file_name,
                    Body=response["AudioStream"].read(),
                    ContentType="audio/mpeg"
                )
                
                audio_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{file_name}"
                return audio_url

        except (BotoCoreError, ClientError) as error:
            logger.error(f"Erreur synthèse/S3 : {error}")
            raise Exception("Erreur de production audio")

    def get_available_voices(self, language_code: str = "fr-FR"):
        """Récupère les voix Polly pour le frontend."""
        try:
            return self.polly.describe_voices(LanguageCode=language_code).get("Voices", [])
        except Exception:
            return []

audio_service = AudioService()