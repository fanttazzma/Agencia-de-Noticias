import urllib.parse
import logging
import feedparser

# Palabras prohibidas para el primer filtro anti-tutoriales
PALABRAS_PROHIBIDAS = [
    "tutorial", "paso a paso", "cómo usar", "como usar", 
    "prompts para", "mejores prompts", "curso gratis", 
    "guía para", "guia para", "trucos para", "aprende a usar"
]

def es_noticia_valida(titulo: str, enlace: str) -> bool:
    """
    Primera verificación: 
    1. Revisa que tenga título y un enlace HTTP válido.
    2. Filtra tutoriales, guías o listas de prompts desde el título.
    """
    if not titulo or not enlace or not enlace.startswith("http"):
        return False
        
    titulo_lower = titulo.lower()
    for palabra in PALABRAS_PROHIBIDAS:
        if palabra in titulo_lower:
            logging.info(f"🚫 Descartada por filtro anti-tutorial: {titulo}")
            return False
            
    return True

def fetch_news(query: str = None, days: int = 7, max_por_categoria: int = 6):
    """
    Realiza 3 búsquedas especializadas en Google News (configurado para México)
    para nutrir las 3 ligas del carrusel (18-30 años).
    """
    # Definimos las 3 búsquedas específicas para el carrusel
    busquedas = {
        "1_Innovador_Nacional": (
            '"inteligencia artificial" (México OR mexicano OR Chiapas OR UNAM OR IPN OR Tec OR jóvenes) '
            '(innovación OR desarrollo OR creación OR tecnología) -tutorial -curso'
        ),
        "2_IA_Educacion_Jovenes": (
            '"inteligencia artificial" (universidad OR universitarios OR estudiantes OR "educación superior" OR alumnos) '
            'México -tutorial -prompts'
        ),
        "3_IA_Internacional_Educacion": (
            '"inteligencia artificial" (universidades OR educación OR investigación OR estudiantes) '
            '(mundo OR internacional OR UNESCO OR Europa OR EUA OR Asia) -tutorial -curso'
        )
    }

    noticias_recolectadas = []
    enlaces_vistos = set()

    for categoria, consulta in busquedas.items():
        consulta_codificada = urllib.parse.quote(f"{consulta} when:{days}d")
        # gl=MX y ceid=MX:es-419 priorizan resultados para México en español
        rss_url = f"https://news.google.com/rss/search?q={consulta_codificada}&hl=es-419&gl=MX&ceid=MX:es-419"
        
        logging.info(f"🔎 Buscando categoría [{categoria}]...")
        feed = feedparser.parse(rss_url)
        
        contador = 0
        for entry in feed.entries:
            if contador >= max_por_categoria:
                break
                
            titulo = entry.get("title", "")
            enlace = entry.get("link", "")
            
            # Evitar noticias duplicadas entre las 3 búsquedas
            if enlace in enlaces_vistos:
                continue
                
            # Verificación 1 (En código): Validar enlace y descartar tutoriales
            if not es_noticia_valida(titulo, enlace):
                continue

            fuente = "Medio verificado"
            if "source" in entry and "title" in entry.source:
                fuente = entry.source.title

            noticias_recolectadas.append({
                "title": f"[{categoria}] {titulo}",
                "link": enlace,
                "published": entry.get("published", ""),
                "source": fuente,
                "summary": entry.get("summary", "")
            })
            
            enlaces_vistos.add(enlace)
            contador += 1

    logging.info(f"✅ Total de noticias pre-verificadas enviadas a Gemini: {len(noticias_recolectadas)}")
    return noticias_recolectadas
