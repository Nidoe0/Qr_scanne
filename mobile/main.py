import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.utils import platform

from services.api_service import APIService

KV = """
#:import dp kivy.metrics.dp
<Screen>:
    canvas.before:
        Color:
            rgba: app.background_color
        Rectangle:
            pos: self.pos
            size: self.size

<SplashScreen>:
    BoxLayout:
        orientation: "vertical"
        spacing: dp(14)
        padding: dp(28)
        Label:
            text: "Q"
            font_size: "82sp"
            bold: True
            color: app.light_color
        Label:
            text: "QR CONNECT"
            font_size: "27sp"
            bold: True
            color: app.light_color
        Label:
            text: "Chargement..."
            color: app.secondary_color
            size_hint_y: None
            height: dp(36)

<WelcomeScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(24)
        spacing: dp(18)
        Widget:
            size_hint_y: 0.5
        Label:
            text: "Transfert rapide • sans compte requis"
            font_size: "23sp"
            bold: True
            color: app.light_color
            text_size: self.width, None
            halign: "center"
            size_hint_y: None
            height: self.texture_size[1] + dp(12)
        Label:
            text: "Partagez vos fichiers en un clic avec un QR code."
            font_size: "17sp"
            color: app.light_color
            text_size: self.width, None
            halign: "center"
            size_hint_y: None
            height: self.texture_size[1] + dp(12)
        Label:
            text: "QR Connect permet d’envoyer des fichiers, vidéos, images, documents et dossiers compressés entre appareils connectés au même Wi-Fi ou point d’accès. Les transferts via des réseaux différents nécessitent un serveur accessible sur Internet."
            font_size: "14sp"
            color: app.light_color
            text_size: self.width, None
            halign: "center"
            valign: "middle"
        Button:
            text: "Ouvrir l’application"
            size_hint_y: None
            height: dp(54)
            background_normal: ""
            background_color: app.secondary_color
            color: app.light_color
            on_release: app.go("connection")
        Widget:
            size_hint_y: 0.5

<ConnectionScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(22)
        spacing: dp(14)
        Label:
            text: "Connecter les appareils"
            font_size: "24sp"
            bold: True
            color: app.primary_color
            size_hint_y: None
            height: dp(48)
        Label:
            text: "Adresse du serveur FastAPI (ordinateur ou appareil qui héberge le transfert)"
            color: app.text_color
            text_size: self.width, None
            halign: "left"
            size_hint_y: None
            height: self.texture_size[1] + dp(8)
        TextInput:
            id: server_url
            text: app.api.base_url
            hint_text: "http://192.168.1.10:8000"
            multiline: False
            size_hint_y: None
            height: dp(50)
            foreground_color: app.text_color
        Label:
            text: "Les deux appareils doivent être sur le même Wi-Fi / point d’accès. Saisis l’adresse IP du PC qui exécute FastAPI, pas 127.0.0.1."
            color: app.text_color
            text_size: self.width, None
            halign: "left"
        Button:
            text: "Tester la connexion"
            size_hint_y: None
            height: dp(50)
            background_normal: ""
            background_color: app.primary_color
            on_release: root.test_connection(server_url.text)
        Label:
            id: connection_status
            text: root.status
            color: app.text_color
            text_size: self.width, None
            halign: "center"
        Button:
            text: "Continuer"
            size_hint_y: None
            height: dp(50)
            background_normal: ""
            background_color: app.secondary_color
            on_release: root.save_server(server_url.text)
        Button:
            text: "Retour"
            size_hint_y: None
            height: dp(42)
            background_normal: ""
            background_color: app.muted_color
            color: app.text_color
            on_release: app.go("welcome")

<DashboardScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(18)
        spacing: dp(14)
        Label:
            text: "QR CONNECT"
            font_size: "27sp"
            bold: True
            color: app.primary_color
            size_hint_y: None
            height: dp(48)
        Label:
            text: "Partagez vos fichiers simplement"
            color: app.text_color
            size_hint_y: None
            height: dp(30)
        Button:
            text: "📤   Envoyer"
            size_hint_y: None
            height: dp(64)
            background_normal: ""
            background_color: app.primary_color
            on_release: app.go("send")
        Button:
            text: "📥   Recevoir"
            size_hint_y: None
            height: dp(64)
            background_normal: ""
            background_color: app.primary_color
            on_release: app.go("receive")
        Button:
            text: "⚙   Paramètres"
            size_hint_y: None
            height: dp(64)
            background_normal: ""
            background_color: app.secondary_color
            on_release: app.go("settings")
        Widget:
        Label:
            text: "Serveur : " + app.api.base_url
            color: app.text_color
            font_size: "12sp"
            size_hint_y: None
            height: dp(24)

<SendScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(18)
        spacing: dp(12)
        Label:
            text: "Envoyer des fichiers"
            font_size: "24sp"
            bold: True
            color: app.primary_color
            size_hint_y: None
            height: dp(46)
        Label:
            text: "Formats : images, vidéos, audio, PDF, Word, Excel, PowerPoint, TXT et ZIP."
            color: app.text_color
            text_size: self.width, None
            halign: "left"
            size_hint_y: None
            height: self.texture_size[1] + dp(10)
        Button:
            text: "Choisir un ou plusieurs fichiers"
            size_hint_y: None
            height: dp(54)
            background_normal: ""
            background_color: app.primary_color
            on_release: root.choose_files()
        Label:
            id: selected_label
            text: root.message
            color: app.text_color
            text_size: self.width, None
            halign: "center"
        Image:
            id: qr_image
            source: ""
            allow_stretch: True
            keep_ratio: True
        Button:
            text: "Réessayer le dernier transfert"
            size_hint_y: None
            height: dp(48)
            background_normal: ""
            background_color: app.secondary_color
            on_release: root.retry()
        Button:
            text: "Arrêter / Retour"
            size_hint_y: None
            height: dp(48)
            background_normal: ""
            background_color: app.muted_color
            color: app.text_color
            on_release: app.go("dashboard")

<ReceiveScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(18)
        spacing: dp(12)
        Label:
            text: "Recevoir un fichier"
            font_size: "24sp"
            bold: True
            color: app.primary_color
            size_hint_y: None
            height: dp(46)
        Label:
            text: "Scanne le QR code avec une future fonction de scan intégrée, ou saisis le jeton de partage affiché par l'appareil expéditeur."
            color: app.text_color
            text_size: self.width, None
            halign: "left"
            size_hint_y: None
            height: self.texture_size[1] + dp(12)
        TextInput:
            id: token
            hint_text: "Jeton de partage"
            multiline: False
            size_hint_y: None
            height: dp(50)
            foreground_color: app.text_color
        Button:
            text: "Télécharger le fichier"
            size_hint_y: None
            height: dp(54)
            background_normal: ""
            background_color: app.primary_color
            on_release: root.download(token.text)
        Label:
            id: receive_status
            text: root.message
            color: app.text_color
            text_size: self.width, None
            halign: "center"
        Button:
            text: "Retour"
            size_hint_y: None
            height: dp(48)
            background_normal: ""
            background_color: app.muted_color
            color: app.text_color
            on_release: app.go("dashboard")

<SettingsScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(18)
        spacing: dp(12)
        Label:
            text: "Paramètres"
            font_size: "24sp"
            bold: True
            color: app.primary_color
            size_hint_y: None
            height: dp(46)
        Label:
            text: "Thème de l'application"
            color: app.text_color
            size_hint_y: None
            height: dp(30)
        Button:
            text: "Mode clair"
            size_hint_y: None
            height: dp(48)
            background_normal: ""
            background_color: app.secondary_color
            on_release: app.set_theme("light")
        Button:
            text: "Mode sombre"
            size_hint_y: None
            height: dp(48)
            background_normal: ""
            background_color: app.primary_color
            on_release: app.set_theme("dark")
        Label:
            text: "Connexion : Wi-Fi / point d’accès avec adresse du serveur. Le scan caméra et Google Drive ne sont pas encore intégrés."
            color: app.text_color
            text_size: self.width, None
            halign: "left"
        Button:
            text: "Modifier la connexion"
            size_hint_y: None
            height: dp(48)
            background_normal: ""
            background_color: app.secondary_color
            on_release: app.go("connection")
        Button:
            text: "Retour"
            size_hint_y: None
            height: dp(48)
            background_normal: ""
            background_color: app.muted_color
            color: app.text_color
            on_release: app.go("dashboard")
"""

class SplashScreen(Screen):
    def on_enter(self, *args):
        Clock.schedule_once(lambda _dt: App.get_running_app().go("welcome"), 1.8)

class WelcomeScreen(Screen):
    pass

class ConnectionScreen(Screen):
    status = StringProperty("Saisis l'adresse IP du serveur.")

    def test_connection(self, url):
        app = App.get_running_app()
        app.api.set_base_url(url)
        self.status = "Test de connexion en cours..."
        app.run_async(app.api.health, self._health_done)

    def _health_done(self, result, error):
        self.status = f"Serveur disponible : {result.get('status')}" if not error else f"Connexion impossible : {error}"

    def save_server(self, url):
        try:
            App.get_running_app().api.set_base_url(url)
            self.status = "Adresse enregistrée."
            App.get_running_app().go("dashboard")
        except ValueError as exc:
            self.status = str(exc)

class DashboardScreen(Screen):
    pass

class SendScreen(Screen):
    message = StringProperty("Aucun fichier sélectionné.")
    last_files = ListProperty([])

    def choose_files(self):
        try:
            if platform == "android":
                from plyer import filechooser
                filechooser.open_file(on_selection=self._selected, multiple=True)
            else:
                from tkinter import Tk, filedialog
                root = Tk()
                root.withdraw()
                paths = filedialog.askopenfilenames()
                root.destroy()
                self._selected(list(paths))
        except Exception as exc:
            self.message = f"Sélection impossible : {exc}"

    def _selected(self, paths):
        if not paths:
            return
        self.last_files = list(paths)
        self.message = f"{len(paths)} fichier(s) sélectionné(s)."
        self._upload_next(0)

    def _upload_next(self, index):
        if index >= len(self.last_files):
            self.message = "Tous les fichiers ont été envoyés."
            return
        path = self.last_files[index]
        self.message = f"Envoi {index + 1}/{len(self.last_files)} : {Path(path).name}"
        app = App.get_running_app()
        app.run_async(lambda: app.api.upload(path), lambda result, error: self._upload_done(index, result, error))

    def _upload_done(self, index, result, error):
        if error:
            self.message = f"Transfert interrompu : {error}. Appuie sur Réessayer."
            return
        self.message = f"Envoyé : {result['original_name']}\\nJeton : {result['token']}\\nExpiration : {result['expires_at']}"
        app = App.get_running_app()
        app.run_async(lambda: app.api.qr(result["token"]), lambda data, err: self._show_qr(data, err))
        if index + 1 < len(self.last_files):
            Clock.schedule_once(lambda _dt: self._upload_next(index + 1), 0.2)

    def _show_qr(self, data, error):
        if error:
            self.message += f"\\nQR indisponible : {error}"
            return
        path = Path(App.get_running_app().user_data_dir) / "share_qr.png"
        path.write_bytes(data)
        self.ids.qr_image.source = str(path)
        self.ids.qr_image.reload()

    def retry(self):
        if self.last_files:
            self._upload_next(0)
        else:
            self.message = "Sélectionne d'abord un fichier."

class ReceiveScreen(Screen):
    message = StringProperty("Le téléchargement sera enregistré dans le dossier de l'application.")

    def download(self, token):
        token = token.strip()
        if not token:
            self.message = "Saisis le jeton reçu."
            return
        self.message = "Téléchargement en cours..."
        app = App.get_running_app()
        destination = Path(app.user_data_dir) / "received"
        destination.mkdir(parents=True, exist_ok=True)
        app.run_async(lambda: app.api.download(token, destination), self._download_done)

    def _download_done(self, result, error):
        self.message = f"Fichier reçu : {result}" if not error else f"Échec du téléchargement : {error}"

class SettingsScreen(Screen):
    pass

class QRConnectApp(App):
    title = "QR Connect"
    primary_color = ListProperty([0.118, 0.231, 0.184, 1])
    secondary_color = ListProperty([0.498, 0.549, 0.416, 1])
    background_color = ListProperty([0.961, 0.941, 0.902, 1])
    light_color = ListProperty([0.961, 0.941, 0.902, 1])
    text_color = ListProperty([0.05, 0.05, 0.05, 1])
    muted_color = ListProperty([0.78, 0.78, 0.74, 1])

    def build(self):
        self.api = APIService()
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.sm = Builder.load_string(KV)
        return self.sm

    def go(self, screen):
        self.root.current = screen

    def run_async(self, function, callback):
        future = self.executor.submit(function)
        def done(f):
            try:
                result = f.result()
                error = None
            except Exception as exc:
                result, error = None, str(exc)
            Clock.schedule_once(lambda _dt: callback(result, error), 0)
        future.add_done_callback(done)

    def set_theme(self, mode):
        if mode == "dark":
            self.background_color = [0.07, 0.09, 0.08, 1]
            self.text_color = [0.94, 0.94, 0.90, 1]
            self.light_color = [0.94, 0.94, 0.90, 1]
        else:
            self.background_color = [0.961, 0.941, 0.902, 1]
            self.text_color = [0.05, 0.05, 0.05, 1]
            self.light_color = [0.961, 0.941, 0.902, 1]

    def on_stop(self):
        if hasattr(self, "executor"):
            self.executor.shutdown(wait=False, cancel_futures=True)

if __name__ == "__main__":
    QRConnectApp().run()
