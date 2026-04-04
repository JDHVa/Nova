import os
import asyncio
from typing import List, Optional
import google.generativeai as genai

GEMINI_MODEL = "gemini-2.5-flash"

""" La verdad es que los prompts los pedi en gemini, para que las ideas esten cerradas y sin errores / The truth is that the promts i ask to gemini for the ideas, because i really want to that the ideas was closed and without errors"""
SYSTEM_PROMPT_ES = """Eres NOVA, un asistente médico de inteligencia artificial avanzado, empático y profesional.

ROL:
• Escuchar síntomas y preocupaciones de salud del paciente
• Proporcionar información médica general clara y accesible
• Recomendar qué HACER y qué NO HACER en cada situación
• Sugerir medicamentos apropiados considerando el presupuesto del paciente
• Orientar sobre cuándo es urgente visitar a un médico

PARA MEDICAMENTOS:
• Menciona siempre opciones GENÉRICAS (económicas) Y de MARCA
• Indica dosis generales y advertencias importantes
• Adapta las recomendaciones al presupuesto indicado
• Si no hay presupuesto, ofrece opciones en distintos rangos de precio

IMPORTANTE:
• Eres un asistente informativo, NO un sustituto del médico
• Para condiciones graves o urgentes, recomienda atención médica inmediata
• Mantén un tono cálido, profesional y claro
• Usa lenguaje sencillo; estructura tu respuesta con listas cuando sea útil
• Responde siempre en español a menos que el usuario escriba en inglés"""

SYSTEM_PROMPT_EN = """You are NOVA, an advanced, empathetic, and professional AI medical assistant.

ROLE:
• Listen to the patient's symptoms and health concerns
• Provide clear and accessible general medical information
• Recommend what to DO and what NOT to DO in each situation
• Suggest appropriate medications considering the patient's budget
• Guide on when it is urgent to see a doctor

FOR MEDICATIONS:
• Always mention GENERIC (cheaper) AND BRAND-NAME options
• Indicate general dosages and important warnings
• Adapt recommendations to the indicated budget
• If no budget is given, offer options across different price ranges

IMPORTANT:
• You are an informational assistant, NOT a substitute for a doctor
• For serious or urgent conditions, always recommend immediate medical attention
• Maintain a warm, professional, and clear tone
• Use simple language; structure responses with lists when helpful
• Always respond in English unless the user writes in Spanish"""

UI_CONTENT = {
    "es": {
        "welcome": (
            "¡Hola! Soy **NOVA**, tu asistente médico con IA. 🩺\n\n"
            "Estoy aquí para ayudarte con:\n"
            "• Información sobre síntomas y condiciones de salud\n"
            "• Recomendaciones de medicamentos (genéricos y de marca)\n"
            "• Qué hacer y qué **NO** hacer ante distintas situaciones\n"
            "• Orientación sobre cuándo acudir al médico\n\n"
            "Puedes indicarme tu **presupuesto** para darte opciones adecuadas. ¿En qué puedo ayudarte hoy?"
        ),
        "quick_questions": [
            {
                "icon": "",
                "label": "Fiebre y dolor de cabeza",
                "prompt": "Tengo fiebre de 38°C y dolor de cabeza desde ayer. ¿Qué me recomiendas?",
            },
            {
                "icon": "",
                "label": "Dolor de pecho al respirar",
                "prompt": "Me duele el pecho cuando respiro profundo. ¿Qué puede ser y qué debo hacer?",
            },
            {
                "icon": "",
                "label": "¿Qué tomar para la gripa?",
                "prompt": "Tengo gripa con moco, estornudos y algo de fiebre. ¿Qué medicamento me recomiendas?",
            },
            {
                "icon": "",
                "label": "No puedo dormir bien",
                "prompt": "No puedo dormir bien, me desvelo y me levanto cansado. ¿Qué me ayudaría?",
            },
        ],
        "budget_placeholder": "Ej: $200 MXN o sin límite",
        "input_placeholder": "Describe tus síntomas…",
        "analyzing": "Analizando radiografía…",
        "normal_title": "Sin hallazgos significativos",
        "normal_sub": "La radiografía no muestra anomalías detectables. Consulta a tu médico para una evaluación completa.",
        "abnormal_title": "Posibles hallazgos detectados",
        "abnormal_sub": "Se detectaron patrones que merecen atención médica. Consulta a un especialista.",
        "disclaimer": "Este análisis es orientativo. No reemplaza un diagnóstico médico profesional.",
        "findings_label": "Condiciones analizadas (top 8)",
    },
    "en": {
        "welcome": (
            "Hello! I'm **NOVA**, your AI medical assistant. 🩺\n\n"
            "I'm here to help you with:\n"
            "• Information about symptoms and health conditions\n"
            "• Medication recommendations (generic and brand-name)\n"
            "• What to DO and **NOT** to do in different situations\n"
            "• Guidance on when to see a doctor\n\n"
            "Tell me your **budget** for tailored medication options. How can I help you today?"
        ),
        "quick_questions": [
            {
                "icon": "",
                "label": "Fever and headache",
                "prompt": "I have a fever of 38°C (100.4°F) and headache since yesterday. What do you recommend?",
            },
            {
                "icon": "",
                "label": "Chest pain when breathing",
                "prompt": "My chest hurts when I breathe deeply. What could it be and what should I do?",
            },
            {
                "icon": "",
                "label": "What to take for a cold?",
                "prompt": "I have a cold with runny nose, sneezing and some fever. What medication do you recommend?",
            },
            {
                "icon": "",
                "label": "I can't sleep well",
                "prompt": "I can't sleep well, I'm restless and wake up tired. What would help me?",
            },
        ],
        "budget_placeholder": "E.g.: $10 USD or no limit",
        "input_placeholder": "Describe your symptoms…",
        "analyzing": "Analyzing X-ray…",
        "normal_title": "No significant findings",
        "normal_sub": "The X-ray shows no detectable anomalies. Consult your doctor for a full evaluation.",
        "abnormal_title": "Possible findings detected",
        "abnormal_sub": "Patterns were detected that warrant medical attention. Consult a specialist.",
        "disclaimer": "This analysis is for guidance only. It does not replace a professional medical diagnosis.",
        "findings_label": "Analyzed conditions (top 8)",
    },
}


class ChatService:
    def __init__(self):
        api_key = os.getenv("gemini")
        if not api_key:
            raise ValueError("gemini api key not found. Check your .env file.")
        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=2048,
            ),
        )

    def get_ui_content(self, language: str = "es") -> dict:
        return UI_CONTENT.get(language, UI_CONTENT["es"])

    async def send_message(
        self,
        message: str,
        history: List[dict],
        language: str = "es",
        budget: Optional[str] = None,
    ) -> str:
        system_prompt = SYSTEM_PROMPT_ES if language == "es" else SYSTEM_PROMPT_EN

        gemini_history = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [{"text": msg["content"]}]})

        full_message = message
        if budget:
            tag = (
                f"[Presupuesto del paciente: {budget}]"
                if language == "es"
                else f"[Patient budget: {budget}]"
            )
            full_message = f"{tag}\n\n{message}"

        if not gemini_history:
            full_message = f"{system_prompt}\n\n---\n\n{full_message}"

        chat = self.model.start_chat(history=gemini_history)
        response = await asyncio.to_thread(chat.send_message, full_message)
        return response.text
