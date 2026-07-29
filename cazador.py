import os
import re
import requests
from bs4 import BeautifulSoup

# Configuración de variables desde el entorno
API_KEY_SCRAPER = os.getenv("API_KEY_SCRAPER") # Tu API Key gratuita de ScraperAPI
URL_BOT_RAILWAY = os.getenv("URL_BOT_RAILWAY") # Ejemplo: https://tu-bot.up.railway.app/actualizar_bcv
CLAVE_SECRETA_BCV = os.getenv("CLAVE_SECRETA_BCV")

def obtener_tasa_bcv_bypass():
    target_url = "https://www.bcv.org.ve"
    
    # Construimos la consulta a través de ScraperAPI para evadir el bloqueo del BCV
    proxy_url = f"http://api.scraperapi.com?api_key={API_KEY_SCRAPER}&url={target_url}"
    
    try:
        print("🔍 Consultando la web del BCV mediante proxy residencial...")
        response = requests.get(proxy_url, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            div_dolar = soup.find("div", id="dolar")
            
            if div_dolar:
                raw_text = div_dolar.get_text()
                match = re.search(r'\d{2,3}[\.,]\d+', raw_text)
                
                if match:
                    val_str = match.group(1).replace('.', '').replace(',', '.')
                    tasa = float(val_str)
                    
                    # Capturamos la Fecha Valor
                    span_fecha = soup.find("span", class_="date-display-single")
                    fecha = span_fecha.text.strip() if span_fecha else "2026-07-29"
                    
                    print(f"✅ Tasa capturada con éxito: {tasa} Bs | Fecha: {fecha}")
                    return tasa, fecha
                    
        print(f"⚠️ La respuesta de la web no devolvió datos válidos. Status: {response.status_code}")
        return None, None

    except Exception as e:
        print(f"❌ Error al conectar con el proxy: {e}")
        return None, None

def notificar_al_bot(tasa, fecha):
    if not tasa or not fecha:
        print("⚠️ No hay datos válidos para enviar al bot.")
        return

    payload = {
        "clave": CLAVE_SECRETA_BCV,
        "tasa": tasa,
        "fecha": fecha
    }

    try:
        print(f"🚀 Enviando datos al bot en Railway ({URL_BOT_RAILWAY})...")
        res = requests.post(URL_BOT_RAILWAY, json=payload, timeout=10)
        
        if res.status_code == 200:
            print("🔥 ¡Tasa enviada y actualizada con éxito en la memoria del bot!")
        else:
            print(f"❌ El bot rechazó la actualización. Respuesta: {res.status_code} - {res.text}")

    except Exception as e:
        print(f"❌ Error enviando la notificación al bot: {e}")

if __name__ == "__main__":
    tasa, fecha = obtener_tasa_bcv_bypass()
    if tasa and fecha:
        notificar_al_bot(tasa, fecha)
              
