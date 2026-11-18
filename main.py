AUTO-DOCTOR-PROimport os
import sys
import time
import socket
import threading
import traceback
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import platform
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp, sp

try:
    import obd
    OBD_AVAILABLE = True
except Exception:
    obd = None
    OBD_AVAILABLE = False

try:
    from jnius import autoclass
    from android.permissions import request_permissions
    ANDROID_AVAILABLE = platform == "android"
except Exception:
    autoclass = None
    request_permissions = None
    ANDROID_AVAILABLE = False

Window.clearcolor = (0.04, 0.07, 0.13, 1)

KV = """
BoxLayout:
    orientation: "vertical"
    padding: dp(8)
    spacing: dp(6)

    canvas.before:
        Color:
            rgba: 0.04, 0.07, 0.13, 1
        Rectangle:
            pos: self.pos
            size: self.size

    ScrollView:
        do_scroll_x: False
        bar_width: dp(4)
        scroll_type: ["bars", "content"]

        BoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: self.minimum_height
            spacing: dp(9)
            padding: dp(3)

            BoxLayout:
                size_hint_y: None
                height: dp(72)
                padding: dp(8)
                spacing: dp(5)

                canvas.before:
                    Color:
                        rgba: 0.08, 0.13, 0.21, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [12]

                BoxLayout:
                    orientation: "vertical"

                    Label:
                        text: "AUTO DOCTOR PRO"
                        font_size: sp(21)
                        bold: True
                        color: 0, 0.8, 1, 1

                    Label:
                        text: "Adel Omar Abdel Aziz | AL ADL GROUP"
                        font_size: sp(10)
                        color: 0.8, 0.85, 0.9, 1

                Label:
                    id: status
                    text: "DISCONNECTED"
                    font_size: sp(12)
                    color: 1, 0.3, 0.3, 1
                    size_hint_x: 0.42

            Spinner:
                id: connection_type
                text: "BLUETOOTH"
                values: ["BLUETOOTH", "WIFI"]
                size_hint_y: None
                height: dp(44)

            TextInput:
                id: address
                hint_text: "Bluetooth MAC or WiFi IP"
                multiline: False
                size_hint_y: None
                height: dp(44)

            TextInput:
                id: port
                hint_text: "WiFi Port"
                text: "35000"
                multiline: False
                size_hint_y: None
                height: dp(44)

            BoxLayout:
                size_hint_y: None
                height: dp(46)
                spacing: dp(8)

                Button:
                    text: "CONNECT"
                    on_release: app.connect_device()

                Button:
                    text: "DISCONNECT"
                    on_release: app.disconnect_device()

            Label:
                text: "LIVE VEHICLE DASHBOARD"
                color: 0, 0.8, 1, 1
                bold: True
                size_hint_y: None
                height: dp(35)

            GridLayout:
                cols: 2
                spacing: dp(8)
                size_hint_y: None
                height: dp(220)
                row_default_height: dp(100)
                row_force_default: True

                BoxLayout:
                    orientation: "vertical"
                    padding: dp(5)
                    canvas.before:
                        Color:
                            rgba: 0.08, 0.15, 0.25, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [12]

                    Label:
                        text: "ENGINE RPM"
                        color: 0, 0.8, 1, 1
                        font_size: sp(13)

                    Label:
                        id: rpm
                        text: "0"
                        font_size: sp(27)
                        bold: True

                BoxLayout:
                    orientation: "vertical"
                    padding: dp(5)
                    canvas.before:
                        Color:
                            rgba: 0.08, 0.20, 0.19, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [12]

                    Label:
                        text: "SPEED KM/H"
                        color: 0, 1, 0.6, 1
                        font_size: sp(13)

                    Label:
                        id: speed
                        text: "0"
                        font_size: sp(27)
                        bold: True

                BoxLayout:
                    orientation: "vertical"
                    padding: dp(5)
                    canvas.before:
                        Color:
                            rgba: 0.22, 0.14, 0.10, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [12]

                    Label:
                        text: "COOLANT TEMP"
                        color: 1, 0.65, 0.2, 1
                        font_size: sp(13)

                    Label:
                        id: coolant
                        text: "0"
                        font_size: sp(27)

                BoxLayout:
                    orientation: "vertical"
                    padding: dp(5)
                    canvas.before:
                        Color:
                            rgba: 0.17, 0.12, 0.25, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [12]

                    Label:
                        text: "ENGINE LOAD"
                        color: 0.65, 0.5, 1, 1
                        font_size: sp(13)

                    Label:
                        id: load
                        text: "0"
                        font_size: sp(27)

            Label:
                text: "DIAGNOSTIC CENTER"
                color: 0, 0.8, 1, 1
                bold: True
                size_hint_y: None
                height: dp(35)

            GridLayout:
                cols: 2
                spacing: dp(8)
                size_hint_y: None
                height: dp(165)
                row_default_height: dp(48)
                row_force_default: True

                Button:
                    text: "FULL SCAN"
                    on_release: app.full_scan()

                Button:
                    text: "ENGINE TEST"
                    on_release: app.engine_scan()

                Button:
                    text: "READ DTC"
                    on_release: app.read_errors()

                Button:
                    text: "LIVE DATA"
                    on_release: app.toggle_live()

                Button:
                    text: "CLEAR DTC"
                    on_release: app.confirm_clear()

                Button:
                    text: "STOP LIVE"
                    on_release: app.stop_live()

            Label:
                text: "DIAGNOSTIC RESULTS"
                color: 0, 0.8, 1, 1
                size_hint_y: None
                height: dp(30)

            TextInput:
                id: output
                text: "AUTO DOCTOR PRO READY"
                readonly: True
                size_hint_y: None
                height: dp(180)
                background_color: 0.05, 0.09, 0.15, 1
                foreground_color: 0.2, 0.9, 1, 1
                font_size: sp(13)

            Button:
                text: "GENERATE PDF REPORT"
                size_hint_y: None
                height: dp(48)
                on_release: app.generate_pdf()

            Label:
                text: "DEVELOPED BY ADEL OMAR ABDEL AZIZ"
                color: 0, 0.8, 1, 1
                font_size: sp(11)
                size_hint_y: None
                height: dp(30)

            Label:
                text: "AL ADL GROUP"
                color: 0.8, 0.85, 0.9, 1
                font_size: sp(11)
                size_hint_y: None
                height: dp(25)
"""


class AutoDoctorPro(App):

    def build(self):
        self.title = "AUTO DOCTOR PRO"
        self.connection = None
        self.bluetooth_socket = None
        self.wifi_socket = None
        self.running = False
        self.last_report = "AUTO DOCTOR PRO READY"
        self.lock = threading.RLock()

        self.root_widget = Builder.load_string(KV)

        if ANDROID_AVAILABLE:
            self.request_android_permissions()

        return self.root_widget

    def on_start(self):
        self.log("AUTO DOCTOR PRO STARTED")

    def on_stop(self):
        self.running = False
        self.disconnect_device()

    def log(self, message):
        self.last_report = str(message)

        def update(dt):
            if self.root:
                self.root.ids.output.text = str(message)

        Clock.schedule_once(update)

    def popup(self, title, message):
        def show(dt):
            Popup(
                title=title,
                content=Label(
                    text=str(message),
                    color=(1, 1, 1, 1)
                ),
                size_hint=(0.85, 0.4)
            ).open()

        Clock.schedule_once(show)

    def status(self, message, connected=False):
        def update(dt):
            self.root.ids.status.text = message
            self.root.ids.status.color = (
                (0, 1, 0.5, 1)
                if connected else (1, 0.3, 0.3, 1)
            )

        Clock.schedule_once(update)

    def background(self, func):
        threading.Thread(
            target=func,
            daemon=True
        ).start()

    def request_android_permissions(self):
        if not request_permissions:
            return

        try:
            permissions = [
                "android.permission.INTERNET",
                "android.permission.ACCESS_NETWORK_STATE"
            ]

            permissions.extend([
                "android.permission.BLUETOOTH",
                "android.permission.BLUETOOTH_ADMIN",
                "android.permission.BLUETOOTH_CONNECT",
                "android.permission.BLUETOOTH_SCAN"
            ])

            request_permissions(permissions)

        except Exception as e:
            self.log("PERMISSION ERROR: " + str(e))

    def connect_device(self):
        kind = self.root.ids.connection_type.text
        address = self.root.ids.address.text.strip()

        if not address:
            self.popup("CONNECTION", "Enter device address first.")
            return

        self.log("CONNECTING TO ELM327...")
        self.background(lambda: self._connect(kind, address))

    def _connect(self, kind, address):
        try:
            self.disconnect_device()

            if kind == "WIFI":
                port = int(self.root.ids.port.text or "35000")

                sock = socket.socket(
                    socket.AF_INET,
                    socket.SOCK_STREAM
                )

                sock.settimeout(8)
                sock.connect((address, port))
                sock.settimeout(3)

                with self.lock:
                    self.wifi_socket = sock

                self.send_at("ATZ")
                self.send_at("ATE0")
                self.send_at("ATL0")
                self.send_at("ATSP0")

            else:
                if not ANDROID_AVAILABLE:
                    raise Exception(
                        "Bluetooth connection requires Android."
                    )

                self.connect_bluetooth(address)

            self.status("CONNECTED", True)
            self.log("ELM327 CONNECTED SUCCESSFULLY")

        except Exception as e:
            self.status("CONNECTION FAILED")
            self.log("CONNECTION ERROR:\n" + str(e))

    def connect_bluetooth(self, address):
        if not autoclass:
            raise Exception("Android Bluetooth unavailable.")

        BluetoothAdapter = autoclass(
            "android.bluetooth.BluetoothAdapter"
        )

        UUID = autoclass("java.util.UUID")
        adapter = BluetoothAdapter.getDefaultAdapter()

        if adapter is None:
            raise Exception("Bluetooth not supported.")

        if not adapter.isEnabled():
            raise Exception("Enable Bluetooth first.")

        device = adapter.getRemoteDevice(address)

        uuid = UUID.fromString(
            "00001101-0000-1000-8000-00805F9B34FB"
        )

        sock = device.createRfcommSocketToServiceRecord(uuid)
        sock.connect()

        with self.lock:
            self.bluetooth_socket = sock

        self.send_at("ATZ")
        self.send_at("ATE0")
        self.send_at("ATL0")
        self.send_at("ATSP0")

    def disconnect_device(self):
        self.running = False

        with self.lock:
            for sock in (
                self.wifi_socket,
                self.bluetooth_socket
            ):
                if sock:
                    try:
                        sock.close()
                    except Exception:
                        pass

            self.wifi_socket = None
            self.bluetooth_socket = None

            if self.connection:
                try:
                    self.connection.close()
                except Exception:
                    pass

                self.connection = None

        self.status("DISCONNECTED")
        self.log("DEVICE DISCONNECTED")

    def send_at(self, command):
        return self.send_command(command)

    def send_command(self, command):
        with self.lock:
            sock = self.wifi_socket or self.bluetooth_socket

            if not sock:
                raise Exception("No ELM327 connection.")

            data = command.strip() + "\r"

            if self.wifi_socket:
                sock.sendall(data.encode("ascii"))
            else:
                output = autoclass(
                    "java.lang.String"
                )(data).getBytes("US-ASCII")

                sock.getOutputStream().write(output)
                sock.getOutputStream().flush()

            response = ""

            if self.wifi_socket:
                while True:
                    try:
                        chunk = sock.recv(1024)
                    except socket.timeout:
                        break

                    if not chunk:
                        break

                    response += chunk.decode(
                        "ascii", errors="ignore"
                    )

                    if ">" in response:
                        break

            else:
                stream = sock.getInputStream()
                deadline = time.time() + 5

                while time.time() < deadline:
                    if stream.available() > 0:
                        value = stream.read()

                        if value >= 0:
                            response += chr(value)

                            if ">" in response:
                                break
                    else:
                        time.sleep(0.03)

            return response.replace(">", "").strip()

    def read_pid(self, pid):
        response = self.send_command(pid)
        lines = response.replace("\r", "\n").split("\n")
        values = []

        for line in lines:
            line = line.strip().replace(" ", "")

            if line.startswith("41"):
                try:
                    values.extend([
                        int(line[i:i + 2], 16)
                        for i in range(4, len(line), 2)
                        if len(line[i:i + 2]) == 2
                    ])
                except Exception:
                    pass

        return values

    def get_data(self, pid):
        values = self.read_pid(pid)

        if not values:
            return None

        a = values[0]

        if pid == "010C" and len(values) >= 2:
            return ((a * 256) + values[1]) / 4

        if pid == "010D":
            return a

        if pid == "0105":
            return a - 40

        if pid == "0104":
            return round(a * 100 / 255, 1)

        return a

    def full_scan(self):
        self.background(self._full_scan)

    def _full_scan(self):
        try:
            codes = self.send_command("03")

            self.log(
                "FULL VEHICLE SCAN\n"
                "====================\n"
                + codes
            )

        except Exception as e:
            self.log("SCAN ERROR: " + str(e))

    def engine_scan(self):
        def scan():
            try:
                data = [
                    ("RPM", "010C"),
                    ("SPEED", "010D"),
                    ("COOLANT TEMP", "0105"),
                    ("ENGINE LOAD", "0104")
                ]

                result = "ENGINE DIAGNOSTIC REPORT\n\n"

                for name, pid in data:
                    value = self.get_data(pid)
                    result += f"{name}: {value}\n"

                self.log(result)

            except Exception as e:
                self.log("ENGINE ERROR: " + str(e))

        self.background(scan)

    def read_errors(self):
        self.full_scan()

    def confirm_clear(self):
        layout = BoxLayout(
            orientation="vertical",
            padding=12,
            spacing=10
        )

        layout.add_widget(
            Label(
                text="WARNING!\nClear diagnostic trouble codes?"
            )
        )

        from kivy.uix.button import Button

        button = Button(text="CONFIRM CLEAR")
        layout.add_widget(button)

        popup = Popup(
            title="CLEAR DTC",
            content=layout,
            size_hint=(0.85, 0.4)
        )

        button.bind(
            on_release=lambda x: (
                popup.dismiss(),
                self.clear_errors()
            )
        )

        popup.open()

    def clear_errors(self):
        def clear():
            try:
                result = self.send_command("04")
                self.log("CLEAR COMMAND RESPONSE:\n" + result)
            except Exception as e:
                self.log("CLEAR ERROR: " + str(e))

        self.background(clear)

    def toggle_live(self):
        if self.running:
            self.stop_live()
            return

        self.running = True
        self.live_data()

    def stop_live(self):
        self.running = False
        self.log("LIVE DATA STOPPED")

    def live_data(self):
        if not self.running:
            return

        def read():
            try:
                values = {
                    "rpm": self.get_data("010C"),
                    "speed": self.get_data("010D"),
                    "coolant": self.get_data("0105"),
                    "load": self.get_data("0104")
                }

                def update(dt):
                    if not self.running:
                        return

                    for key, value in values.items():
                        self.root.ids[key].text = (
                            str(value)
                            if value is not None else "N/A"
                        )

                Clock.schedule_once(update)

            except Exception as e:
                self.log("LIVE ERROR: " + str(e))
                self.running = False

        self.background(read)

        Clock.schedule_once(
            lambda dt: self.live_data()
            if self.running else None,
            2
        )

    def generate_pdf(self):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas

            folder = self.user_data_dir

            filename = os.path.join(
                folder,
                "AUTO_DOCTOR_"
                + datetime.now().strftime("%Y%m%d_%H%M%S")
                + ".pdf"
            )

            pdf = canvas.Canvas(filename, pagesize=A4)
            width, height = A4

            pdf.setFillColorRGB(0.04, 0.08, 0.16)
            pdf.rect(0, 0, width, height, fill=1)

            pdf.setFillColorRGB(0, 0.8, 1)
            pdf.setFont("Helvetica-Bold", 22)
            pdf.drawString(
                40, height - 60, "AUTO DOCTOR PRO"
            )

            pdf.setFillColorRGB(1, 1, 1)
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(
                40, height - 90,
                "Developer: Adel Omar Abdel Aziz"
            )

            pdf.drawString(
                40, height - 110,
                "Company: AL ADL GROUP"
            )

            pdf.setFont("Helvetica", 10)
            pdf.drawString(
                40, height - 140,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

            y = height - 175

            for line in self.last_report.splitlines():
                if y < 50:
                    pdf.showPage()
                    y = height - 50

                pdf.drawString(
                    40, y,
                    line.encode(
                        "ascii", errors="replace"
                    ).decode()[:100]
                )

                y -= 16

            pdf.save()

            self.popup(
                "PDF REPORT",
                "Report saved:\n" + filename
            )

        except Exception as e:
            self.popup("PDF ERROR", str(e))


if __name__ == "__main__":
    try:
        AutoDoctorPro().run()

    except Exception:
        error = traceback.format_exc()

        try:
            with open(
                "/sdcard/auto_doctor_error.txt",
                "w"
            ) as f:
                f.write(error)

        except Exception:
            pass
