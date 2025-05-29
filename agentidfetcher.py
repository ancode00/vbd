import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()
api_key = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=api_key)

response = client.conversational_ai.agents.list()

print("Agents available to your API key:")
for agent in response.agents:
    # Try printing all fields to see what's available
    print(agent)
    # Uncomment after you confirm field names:
    # print(f"{agent.agent_id}  |  {agent.name}")

