import os
import time
import base64
from requests import get
from requests.structures import CaseInsensitiveDict
from pycognito import Cognito

########################## EDITAR ###################################
# Bot Telegram
chat = "-1000000000000" #chatid del grupo  o usuario de telegram
token_bot = "0000000000:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" # token del bot de telegram

# Usuario y dispositivo Komobi
usuario_komobi = "micorreo@ñññ.com" # correo de tu cuenta Komobi (el que usas en la app)
contrasena_komobi = "micontraseña" # Contraseña de tu cuenta Komobi (la que usas en la app)
id_dispositivo_komobi = "860000000000000" # ID del kit de Komobi, en la APP -> Ajustes -> Configurar Dispotitivo -> Dispositivos emparejados
#########################################################################

os.chdir(os.path.dirname(__file__))

limpiar = "cls" if os.name == "nt" else "clear"

ruta_archivo_token = "ultimo_token.txt"

def enviar_mensaje(chat_id, mensaje):
    try:
        url = f"https://api.telegram.org/bot{token_bot}/sendMessage"
        parametros = {
            'chat_id': chat_id,
            'text': mensaje
        }
        get(url, params=parametros, timeout=10)
    except:
        os.system(limpiar)
        print("Error al enviar el mensaje de Telegram, reiniciando...")
        time.sleep(5)
        main()


def obtener_token():
    usuario = Cognito(servidor_cognito, app_client_id, username=usuario_komobi, client_secret=app_client_secret)
    try:
        usuario.authenticate(password=contrasena_komobi)
    except:
        os.system(limpiar)
        print("Error al obtener el token de acceso, reiniciando...")
        time.sleep(5)
        main()
    return usuario.id_token

def d(_str):
    for d in range(99//1//2//3//6):
        _str = base64.b64decode(_str + "==").decode('utf-8')
    return _str

def comprobar_alarma(token, inicio):
    global ultima_alarma
    url = f"https://{api_aws}/dev/v1/devices/{id_dispositivo_komobi}/info"
    headers = CaseInsensitiveDict()
    headers["Host"] = f"{api_aws}"
    headers["authorization"] = token
    headers["content-type"] = "application/json"
    headers["user-agent"] = "okhttp/3.14.7"

    try:
        respuesta = get(url, headers=headers, timeout=10)
        respuesta_json = respuesta.json()
    except:
        os.system(limpiar)
        print("Error al conectar con el servidor de datos de Komobi, reiniciando...")
        time.sleep(5)
        main()

    if "expired" in respuesta.text or '{"message":null}' in respuesta.text:
        token = obtener_token()
        with open(ruta_archivo_token, "w") as archivo_token:
            archivo_token.write(token)
        os.system(limpiar)
        print("El token de acceso ha expirado, obteniendo uno nuevo...")
        time.sleep(1)
        main()

    if '"errorCode":"202"' in respuesta.text:
        os.system(limpiar)
        print("ID de dispositivo no existe o no está vinculado a la cuenta usada")
        time.sleep(5)
        main()

    else:
        estado_alarma = respuesta_json['devices']['alarmConfig']['isFired']

        if inicio == 1:
            ultima_alarma = respuesta_json['devices']['alarmConfig']['lastFired']
            return
        else:
            alarma_actual = respuesta_json['devices']['alarmConfig']['lastFired']

        if alarma_actual != ultima_alarma and estado_alarma:
            ahora = time.time()
            fecha_hora_alarma = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(alarma_actual))
            os.system(limpiar)
            print("Alarma detectada", fecha_hora_alarma)
            mensaje = f"Alarma detectada\nFecha de detección original: {fecha_hora_alarma}"
            enviar_mensaje(chat_id=chat, mensaje=mensaje)
            ultima_alarma = alarma_actual
            time.sleep(5)
        else:
            ahora = time.time()
            fecha_hora_actual = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(ahora))
            print("Alarma normal", fecha_hora_actual)

servidor_cognito = d("WlhVdGQyVnpkQzB4WDJSeU9HZG1kV3cyVlE")
app_client_id = d("TlRKck9HWmtZblZ5WjNKcU1YWnVjelp4WkRsc2JHTXhkWEk")
app_client_secret = d("TldSd2FXTTNiM0F6Wnpjelp6Vm1ZVE56T1c1dmRUWTFZblpsTTJseGNqWmhNbkZwYTI4NFp6RTJaMlExTnpNd2FEWXc")
api_aws = d("WTNZMWQyWjBiWFprT0M1bGVHVmpkWFJsTFdGd2FTNWxkUzEzWlhOMExURXVZVzFoZW05dVlYZHpMbU52YlE")

def main():
    inicio = 1
    token = ""
    if os.path.exists(ruta_archivo_token):
        with open(ruta_archivo_token, "r") as archivo_token:
            token = archivo_token.readline()

    if not token:
        token = obtener_token()
        with open(ruta_archivo_token, "w") as archivo_token:
            archivo_token.write(token)

    comprobar_alarma(token, inicio)
    time.sleep(1)
    inicio = 0
    while True:
        comprobar_alarma(token, inicio)
        time.sleep(2)

if __name__ == "__main__":
    main()
