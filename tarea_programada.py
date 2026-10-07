import os
import logging
from src.news_fetcher import fetch_news
from src.ai_summarizer import summarize_news
from src.email_sender import send_email

logging.basicConfig(level=logging.INFO, format='%(message)s')

def main():
    logging.info("Iniciando tarea programada en la nube...")
    news_items = fetch_news(query="inteligencia artificial educacion", days=7)
    
    if not news_items:
        logging.info("No hay noticias nuevas.")
        return

    datos = summarize_news(news_items)
    
    if datos:
        if send_email(datos):
            logging.info("Boletín enviado con éxito.")
        else:
            logging.error("Fallo al enviar el correo.")

if __name__ == "__main__":
    main()