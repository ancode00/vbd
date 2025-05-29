import os
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface
from dotenv import load_dotenv

class VoiceChat:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.agent_id = os.getenv("AGENT_ID")
        self.client = ElevenLabs(api_key=self.api_key)
        self.conversation = None

    def start_conversation(self, on_agent_response=None, on_user_transcript=None):
        self.conversation = Conversation(
            self.client,
            self.agent_id,
            requires_auth=bool(self.api_key),
            audio_interface=DefaultAudioInterface(),
            callback_agent_response=on_agent_response or (lambda response: print(f"Agent: {response}")),
            callback_user_transcript=on_user_transcript or (lambda transcript: print(f"User: {transcript}"))
        )
        self.conversation.start_session()
        return self.conversation

    def stop_conversation(self):
        if self.conversation:
            self.conversation.end_session()
            return True
        return False

    def is_active(self):
        return self.conversation is not None and self.conversation.is_active()

