import os, time, serial

mac = "38:18:2B:8A:D2:8A"

os.system("sudo rfcomm release /dev/rfcomm0") # No lo puede hacer porque no es sudo
os.system(f"sudo rfcomm bind /dev/rfcomm0 {mac}") # No lo puede hacer porque no es sudo (Can't create device: Operation not permitted)

# Esperar hasta que el dispositivo esté disponible (máx 5 segundos)
for _ in range(10):
    if os.path.exists("/dev/rfcomm0"):
        break
    time.sleep(0.5)
else:
    print("No se encontró /dev/rfcomm0")
    exit(1)

try:
    with serial.Serial("/dev/rfcomm0", baudrate=9600, timeout=2) as ser:
        ser.write(b"S")
        resp = ser.readline().decode().strip()
        print("Respuesta:", resp)
except Exception as e:
    print("Error al abrir el puerto serie:", e)