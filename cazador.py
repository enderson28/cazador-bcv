import os
import re
import subprocess
import requests
from bs4 import BeautifulSoup

URL_BOT_RAILWAY = os.getenv("URL_BOT_RAILWAY")
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
            datos_respuesta = res.json() if res.headers.get('content-type') == 'application/json' else {}
            
            # Si el webhook te responde que la tasa ya era la misma
            if datos_respuesta.get("status") == "sin_cambios":
                print("ℹ️ La tasa de hoy ya estaba registrada. Cazador finalizado sin cambios.")
            else:
                print("🔥 ¡Tasa enviada y actualizada con éxito en la memoria del bot!")
        else:       
            print(f"❌ El bot rechazó la actualización. Respuesta: {res.status_code} - {res.text}")

    except Exception as e:
        print(f"❌ Error enviando la notificación al bot: {e}")

if __name__ == "__main__":
    tasa, fecha = obtener_tasa_bcv_bypass()
    if tasa and fecha:
        notificar_al_bot(tasa, fecha)
                
        
            
    
        
        
        
              
