import logging
from dotenv import load_dotenv
from src.news_fetcher import fetch_news
from src.ai_summarizer import summarize_news
from src.email_sender import send_email

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

def main():
    logging.info("🚀 Iniciando agente de noticias (Top 3 Carrusel)...")
    news_items = fetch_news(days=7)
    
    if not news_items:
        logging.warning("No se encontraron noticias nuevas.")
        return

    datos = summarize_news(news_items)
    
    if datos:
        if send_email(datos):
            logging.info("✅ Boletín enviado con éxito al correo.")
        else:
            logging.error("❌ Fallo al enviar el correo.")
    else:
        logging.error("❌ Gemini no devolvió datos válidos.")

if __name__ == "__main__":
    main()
