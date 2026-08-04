import os
import re
import subprocess
import requests
from bs4 import BeautifulSoup

# URLs de los Webhooks en Railway
URL_BOT_RAILWAY = os.getenv("URL_BOT_RAILWAY")
URL_BOT_RAILWAY_SECUNDARIO = os.getenv("URL_BOT_RAILWAY_SECUNDARIO")

CLAVE_SECRETA_BCV = os.getenv("CLAVE_SECRETA_BCV")

def obtener_tasa_bcv_bypass():
    target_url = "https://www.bcv.org.ve"

    try:
        print("🔍 Consultando la web del BCV directamente vía curl (insecure)...")

        # Ejecutamos curl con -k (insecure) y User-Agent de navegador para saltar SSL y bloqueos
        comando = [
            "curl", "-s", "-k",
            "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            target_url
        ]

        resultado = subprocess.run(comando, capture_output=True, text=True, timeout=30)
        html_content = resultado.stdout

        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            div_dolar = soup.find("div", id="dolar")

            if div_dolar:
                strong_tag = div_dolar.find("strong")
                texto_tasa = strong_tag.text.strip() if strong_tag else div_dolar.text.strip()

                texto_limpio = texto_tasa.replace(',', '.')
                match = re.search(r'\d+\.\d+', texto_limpio)

                if match:
                    tasa = float(match.group(0))

                    span_fecha = soup.find("span", class_="date-display-single")
                    fecha = span_fecha.text.strip() if span_fecha else "Fecha no detectada"

                    print(f"✅ Tasa capturada con éxito: {tasa} Bs | Fecha: {fecha}")
                    return tasa, fecha
                else:
                    print("⚠️ No se pudo extraer el valor numérico de la tasa.")
            else:
                print("⚠️ No se encontró la sección #dolar en la página.")
        else:
            print("⚠️ No se recibió contenido HTML de la página.")

        return None, None

    except Exception as e:
        print(f"❌ Error al consultar el BCV: {e}")
        return None, None

def enviar_webhook(url, nombre_bot, payload):
    """Función auxiliar para enviar la notificación a una URL específica"""
    if not url:
        print(f"ℹ️ [{nombre_bot}] No hay URL configurada en los Secrets. Se omite.")
        return

    try:
        print(f"🚀 Enviando datos al {nombre_bot} ({url})...")
        res = requests.post(url, json=payload, timeout=10)

        if res.status_code == 200:
            datos_respuesta = res.json() if res.headers.get('content-type') == 'application/json' else {}

            if datos_respuesta.get("status") == "ignored":
                print(f"😴 [{nombre_bot}] La tasa de hoy ya estaba registrada. Sin cambios.")
            else:
                print(f"🔥 [{nombre_bot}] ¡Tasa enviada y actualizada con éxito!")
        else:
            print(f"❌ [{nombre_bot}] El bot rechazó la actualización. Respuesta: {res.status_code} - {res.text}")

    except Exception as e:
        print(f"❌ [{nombre_bot}] Error enviando la notificación: {e}")

def notificar_al_bot(tasa, fecha):
    if not tasa or not fecha:
        print("⚠️ No hay datos válidos para enviar al bot.")
        return

    json_payload = {
        "clave": CLAVE_SECRETA_BCV,
        "tasa": tasa,
        "fecha": fecha
    }

    # 1. Notificamos al Bot Principal
    enviar_webhook(URL_BOT_RAILWAY, "Bot Principal", json_payload)

    # 2. Notificamos al Bot Secundario
    enviar_webhook(URL_BOT_RAILWAY_SECUNDARIO, "Bot Secundario", json_payload)

if __name__ == "__main__":
    tasa, fecha = obtener_tasa_bcv_bypass()
    if tasa and fecha:
        notificar_al_bot(tasa, fecha)
        
