import os
import logging
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler

from src.news_fetcher import fetch_news
from src.ai_summarizer import summarize_news
from src.email_sender import send_email

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

app = FastAPI(title="Agente Observatorio IA y Educación", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def ejecutar_flujo_completo(enviar_correo: bool = True):
    """Extrae, procesa y envía el correo automáticamente."""
    logging.info("Extrayendo noticias recientes de los últimos 7 días...")
    news_items = fetch_news(query="inteligencia artificial educacion", days=7)
    
    if not news_items:
        return None

    datos = summarize_news(news_items)
    
    if enviar_correo and datos:
        send_email(datos)
        logging.info("¡Boletín automático despachado exitosamente!")
        
    return datos

# --- TEMPORIZADOR AUTOMÁTICO ---
@app.on_event("startup")
def programar_envio_automatico():
    scheduler = BackgroundScheduler(timezone="America/Mexico_City")
    # day_of_week='thu' significa jueves (Thursday)
    scheduler.add_job(
        ejecutar_flujo_completo, 
        'cron', 
        day_of_week='thu', 
        hour=7, 
        minute=0, 
        kwargs={'enviar_correo': True}
    )
    scheduler.start()
    logging.info("⏰ Temporizador activado: El correo se enviará silenciosamente cada jueves a las 7:00 AM.")

# --- ENDPOINT DEL DASHBOARD ---
@app.get("/api/noticias")
def api_obtener_noticias(background_tasks: BackgroundTasks, enviar_correo: bool = False):
    """
    Ruta para que tu dashboard consulte los datos al vuelo sin enviar correo 
    (a menos que le pasemos ?enviar_correo=true).
    """
    news_items = fetch_news(query="inteligencia artificial educacion", days=7)
    if not news_items:
        return {"status": "error"}
        
    datos = summarize_news(news_items)
    
    if enviar_correo:
        background_tasks.add_task(send_email, datos)

    return {"status": "success", "data": datos}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)