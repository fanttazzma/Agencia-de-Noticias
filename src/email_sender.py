import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

def send_email(json_data: dict) -> bool:
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    receiver = os.getenv("EMAIL_RECEIVER")
    
    # Cargar y renderizar la plantilla HTML
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template_boletin.html')
    html_content = template.render(data=json_data)
    
    msg = EmailMessage()
    msg['Subject'] = f"Observatorio IA y Educación ({datetime.now().strftime('%d/%m/%Y')})"
    msg['From'] = sender
    msg['To'] = receiver
    msg.add_alternative(html_content, subtype='html')
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender, password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"Error SMTP: {e}")
        return False