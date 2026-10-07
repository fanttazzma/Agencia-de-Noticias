import urllib.parse
import feedparser

def fetch_news(query: str, days: int = 7) -> list:
    """
    Obtiene noticias de Google News mediante RSS sin necesidad de API Key.
    """
    encoded_query = urllib.parse.quote(f"{query} when:{days}d")
    # Configurado para español de México (es-419 / MX)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=es-419&gl=MX&ceid=MX:es-419"
    
    feed = feedparser.parse(rss_url)
    news_list = []
    
    # Tomamos un lote más grande (ej. 15) para darle margen a la IA de elegir las mejores 5
    for entry in feed.entries[:15]: 
        news_list.append({
            "title": entry.title,
            "link": entry.link,
            "published": getattr(entry, 'published', 'Fecha desconocida')
        })
        
    return news_list
