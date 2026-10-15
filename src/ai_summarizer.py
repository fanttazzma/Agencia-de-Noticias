import os
import json
import logging
import google.generativeai as genai

def summarize_news(news_items):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.error("No se encontró GEMINI_API_KEY en las variables de entorno.")
        return None

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # Convertimos las noticias extraídas a texto para que la IA las evalúe
    noticias_texto = ""
    for i, item in enumerate(news_items, 1):
        noticias_texto += (
            f"ID: {i}\n"
            f"Título: {item.get('title')}\n"
            f"Fuente: {item.get('source', 'Desconocida')}\n"
            f"Fecha: {item.get('published', '')}\n"
            f"Enlace: {item.get('link')}\n"
            f"Resumen previo: {item.get('summary', '')}\n---\n"
        )

    prompt = f"""
    Eres un editor experto en comunicación digital universitaria y curador de tecnología.
    Tu público objetivo son jóvenes universitarios de 18 a 30 años en México. 
    Usa un tono dinámico, claro, atractivo para estudiantes y directo al grano.

    A partir de la siguiente lista de noticias, debes seleccionar y priorizar EXACTAMENTE 3 NOTICIAS para armar un carrusel informativo, cumpliendo estrictamente estas reglas:

    1. ESTRUCTURA DEL CARRUSEL (3 LIGAS ORDENADAS POR PRIORIDAD):
       - Noticia 1 (Tema: Innovador | Enfoque Nacional/Local): Una noticia sobre un avance o uso innovador de la IA, dando máxima prioridad a lo que ocurre en México o América Latina y que despierte el interés de los alumnos.
       - Noticia 2 (Tema: IA con la educación | Enfoque Jóvenes 18-30 años): Cómo la IA está cambiando la forma de estudiar, investigar o prepararse profesionalmente en la universidad (preferentemente en México).
       - Noticia 3 (Tema: IA internacional educación): Una noticia relevante a nivel global sobre regulaciones, descubrimientos o adopciones de IA en universidades del mundo.

    2. FILTRO ESTRICTO ANTI-TUTORIALES (PROHIBIDO):
       - Descarta inmediatamente cualquier nota que sea un tutorial, guía paso a paso, lista de prompts ("10 prompts para...", "Cómo usar ChatGPT para..."), cursos promocionales o artículos de opinión sin sustento noticioso. Solo selecciona hechos, lanzamientos, estudios o noticias reales.

    3. DOBLE VERIFICACIÓN (FACT-CHECKING):
       - Verificación 1 (Fuente y Enlace): Asegúrate de que el enlace ('u') pertenezca exactamente a la noticia seleccionada, provenga de un medio legítimo y no esté vacío ni alterado.
       - Verificación 2 (Congruencia y No-Clickbait): Verifica que el título y el resumen hablen de un hecho real y comprobable, descartando rumores o títulos engañosos.

    4. RECOMENDACIÓN PARA REDES SOCIALES:
       - Evalúa las 3 noticias finales y elige LA MEJOR para replicar en redes sociales (Instagram/TikTok) para jóvenes de 18 a 30 años.
       - En el campo "intro", redacta primero un saludo breve (2 líneas) presentando el carrusel de la semana y, justo debajo, agrega la sección: "📱 RECOMENDACIÓN PARA REDES: Te sugerimos replicar la Noticia #[Número] porque [explicación breve de su potencial viral/interés estudiantil]. Idea de gancho para el post: '[Propuesta de frase corta para la portada del carrusel]'."

    Devuelve ÚNICAMENTE un objeto JSON válido (sin bloques de código markdown ```json) con esta estructura exacta:
    {{
      "intro": "Saludo juvenil breve + 📱 RECOMENDACIÓN PARA REDES...",
      "news": [
        {{
          "t": "Título atractivo de la noticia 1 (Innovador / México)",
          "s": "Nombre del medio · Fecha corta (ej. 15 oct 2026) · [Prioridad Alta]",
          "u": "URL exacta y verificada de la noticia original",
          "desc": "Resumen dinámico de 2 a 3 líneas enfocado en qué pasó y cómo impacta a los jóvenes universitarios.",
          "why": "Por qué le importa a un alumno de 18-30 años + Motivo de prioridad.",
          "cat": "Innovador (Nacional)",
          "r": ["est", "doc"]
        }},
        {{
          "t": "Título de la noticia 2 (IA con la educación)",
          "s": "Nombre del medio · Fecha corta · [Prioridad Media]",
          "u": "URL exacta y verificada",
          "desc": "Resumen dinámico...",
          "why": "Por qué importa...",
          "cat": "IA en Educación",
          "r": ["est", "doc"]
        }},
        {{
          "t": "Título de la noticia 3 (IA internacional educación)",
          "s": "Nombre del medio · Fecha corta · [Prioridad Global]",
          "u": "URL exacta y verificada",
          "desc": "Resumen dinámico...",
          "why": "Por qué importa...",
          "cat": "IA Internacional",
          "r": ["est", "inv"]
        }}
      ]
    }}
    Nota para el campo "r" (roles): usa combinaciones de ["est", "doc", "inv", "coord", "dir"], priorizando "est" (Estudiantes).

    LISTA DE NOTICIAS A EVALUAR:
    {noticias_texto}
    """

    try:
        response = model.generate_content(prompt)
        texto_limpio = response.text.strip()
        
        # Limpiar posibles etiquetas markdown si el modelo las incluye
        if texto_limpio.startswith("```json"):
            texto_limpio = texto_limpio[7:]
        if texto_limpio.startswith("```"):
            texto_limpio = texto_limpio[3:]
        if texto_limpio.endswith("```"):
            texto_limpio = texto_limpio[:-3]

        datos_json = json.loads(texto_limpio.strip())
        return datos_json

    except Exception as e:
        logging.error(f"Error al procesar el JSON con Gemini: {e}")
        return None
