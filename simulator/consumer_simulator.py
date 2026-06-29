"""
Consumer Simulator
Uses an LLM to simulate varied consumer responses to MAVVE agent messages.
"""
import os
import random
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

PERSONAS = {
    "cooperative": "You are a cooperative rural Indian consumer. You answer questions clearly, provide necessary address details if asked, and are willing to pay via UPI if offered a discount. Keep your responses short (1-2 sentences).",
    "hesitant": "You are a hesitant consumer. You are unsure about digital payments, worry about scams, and give slightly vague answers. You need a lot of reassurance to convert to prepaid, or you might just prefer COD.",
    "hostile": "You are an angry consumer. You changed your mind about the order, you don't want it anymore, and you are annoyed that a bot is messaging you. You want to cancel.",
    "confused": "You are a confused consumer. You don't understand complex Hindi/English. You ask the bot to repeat or simplify. You are easily overwhelmed.",
}

class ConsumerSimulator:
    def __init__(self, persona="random", language="hi"):
        if persona == "random":
            self.persona = random.choice(list(PERSONAS.keys()))
        else:
            self.persona = persona
            
        self.language = language
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
        self.chat_history = []
        
        system_prompt = f"""
        {PERSONAS.get(self.persona, PERSONAS['cooperative'])}
        Respond in this language code: {self.language} (using native script).
        You are replying on WhatsApp. Be realistic to Indian e-commerce buyers.
        """
        self.chat_history.append(SystemMessage(content=system_prompt))

    def generate_response(self, agent_message: str) -> str:
        """Generates a response to the agent's message based on the persona."""
        
        # Handle 'unavailable' persona specially
        if self.persona == "unavailable":
            return "" # Simulate no response
            
        self.chat_history.append(HumanMessage(content=f"Agent says: {agent_message}"))
        
        response = self.llm.invoke(self.chat_history)
        reply = response.content.strip()
        
        self.chat_history.append(SystemMessage(content=f"You replied: {reply}"))
        return reply

if __name__ == "__main__":
    # Quick test
    sim = ConsumerSimulator(persona="cooperative", language="hi")
    reply = sim.generate_response("Hello! We noticed your address is missing a landmark. Can you tell us what is near your house?")
    print(f"Cooperative Reply: {reply}")
