import os
import json
import google.generativeai as genai

def summarize_news(news_list: list) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    
    news_text = "\n".join([f"- Título: {n['title']}\n  Enlace: {n['link']}" for n in news_list])
    
    prompt = f"""
    Eres un curador experto en IA y Educación. Analiza estas noticias y elige las 5 más importantes.
    Devuelve ÚNICAMENTE un objeto JSON válido, sin bloques de código Markdown (```json), con esta estructura exacta:
    {{
      "intro": "Un párrafo introductorio resumiendo la tendencia de la semana.",
      "news": [
        {{
          "t": "Título de la noticia",
          "s": "Nombre del medio o fuente",
          "u": "El enlace proporcionado",
          "desc": "Resumen de un párrafo",
          "why": "Por qué importa esta noticia",
          "cat": "Categoría (ej. Política pública, Investigación, Formación docente, Herramientas, Integridad)",
          "r": ["dir", "doc"] // Asigna 1 a 3 roles aplicables usando estas claves estrictas: dir (directivos), coord (coordinadores), doc (docentes), inv (investigadores)
        }}
      ]
    }}
    Noticias disponibles:
    {news_text}
    """
    
    # Usamos el modelo que ya te funcionó
    model = genai.GenerativeModel('models/gemini-flash-latest')
    response = model.generate_content(prompt)
    
    # Limpiar el texto devuelto y convertirlo a diccionario de Python
    raw_text = response.text.strip()
    if raw_text.startswith("```json"): raw_text = raw_text[7:]
    if raw_text.startswith("```"): raw_text = raw_text[3:]
    if raw_text.endswith("```"): raw_text = raw_text[:-3]
    
    return json.loads(raw_text)