import os
import re
import requests
import cloudscraper
from bs4 import BeautifulSoup

URL_BOT_RAILWAY = os.getenv("URL_BOT_RAILWAY")
CLAVE_SECRETA_BCV = os.getenv("CLAVE_SECRETA_BCV")

def obtener_tasa_bcv_bypass():
    target_url = "https://www.bcv.org.ve"
    
    try:
        print("🔍 Consultando la web del BCV usando cloudscraper...")
        
        # Ocultar alertas de SSL
        requests.packages.urllib3.disable_warnings()

        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        # Desactivamos verificación de certificado SSL
        response = scraper.get(target_url, timeout=30, verify=False)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
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
                print("⚠️ No se encontró la sección #dolar en la página.")
        else:
            print(f"⚠️ La respuesta devolvió código HTTP: {response.status_code}")
            
        return None, None

    except Exception as e:
        print(f"❌ Error al consultar el BCV: {e}")
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
        
        
        
              
