import os
import sys
import time
import serial
import threading
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy_garden.graph import Graph, MeshLinePlot
from kivy.clock import Clock

# === Definición de pantallas ===
class MenuScreen(Screen):
    pass

class ConexionScreen(Screen):
    pass

class CalibracionScreen(Screen):
    pass

class CarreraScreen(Screen):
    pass

class PolarisBT:
    def __init__(self, port="/dev/rfcomm0", baudrate=9600):
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=1)
        self.running = False
        self.handlers = {}  # Diccionario de callbacks

    def start(self):
        """Inicia el thread de escucha"""
        self.running = True
        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()

    def stop(self):
        """Detiene la comunicación"""
        self.running = False
        if self.ser.is_open:
            self.ser.close()

    def send(self, msg):
        """Envía un comando a la ESP (siempre con newline)"""
        if self.ser.is_open:
            self.ser.write((msg + "\n").encode())

    def register_handler(self, key, func):
        """Registra un callback para una cabecera (ej: 'C', 'G', 'P')"""
        self.handlers[key] = func

    def _listen(self):
        """Hilo interno que escucha datos y los despacha"""
        while self.running:
            try:
                line = self.ser.readline().decode().strip()
                if not line:
                    continue

                # Determinar tipo de mensaje
                if line.startswith("C:"):  # Centroide
                    valor = float(line.split(":")[1])
                    if "C" in self.handlers:
                        self.handlers["C"](valor)

                elif line.startswith("G,"):  # Get PID
                    partes = line.split(",")
                    if len(partes) == 5 and "G" in self.handlers:
                        kp, ti, td, vmax = map(float, partes[1:])
                        self.handlers["G"](kp, ti, td, vmax)

                elif line.startswith("P:"):  # Respuesta al set PID
                    if "P" in self.handlers:
                        self.handlers["P"](line[2:])  # "OK" o "ERR"

                elif line.startswith("S"):  # Inicio comunicación
                    if "S" in self.handlers:
                        self.handlers["S"](line)

                elif line in ("A", "B", "R"):  # Mensajes cortos
                    if line in self.handlers:
                        self.handlers[line](line)

                else:
                    # Debug u otros mensajes
                    if "DBG" in self.handlers:
                        self.handlers["DBG"](line)

            except Exception as e:
                print("Error parser:", e)

# === App principal ===
class GREAApp(App):
    def build(self):
        self.screen_manager = Builder.load_file("grea.kv")
        self.serial_conn = None
        self.running = True
        self.data_x = list(range(100))
        self.data_y = [0]*100
        return self.screen_manager

    # Métodos de conexión Bluetooth

    def connect_bt(self, mac_address):
        screen = self.root.get_screen("conexion")
        status_label = screen.ids.status_label

        if sys.platform.startswith("linux"):
            try:
                os.system("sudo rfcomm release /dev/rfcomm0")
                os.system(f"sudo rfcomm bind /dev/rfcomm0 {mac_address}")

                # Esperar hasta 5s a que /dev/rfcomm0 aparezca
                for _ in range(10):
                    if os.path.exists("/dev/rfcomm0"):
                        break
                    time.sleep(0.5)
                else:
                    status_label.text = "Estado: No se encontró /dev/rfcomm0"
                    return

                # Guardar conexión serie en la app
                self.serial_conn = serial.Serial("/dev/rfcomm0", baudrate=9600, timeout=1)
                self.serial_conn.write(b"S\n")  # inicio comunicación
                resp = self.serial_conn.readline().decode().strip()
                status_label.text = f"Estado: Conectado. Resp: {resp}"

            except Exception as e:
                status_label.text = f"Estado: Error ({e})"
        else:
            status_label.text = "Estado: SO no soportado aún"
   
    def reset_status_label(self):
        screen = self.root.get_screen("conexion")
        screen.ids.status_label.text = " "

    # Métodos de calibración y gráfico

    def iniciar_calibracion(self):
        if self.serial_conn:
            self.serial_conn.write(b"C\n")
            # lanzar hilo si no estaba corriendo
            if not hasattr(self, "thread_running") or not self.thread_running:
                self.thread_running = True
                threading.Thread(target=self.read_from_esp, daemon=True).start()

    def on_start(self):
        # Inicializar gráfico
        graph = self.screen_manager.get_screen("calibracion").ids.centroide_graph
        self.plot = MeshLinePlot(color=[0, 0.5, 1, 1])  # azul
        graph.add_plot(self.plot)

        # 🔹 Lanza hilo de lectura ESP
        if self.serial_conn:
            threading.Thread(target=self.read_from_esp, daemon=True).start()

        # Refrescar gráfico cada 50ms
        Clock.schedule_interval(self.update_graph, 0.05)

    def read_from_esp(self):
        """Lee datos desde la ESP32 en un hilo."""
        while self.running and self.serial_conn:
            try:
                line = self.serial_conn.readline().decode().strip()
                if not line:
                    continue

                if line.startswith("C:"):  # dato de centroide
                    valor = float(line.split(":")[1])
                    Clock.schedule_once(lambda dt: self.update_centroide(valor))

                elif line.startswith("G,"):  # parámetros PID
                    _, kp, ti, td, vmax = line.split(",")
                    pantalla = self.screen_manager.get_screen("calibracion")
                    Clock.schedule_once(lambda dt: self._update_pid_ui(pantalla, kp, ti, td, vmax))

                elif line.startswith("P:"):
                    print("Respuesta Set PID:", line)

                else:
                    print("Mensaje no reconocido:", line)

            except Exception as e:
                print("Error lectura ESP:", e)

    def _update_pid_ui(self, pantalla, kp, ti, td, vmax):
        pantalla.ids.kp_input.text = kp
        pantalla.ids.ti_input.text = ti
        pantalla.ids.td_input.text = td
        pantalla.ids.vmax_input.text = vmax


    def update_centroide(self, valor):
        """Actualiza label y buffer de datos para graficar"""
        pantalla = self.screen_manager.get_screen("calibracion")
        pantalla.ids.centroide_label.text = f"Centroide: {valor:.2f} mm"

        self.data_y.append(valor)
        self.data_y.pop(0)

    def update_graph(self, dt):
        self.plot.points = list(zip(self.data_x, self.data_y))

    # Métodos PID
    def set_pid(self, kp, ti, td, vmax):
        cmd = f"P,{kp},{ti},{td},{vmax}\n"
        self.bt_send(cmd)

    def get_pid(self):
        self.bt_send("G")
        resp = self.bt_read()
        if resp and resp.startswith("G"):
            _, kp, ti, td, vmax = resp.split(",")
            screen = self.screen_manager.get_screen("calibracion")
            screen.ids.kp_input.text = kp
            screen.ids.ti_input.text = ti
            screen.ids.td_input.text = td
            screen.ids.vmax_input.text = vmax

    def enviar_comando(self, c):
        self.bt_send(c)

    # Métodos stub para BT (reemplazar luego)
    def bt_send(self, msg):
        print("Enviado:", msg.strip())

    def bt_read(self):
        # Simulación
        return "G,1.0,0.5,0.1,200"


if __name__ == "__main__":
    GREAApp().run()
