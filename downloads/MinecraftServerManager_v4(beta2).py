"""
Minecraft Server Manager
-------------------------
App GUI (Tkinter) de quan ly nhieu Minecraft server tren may Windows cua ban:
- Tao server Paper moi (tu dong tai jar theo version ban chon)
- Tuy chon tu dong cai Geyser + Floodgate (ho tro Bedrock) va ViaVersion +
  ViaBackwards + ViaRewind (cho phep client tu 1.8 den ban moi nhat ket noi)
- Them server "tuy chinh" tu thu muc co san (modpack Forge/Fabric...)
- Start / Stop tung server, xem console truc tiep, gui lenh vao console
- Chay duoc nhieu server cung luc (moi server 1 process rieng)

Yeu cau: da cai Python 3.9+ (co san tkinter) va da cai Java (JDK) phu hop
voi phien ban Minecraft ban muon chay (vi du Minecraft 1.21.x can Java 21).

Chay app:  python MinecraftServerManager.py
"""
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, colorchooser
import subprocess
import threading
import queue
import json
import os
import sys
import shutil
import stat
import time
import urllib.request
import urllib.error
import socket
import uuid
import hashlib
import customtkinter as ctk
import ipaddress
import psutil
import zipfile

try:
    from PIL import Image, ImageDraw, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


WINDOW_BG = "#18181B"
SIDEBAR_BG = "#111827"
CARD = "#27272A"

TEXT = "#FFFFFF"
TITLE = "#60A5FA"

BUTTON = "#2563EB"
BUTTON_HOVER = "#1D4ED8"

GREEN = "#22C55E"
RED = "#EF4444"
ORANGE = "#F59E0B"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVERS_ROOT = os.path.join(BASE_DIR, "servers")
CONFIG_FILE = os.path.join(BASE_DIR, "servers.json")

APP_SETTINGS_FILE = os.path.join(BASE_DIR, "app_settings.json")

DEFAULT_APP_SETTINGS = {"appearance": "Dark", "language": "Tiếng Việt"}

LANGUAGES = {
    "English": {
        "settings": "Settings", "language": "Language", "appearance": "Appearance",
        "dark": "Dark", "light": "Light", "apply": "Apply", "close": "Close",
        "choose_language": "Choose language", "saved": "Settings saved.",
        "new_server": "➕ New Server", "open_folder": "📂 Open Folder",
        "plugins": "📦 Plugins / Mods", "address": "🌐 Address / Port",
        "advanced": "🛠 Advanced", "delete": "🗑 Delete Server",
        "overview": "🖥 Servers Overview", "settings_button": "☰ Settings",
        "no_server": "🖥 No Server Selected", "start": "▶ Start", "stop": "■ Stop",
        "auto": "🔄 Auto", "no_auto": "⏹ No Auto", "send": "📤 Send",
        "clear": "🗑 Clear", "console": "📜 Live Console", "tab_player": "Player", "tab_server": "Server", "tab_world": "World & Backup",
    },
    "Tiếng Việt": {
        "settings": "Cài đặt", "language": "Ngôn ngữ", "appearance": "Giao diện",
        "dark": "Tối", "light": "Sáng", "apply": "Áp dụng", "close": "Đóng",
        "choose_language": "Chọn ngôn ngữ", "saved": "Đã lưu cài đặt.",
        "new_server": "➕ Server mới", "open_folder": "📂 Mở thư mục",
        "plugins": "📦 Plugins / Mods", "address": "🌐 Địa chỉ / Port",
        "advanced": "🛠 Nâng cao", "delete": "🗑 Xóa Server",
        "overview": "🖥 Tổng quan Server", "settings_button": "☰ Cài đặt",
        "no_server": "🖥 Chưa chọn Server", "start": "▶ Chạy", "stop": "■ Dừng",
        "auto": "🔄 Tự chạy lại", "no_auto": "⏹ Không tự chạy", "send": "📤 Gửi",
        "clear": "🗑 Xóa", "console": "📜 Console trực tiếp", "tab_player": "Người chơi", "tab_server": "Server", "tab_world": "Thế giới & Sao lưu",
    },
    "日本語": {
        "settings": "設定", "language": "言語", "appearance": "外観",
        "dark": "ダーク", "light": "ライト", "apply": "適用", "close": "閉じる",
        "choose_language": "言語を選択", "saved": "設定を保存しました。",
        "new_server": "➕ 新しいサーバー", "open_folder": "📂 フォルダーを開く",
        "plugins": "📦 Plugins / Mods", "address": "🌐 アドレス / Port",
        "advanced": "🛠 詳細設定", "delete": "🗑 サーバー削除",
        "overview": "🖥 サーバー一覧", "settings_button": "☰ 設定",
        "no_server": "🖥 サーバー未選択", "start": "▶ 起動", "stop": "■ 停止",
        "auto": "🔄 自動再起動", "no_auto": "⏹ 自動再起動なし", "send": "📤 送信",
        "clear": "🗑 クリア", "console": "📜 ライブコンソール", "tab_player": "プレイヤー", "tab_server": "サーバー", "tab_world": "ワールド＆バックアップ",
    },
    "Français": {
        "settings":"Paramètres","language":"Langue","appearance":"Apparence","dark":"Sombre","light":"Clair","apply":"Appliquer","close":"Fermer","choose_language":"Choisir la langue","saved":"Paramètres enregistrés.",
        "new_server":"➕ Nouveau serveur","open_folder":"📂 Ouvrir le dossier","plugins":"📦 Plugins / Mods","address":"🌐 Adresse / Port","advanced":"🛠 Avancé","delete":"🗑 Supprimer le serveur","overview":"🖥 Vue d'ensemble des serveurs","settings_button":"☰ Paramètres","no_server":"🖥 Aucun serveur sélectionné","start":"▶ Démarrer","stop":"■ Arrêter","auto":"🔄 Redémarrage auto","no_auto":"⏹ Pas de redémarrage auto","send":"📤 Envoyer","clear":"🗑 Effacer","console":"📜 Console en direct","tab_player":"Joueur","tab_server":"Serveur","tab_world":"Monde & sauvegarde"
    },
    "Español": {
        "settings":"Ajustes","language":"Idioma","appearance":"Apariencia","dark":"Oscuro","light":"Claro","apply":"Aplicar","close":"Cerrar","choose_language":"Elegir idioma","saved":"Ajustes guardados.",
        "new_server":"➕ Nuevo servidor","open_folder":"📂 Abrir carpeta","plugins":"📦 Plugins / Mods","address":"🌐 Dirección / Puerto","advanced":"🛠 Avanzado","delete":"🗑 Eliminar servidor","overview":"🖥 Resumen de servidores","settings_button":"☰ Ajustes","no_server":"🖥 Ningún servidor seleccionado","start":"▶ Iniciar","stop":"■ Detener","auto":"🔄 Reinicio automático","no_auto":"⏹ Sin reinicio automático","send":"📤 Enviar","clear":"🗑 Limpiar","console":"📜 Consola en vivo","tab_player":"Jugador","tab_server":"Servidor","tab_world":"Mundo y copias"
    },
    "한국어": {
        "settings":"설정","language":"언어","appearance":"화면","dark":"다크","light":"라이트","apply":"적용","close":"닫기","choose_language":"언어 선택","saved":"설정이 저장되었습니다.",
        "new_server":"➕ 새 서버","open_folder":"📂 폴더 열기","plugins":"📦 플러그인 / 모드","address":"🌐 주소 / 포트","advanced":"🛠 고급","delete":"🗑 서버 삭제","overview":"🖥 서버 개요","settings_button":"☰ 설정","no_server":"🖥 서버를 선택하지 않음","start":"▶ 시작","stop":"■ 중지","auto":"🔄 자동 재시작","no_auto":"⏹ 자동 재시작 안 함","send":"📤 보내기","clear":"🗑 지우기","console":"📜 실시간 콘솔","tab_player":"플레이어","tab_server":"서버","tab_world":"월드 및 백업"
    },
    "Português": {
        "settings":"Configurações","language":"Idioma","appearance":"Aparência","dark":"Escuro","light":"Claro","apply":"Aplicar","close":"Fechar","choose_language":"Escolher idioma","saved":"Configurações salvas.",
        "new_server":"➕ Novo servidor","open_folder":"📂 Abrir pasta","plugins":"📦 Plugins / Mods","address":"🌐 Endereço / Porta","advanced":"🛠 Avançado","delete":"🗑 Excluir servidor","overview":"🖥 Visão geral dos servidores","settings_button":"☰ Configurações","no_server":"🖥 Nenhum servidor selecionado","start":"▶ Iniciar","stop":"■ Parar","auto":"🔄 Reinício automático","no_auto":"⏹ Sem reinício automático","send":"📤 Enviar","clear":"🗑 Limpar","console":"📜 Console ao vivo","tab_player":"Jogador","tab_server":"Servidor","tab_world":"Mundo e backup"
    },
    "简体中文": {
        "settings": "设置", "language": "语言", "appearance": "外观",
        "dark": "深色", "light": "浅色", "apply": "应用", "close": "关闭",
        "choose_language": "选择语言", "saved": "设置已保存。",
        "new_server": "➕ 新建服务器", "open_folder": "📂 打开文件夹",
        "plugins": "📦 插件 / Mods", "address": "🌐 地址 / 端口",
        "advanced": "🛠 高级", "delete": "🗑 删除服务器",
        "overview": "🖥 服务器总览", "settings_button": "☰ 设置",
        "no_server": "🖥 未选择服务器", "start": "▶ 启动", "stop": "■ 停止",
        "auto": "🔄 自动重启", "no_auto": "⏹ 不自动重启", "send": "📤 发送",
        "clear": "🗑 清除", "console": "📜 实时控制台", "tab_player": "玩家", "tab_server": "服务器", "tab_world": "世界与备份",
    },
}

# Common UI text fallback: keeps older dialogs/buttons translatable even when
# they were created before the localization system was added.
UI_TRANSLATIONS = {
    "Luu": "save", "Lưu": "save", "Dong": "close", "Đóng": "close", "Close": "close",
    "Huy": "cancel", "Hủy": "cancel", "Cancel": "cancel", "Xoa": "delete", "Xóa": "delete",
    "Sua": "edit", "Sửa": "edit", "Chon": "choose", "Chọn": "choose", "Ap dung": "apply", "Áp dụng": "apply",
    "Bat": "enable", "Bật": "enable", "Tat": "disable", "Tắt": "disable", "Khoi dong": "start", "Khởi động": "start",
    "Dừng": "stop", "Dung": "stop", "Xong": "done", "Loi": "error", "Lỗi": "error", "Canh bao": "warning", "Cảnh báo": "warning",
    "Ten server:": "server_name", "Ten nguoi choi:": "player_name", "ID server:": "server_id",
    "Port server (Java):": "java_port", "RAM toi thieu:": "min_ram", "RAM toi da:": "max_ram",
    "Player": "tab_player", "Server": "tab_server", "World & Backup": "tab_world",
    "Người chơi": "tab_player", "Thế giới & Sao lưu": "tab_world",
    "Chon anh va ap dung": "choose_apply_image", "Xoa icon (ve mac dinh)": "remove_icon",
    "Luu the gioi (xuat ra may)": "backup_world", "Tai the gioi (nhap tu may)": "restore_world",
    "Xoa the gioi va tao lai (KHONG THE HOAN TAC)": "reset_world",
    "Cap OP": "op", "Go OP": "deop", "Ban nguoi choi": "ban_player", "Go Ban": "pardon",
    "Ban IP": "ban_ip", "Go Ban IP": "pardon_ip", "Kick": "kick", "Send": "send",
}
UI_TEXT_KEYS = {
    "save":"Lưu", "close":"Đóng", "cancel":"Hủy", "delete":"Xóa", "edit":"Sửa", "choose":"Chọn",
    "apply":"Áp dụng", "enable":"Bật", "disable":"Tắt", "start":"Khởi động", "stop":"Dừng", "done":"Xong",
    "error":"Lỗi", "warning":"Cảnh báo", "server_name":"Tên server:", "player_name":"Tên người chơi:",
    "server_id":"ID server:", "java_port":"Port server (Java):", "min_ram":"RAM tối thiểu:", "max_ram":"RAM tối đa:",
    "choose_apply_image":"Chọn ảnh và áp dụng", "remove_icon":"Xóa icon (về mặc định)", "backup_world":"Lưu thế giới (xuất ra máy)",
    "restore_world":"Tải thế giới (nhập từ máy)", "reset_world":"Xóa thế giới và tạo lại (KHÔNG THỂ HOÀN TÁC)",
    "op":"Cấp OP", "deop":"Gỡ OP", "ban_player":"Ban người chơi", "pardon":"Gỡ Ban", "ban_ip":"Ban IP", "pardon_ip":"Gỡ Ban IP", "kick":"Kick", "send":"Gửi",
}
# Extend the small key set per language. Missing keys intentionally fall back to
# Vietnamese so functionality is never lost.
for _lang, _vals in LANGUAGES.items():
    _vals.update({
        "save": {"English":"Save","Français":"Enregistrer","Español":"Guardar","한국어":"저장","Português":"Salvar","日本語":"保存","简体中文":"保存"}.get(_lang, "Lưu"),
        "cancel": {"English":"Cancel","Français":"Annuler","Español":"Cancelar","한국어":"취소","Português":"Cancelar","日本語":"キャンセル","简体中文":"取消"}.get(_lang, "Hủy"),
        "done": {"English":"Done","Français":"Terminé","Español":"Listo","한국어":"완료","Português":"Concluído","日本語":"完了","简体中文":"完成"}.get(_lang, "Xong"),
        "error": {"English":"Error","Français":"Erreur","Español":"Error","한국어":"오류","Português":"Erro","日本語":"エラー","简体中文":"错误"}.get(_lang, "Lỗi"),
        "warning": {"English":"Warning","Français":"Avertissement","Español":"Advertencia","한국어":"경고","Português":"Aviso","日本語":"警告","简体中文":"警告"}.get(_lang, "Cảnh báo"),
        "save_button": _vals.get("save", "Lưu"),
    })

def _localized_widget_text(widget, language=None):
    language = language or APP_SETTINGS["language"]
    try:
        text = widget.cget("text")
    except Exception:
        text = None
    if not text:
        return
    key = UI_TRANSLATIONS.get(str(text))
    if not key:
        # Recognize any language's value and map it back to its canonical key.
        for _k, _langvals in LANGUAGES.items():
            for _key, _value in _langvals.items():
                if _value == str(text):
                    key = _key
                    break
            if key: break
    if key:
        val = LANGUAGES.get(language, LANGUAGES["Tiếng Việt"]).get(key)
        if val:
            try: widget.configure(text=val)
            except Exception: pass

def localize_tree(root, language=None):
    """Translate buttons/labels/tabs across every open dialog, including legacy UI."""
    language = language or APP_SETTINGS["language"]
    try: _localized_widget_text(root, language)
    except Exception: pass
    try:
        for child in root.winfo_children(): localize_tree(child, language)
    except Exception: pass

def load_app_settings():
    settings = dict(DEFAULT_APP_SETTINGS)
    try:
        with open(APP_SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            settings.update(data)
    except Exception:
        pass
    if settings.get("appearance") not in ("Dark", "Light"):
        settings["appearance"] = "Dark"
    if settings.get("language") not in LANGUAGES:
        settings["language"] = "Tiếng Việt"
    return settings

def save_app_settings(settings):
    with open(APP_SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

APP_SETTINGS = load_app_settings()
ctk.set_appearance_mode(APP_SETTINGS["appearance"])

def tr(key, language=None):
    language = language or APP_SETTINGS["language"]
    return LANGUAGES.get(language, LANGUAGES["Tiếng Việt"]).get(
        key, LANGUAGES["Tiếng Việt"].get(key, key)
    )

def theme_palette(mode=None):
    mode = mode or APP_SETTINGS["appearance"]
    if mode == "Light":
        return {
            "window": "#F4F4F5", "surface": "#FFFFFF", "surface2": "#E4E4E7",
            "text": "#18181B", "muted": "#52525B", "border": "#D4D4D8",
            "entry": "#FFFFFF", "canvas": "#F4F4F5", "console": "#111827",
            "console_text": "#86EFAC", "button": "#2563EB", "button_hover": "#1D4ED8",
        }
    return {
        "window": "#18181B", "surface": "#27272A", "surface2": "#3F3F46",
        "text": "#FFFFFF", "muted": "#A1A1AA", "border": "#3F3F46",
        "entry": "#18181B", "canvas": "#18181B", "console": "#0F172A",
        "console_text": "#22C55E", "button": "#2563EB", "button_hover": "#1D4ED8",
    }

def configure_ttk_theme(master, mode=None):
    p = theme_palette(mode)
    style = ttk.Style(master)
    try:
        style.theme_use("clam")
    except Exception:
        pass
    style.configure("TFrame", background=p["window"])
    style.configure("TLabel", background=p["window"], foreground=p["text"])
    style.configure("TButton", background=p["surface"], foreground=p["text"],
                    bordercolor=p["border"], padding=(10, 7))
    style.configure("TCheckbutton", background=p["window"], foreground=p["text"])
    style.configure("TRadiobutton", background=p["window"], foreground=p["text"])
    style.configure("TEntry", fieldbackground=p["entry"], foreground=p["text"],
                    insertcolor=p["text"], bordercolor=p["border"])
    style.configure("TCombobox", fieldbackground=p["entry"], foreground=p["text"],
                    background=p["surface"], arrowcolor=p["text"])
    style.configure("TSpinbox", fieldbackground=p["entry"], foreground=p["text"],
                    background=p["surface"], arrowcolor=p["text"])
    style.configure("TLabelframe", background=p["surface"], foreground=p["text"],
                    bordercolor=p["border"])
    style.configure("TLabelframe.Label", background=p["surface"], foreground="#60A5FA")
    style.configure("TNotebook", background=p["window"])
    style.configure("TNotebook.Tab", background=p["surface"], foreground=p["muted"],
                    padding=(16, 9))
    style.configure("TSeparator", background=p["border"])
    style.map("TButton", background=[("active", p["button"]), ("pressed", p["button_hover"])],
              foreground=[("active", "#FFFFFF")])
    style.map("TNotebook.Tab", background=[("selected", p["button"])],
              foreground=[("selected", "#FFFFFF")])
    return p

def _theme_tk_tree(widget, mode=None):
    p = theme_palette(mode)
    try:
        if isinstance(widget, (tk.Toplevel, tk.Frame, tk.LabelFrame)):
            widget.configure(bg=p["window"])
        elif isinstance(widget, tk.Label):
            widget.configure(bg=p["window"], fg=p["text"])
        elif isinstance(widget, tk.Entry):
            widget.configure(bg=p["entry"], fg=p["text"],
                             insertbackground=p["text"],
                             highlightbackground=p["border"],
                             highlightcolor="#60A5FA")
        elif isinstance(widget, tk.Text):
            font_text = str(widget.cget("font"))
            is_console = "Consolas" in font_text
            widget.configure(bg=p["console"] if is_console else p["entry"],
                             fg=p["console_text"] if is_console else p["text"],
                             insertbackground=p["text"], selectbackground=p["button"],
                             selectforeground="#FFFFFF")
        elif isinstance(widget, tk.Listbox):
            widget.configure(bg=p["entry"], fg=p["text"],
                             selectbackground=p["button"], selectforeground="#FFFFFF")
        elif isinstance(widget, tk.Canvas):
            widget.configure(bg=p["canvas"])
    except Exception:
        pass
    for child in widget.winfo_children():
        _theme_tk_tree(child, mode)

def apply_secondary_theme(window, mode=None):
    p = configure_ttk_theme(window, mode)
    try:
        window.configure(bg=p["window"])
    except Exception:
        pass
    _theme_tk_tree(window, mode)

class AppSettingsDialog(ctk.CTkToplevel):
    def __init__(self, master, app, language_only=False):
        super().__init__(master)
        self.app = app
        self.language_only = language_only
        self.title(tr("settings"))
        self.geometry("430x360")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        p = theme_palette()
        self.configure(fg_color=p["window"])

        card = ctk.CTkFrame(self, fg_color=p["surface"], corner_radius=14)
        card.pack(fill="both", expand=True, padx=18, pady=18)
        ctk.CTkLabel(card,
                     text="☰ " + tr("settings"),
                     font=("Segoe UI", 20, "bold"), text_color="#60A5FA").pack(
                         anchor="w", padx=22, pady=(20, 12))

        ctk.CTkLabel(card, text=tr("choose_language"), text_color=p["text"],
                     font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=22, pady=(4, 5))
        self.language_var = tk.StringVar(value=APP_SETTINGS["language"])
        self.language_menu = ctk.CTkOptionMenu(
            card, values=list(LANGUAGES.keys()), variable=self.language_var, width=330,
            fg_color=p["surface2"], button_color=p["button"], button_hover_color=p["button_hover"])
        self.language_menu.pack(padx=22, pady=(0, 12))

        ctk.CTkLabel(card, text=tr("appearance"), text_color=p["text"],
                     font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=22, pady=(3, 5))
        self.appearance_var = tk.StringVar(value=APP_SETTINGS["appearance"])
        self.appearance_menu = ctk.CTkOptionMenu(
            card, values=["Dark", "Light"], variable=self.appearance_var, width=330,
            fg_color=p["surface2"], button_color=p["button"],
            button_hover_color=p["button_hover"])
        self.appearance_menu.pack(padx=22, pady=(0, 14))

        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.pack(fill="x", padx=22, pady=(4, 18))
        ctk.CTkButton(buttons, text=tr("apply"), width=140,
                      fg_color=p["button"], hover_color=p["button_hover"],
                      command=self._apply).pack(side="left")
        ctk.CTkButton(buttons, text=tr("close"), width=100,
                      fg_color=p["surface2"], hover_color=p["border"],
                      command=self.destroy).pack(side="right")

    def _preview_appearance(self, value):
        # Do not change the application theme until the user presses Apply.
        # The dropdown only changes the pending preference.
        return

    def _apply(self):
        appearance = self.appearance_var.get()
        self.app.apply_preferences(appearance, self.language_var.get())
        self.destroy()

TUNNEL_ROOT = os.path.join(BASE_DIR, "tunnel")
PLAYIT_EXE = os.path.join(TUNNEL_ROOT, "playit.exe")

# =========================
# PUBLIC TUNNEL
# =========================

TUNNEL_ROOT = os.path.expandvars(r"%LOCALAPPDATA%/playit_gg/bin")

PLAYIT_EXE = os.path.join(TUNNEL_ROOT, "playit.exe")

PAPER_API = "https://fill.papermc.io/v3/projects/paper"
USER_AGENT = "MinecraftServerManager-App/1.0 (self-hosted local tool; contact: local-user@example.com)"
GEYSER_URL = "https://download.geysermc.org/v2/projects/geyser/versions/latest/builds/latest/downloads/spigot"
FLOODGATE_URL = "https://download.geysermc.org/v2/projects/floodgate/versions/latest/builds/latest/downloads/spigot"
MODRINTH_VERSION_API = "https://api.modrinth.com/v2/project/{slug}/version"

os.makedirs(SERVERS_ROOT, exist_ok=True)


def get_lan_ip():
    """Lay dia chi IP noi bo (LAN) cua may, de nguoi khac cung mang vao choi."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "khong xac dinh"
    finally:
        s.close()
    return ip


def set_server_property(server_path, key, value):
    """Ghi/cap nhat 1 dong key=value trong server.properties."""
    props_path = os.path.join(server_path, "server.properties")
    lines = []
    found = False
    if os.path.exists(props_path):
        with open(props_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                found = True
                break
    if not found:
        lines.append(f"{key}={value}\n")
    with open(props_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def get_server_property(server_path, key, default=""):
    props_path = os.path.join(server_path, "server.properties")
    if not os.path.exists(props_path):
        return default
    with open(props_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith(f"{key}="):
                return line.strip().split("=", 1)[1]
    return default


def update_server_port(server_path, new_port):
    set_server_property(server_path, "server-port", new_port)


def offline_uuid(name):
    """Tinh UUID offline giong cach Minecraft tinh cho tai khoan cracked
    (dua tren 'OfflinePlayer:<ten>'), de ghi vao ops.json/banned-players.json."""
    data = bytearray(hashlib.md5(f"OfflinePlayer:{name}".encode("utf-8")).digest())
    data[6] = (data[6] & 0x0F) | 0x30
    data[8] = (data[8] & 0x3F) | 0x80
    return str(uuid.UUID(bytes=bytes(data)))


def _load_json_list(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def _save_json_list(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def add_op_offline(server_path, name):
    ops_path = os.path.join(server_path, "ops.json")
    ops = _load_json_list(ops_path)
    if any(o.get("name", "").lower() == name.lower() for o in ops):
        return
    ops.append({
        "uuid": offline_uuid(name),
        "name": name,
        "level": 4,
        "bypassesPlayerLimit": False,
    })
    _save_json_list(ops_path, ops)


def remove_op_offline(server_path, name):
    ops_path = os.path.join(server_path, "ops.json")
    ops = _load_json_list(ops_path)
    ops = [o for o in ops if o.get("name", "").lower() != name.lower()]
    _save_json_list(ops_path, ops)


def is_pid_alive(pid):
    """Kiem tra 1 tien trinh (theo PID) co con dang chay tren Windows khong."""
    if not pid:
        return False
    try:
        result = subprocess.run(
            ["tasklist", "/fi", f"PID eq {pid}"],
            capture_output=True, text=True, timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
        )
        return str(pid) in result.stdout
    except Exception:
        return False


def force_kill_pid(pid):
    try:
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/F", "/T"],
            capture_output=True, text=True, timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
        )
        return True
    except Exception:
        return False


def set_player_flag(entry, player, flag, value):
    """Ghi nhan trang thai (op/ban/banip/always_op) cua 1 nguoi choi vao entry server."""
    players = entry.setdefault("players", {})
    p = players.setdefault(player, {"op": False, "ban": False, "banip": False, "always_op": False})
    p[flag] = value


def get_status_color(app, name):
    """Tra ve (mau, mo ta) trang thai cua 1 server: xanh la=dang chay,
    vang=dang khoi dong, do=co van de, den=khong khoi dong."""
    entry = app.servers.get(name, {})
    rs = app.running.get(name)
    if rs and rs.is_running():
        if rs.state == "starting":
            return "#f1c40f", "dang khoi dong"
        return "#2ecc71", "dang hoat dong"
    if rs and not rs.is_running() and rs.state == "error":
        return "#e74c3c", "co van de"
    pid = entry.get("pid")
    if pid and is_pid_alive(pid):
        return "#2ecc71", "dang hoat dong (nen)"
    return "#555555", "khong khoi dong"


# ---------------------------------------------------------------------------
# Luu / doc danh sach server
# ---------------------------------------------------------------------------
def load_servers():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_servers(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _force_remove_readonly(func, path, exc_info):
    """Ho tro shutil.rmtree: go co read-only truoc khi xoa (loi hay gap tren Windows)."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


def safe_rmtree(path, retries=6, delay=0.5):
    """Xoa thu muc, thu lai vai lan neu file dang bi khoa tam thoi
    (vi du Java/antivirus chua nha file ngay sau khi server vua tat).
    Tra ve True neu xoa thanh cong (hoac thu muc khong con ton tai)."""
    if not os.path.exists(path):
        return True
    for _ in range(retries):
        try:
            shutil.rmtree(path, onerror=_force_remove_readonly)
        except Exception:
            pass
        if not os.path.exists(path):
            return True
        time.sleep(delay)
    return not os.path.exists(path)


# ---------------------------------------------------------------------------
# Ham tai file tu mang
# ---------------------------------------------------------------------------
def http_get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def download_file(url, dest_path, log=None):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    if log:
        log(f"Dang tai: {url}")
    with urllib.request.urlopen(req, timeout=60) as r, open(dest_path, "wb") as out:
        shutil.copyfileobj(r, out)
    if log:
        log(f"Da luu: {dest_path}")


def get_paper_versions():
    """Tra ve danh sach version Minecraft ma Paper ho tro, moi nhat len dau."""
    data = http_get_json(PAPER_API)
    versions_by_group = data.get("versions", {})
    flat = []
    for group_versions in versions_by_group.values():
        flat.extend(group_versions)
    return flat


def get_latest_paper_build(version):
    """Tra ve (download_url, ten_file_jar) cho build on dinh (STABLE) moi nhat.
    Neu khong co build STABLE, lay build moi nhat bat ke channel nao."""
    data = http_get_json(f"{PAPER_API}/versions/{version}/builds")
    if isinstance(data, dict) and data.get("ok") is False:
        raise RuntimeError(data.get("message", "Loi khong xac dinh tu PaperMC API"))
    if not data:
        raise RuntimeError("Khong tim thay build nao cho version nay")

    stable_builds = [b for b in data if b.get("channel") == "STABLE"]
    chosen = stable_builds[0] if stable_builds else data[0]

    download_info = chosen.get("downloads", {}).get("server:default")
    if not download_info:
        raise RuntimeError("Build nay khong co file server de tai")

    return download_info["url"], download_info["name"]


def download_paper(version, dest_folder, log=None):
    url, jar_name = get_latest_paper_build(version)
    dest_path = os.path.join(dest_folder, "server.jar")
    download_file(url, dest_path, log=log)
    return "server.jar"


def download_modrinth_latest(slug, dest_folder, log=None):
    data = http_get_json(MODRINTH_VERSION_API.format(slug=slug))
    if not data:
        raise RuntimeError(f"Khong tim thay ban tai ve cho {slug}")
    latest = data[0]
    file_info = latest["files"][0]
    url = file_info["url"]
    filename = file_info["filename"]
    dest_path = os.path.join(dest_folder, filename)
    download_file(url, dest_path, log=log)


def install_geyser_floodgate(plugins_dir, log=None):
    download_file(GEYSER_URL, os.path.join(plugins_dir, "Geyser-Spigot.jar"), log=log)
    download_file(FLOODGATE_URL, os.path.join(plugins_dir, "floodgate-spigot.jar"), log=log)


def install_via_suite(plugins_dir, log=None):
    for slug in ("viaversion", "viabackwards", "viarewind"):
        try:
            download_modrinth_latest(slug, plugins_dir, log=log)
        except Exception as e:
            if log:
                log(f"Loi khi tai {slug}: {e}")


# ---------------------------------------------------------------------------
# Quan ly 1 tien trinh server dang chay
# ---------------------------------------------------------------------------

# =========================
# RESPONSIVE BUTTON HELPERS
# =========================
def auto_resize_button(button, min_width=90, padding=30):
    """Tu dong chinh kich thuoc nut theo noi dung."""
    try:
        value = str(button.cget("text") or "")
        font = button.cget("font")
        if font is not None and hasattr(font, "measure"):
            width = font.measure(value) + padding
        else:
            width = len(value) * 8 + padding
        button.configure(width=max(min_width, int(width)))
    except Exception:
        pass


def auto_resize_buttons(parent, min_width=90, padding=30):
    """Tu dong resize cac CTkButton trong mot frame."""
    try:
        for child in parent.winfo_children():
            if isinstance(child, ctk.CTkButton):
                auto_resize_button(child, min_width, padding)
            elif hasattr(child, "winfo_children"):
                auto_resize_buttons(child, min_width, padding)
    except Exception:
        pass


class RunningServer:
    def __init__(self, name, proc):
        self.name = name
        self.proc = proc
        self.log_queue = queue.Queue()
        self.state = "starting"  # starting | running | stopped | error
        self.intentional_stop = False
        self.auto_restart = False
        self.restart_scheduled = False
        self.reader_thread = threading.Thread(target=self._read_output, daemon=True)
        self.reader_thread.start()

    def _read_output(self):
        try:
            for line in iter(self.proc.stdout.readline, ""):
                if line == "" and self.proc.poll() is not None:
                    break
                if line:
                    stripped = line.rstrip("\n")
                    if self.state == "starting" and ")! For help" in stripped and stripped.strip().startswith("["):
                        self.state = "running"
                    self.log_queue.put(stripped)
        except Exception as e:
            self.log_queue.put(f"[Loi doc output] {e}")
        returncode = self.proc.poll()
        if self.intentional_stop:
            self.state = "stopped"
        elif returncode not in (0, None):
            self.state = "error"
        else:
            self.state = "stopped"
        self.log_queue.put("__PROCESS_ENDED__")

    def send_command(self, cmd):
        if self.proc.poll() is None and self.proc.stdin:
            try:
                self.proc.stdin.write(cmd + "\n")
                self.proc.stdin.flush()
            except Exception:
                pass

    def is_running(self):
        return self.proc.poll() is None

    def stop(self):
        self.intentional_stop = True
        self.send_command("stop")




# ---------------------------------------------------------------------------
# Dialog: Tao server moi
# ---------------------------------------------------------------------------
class NewServerDialog(tk.Toplevel):
    def __init__(self, master, on_created):
        super().__init__(master)
        apply_secondary_theme(self)
        self.title("Tao server moi")
        self.geometry("480x520")
        self.resizable(False, False)
        self.on_created = on_created
        self.transient(master)
        self.grab_set()

        pad = {"padx": 10, "pady": 6}

        # Ten server
        ttk.Label(self, text="Ten server:").grid(row=0, column=0, sticky="w", **pad)
        self.name_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.name_var, width=35).grid(row=0, column=1, **pad)

        # Loai server
        ttk.Label(self, text="Loai server:").grid(row=1, column=0, sticky="w", **pad)
        self.type_var = tk.StringVar(value="paper")
        type_frame = ttk.Frame(self)
        type_frame.grid(row=1, column=1, sticky="w", **pad)
        ttk.Radiobutton(type_frame, text="Paper (tu dong tai ve)", variable=self.type_var,
                         value="paper", command=self._on_type_change).pack(anchor="w")
        ttk.Radiobutton(type_frame, text="Tuy chinh / Modpack co san", variable=self.type_var,
                         value="custom", command=self._on_type_change).pack(anchor="w")

        # --- Khung Paper ---
        self.paper_frame = ttk.LabelFrame(self, text="Cau hinh Paper")
        self.paper_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=6)

        ttk.Label(self.paper_frame, text="Phien ban Minecraft:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.version_var = tk.StringVar()
        self.version_combo = ttk.Combobox(self.paper_frame, textvariable=self.version_var,
                                           state="readonly", width=20)
        self.version_combo.grid(row=0, column=1, padx=8, pady=6)
        ttk.Button(self.paper_frame, text="Tai danh sach version",
                   command=self._load_versions).grid(row=0, column=2, padx=8, pady=6)

        self.geyser_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.paper_frame, text="Tu cai Geyser + Floodgate (ho tro nguoi choi Bedrock)",
                         variable=self.geyser_var).grid(row=1, column=0, columnspan=3, sticky="w", padx=8)

        self.via_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.paper_frame, text="Tu cai ViaVersion/ViaBackwards/ViaRewind (ho tro client tu ban cu)",
                         variable=self.via_var).grid(row=2, column=0, columnspan=3, sticky="w", padx=8, pady=(0, 8))

        # --- Khung Custom ---
        self.custom_frame = ttk.LabelFrame(self, text="Server tuy chinh / Modpack")
        self.custom_path_var = tk.StringVar()
        ttk.Label(self.custom_frame, text="Thu muc server co san:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(self.custom_frame, textvariable=self.custom_path_var, width=28).grid(row=0, column=1, padx=4)
        ttk.Button(self.custom_frame, text="Chon...", command=self._browse_folder).grid(row=0, column=2, padx=4)

        ttk.Label(self.custom_frame, text="File khoi dong (.jar hoac .bat):").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.custom_launch_var = tk.StringVar()
        ttk.Entry(self.custom_frame, textvariable=self.custom_launch_var, width=28).grid(row=1, column=1, padx=4)
        ttk.Button(self.custom_frame, text="Chon...", command=self._browse_launch_file).grid(row=1, column=2, padx=4)

        # RAM + port
        common_frame = ttk.LabelFrame(self, text="Tai nguyen")
        common_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=6)

        ttk.Label(common_frame, text="RAM toi thieu (vi du 1G):").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        self.xms_var = tk.StringVar(value="1G")
        ttk.Entry(common_frame, textvariable=self.xms_var, width=10).grid(row=0, column=1, sticky="w", padx=8)

        ttk.Label(common_frame, text="RAM toi da (vi du 4G):").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        self.xmx_var = tk.StringVar(value="4G")
        ttk.Entry(common_frame, textvariable=self.xmx_var, width=10).grid(row=1, column=1, sticky="w", padx=8)

        ttk.Label(common_frame, text="Port server (Java, moi server 1 port khac nhau):").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        self.port_var = tk.StringVar(value="25565")
        ttk.Entry(common_frame, textvariable=self.port_var, width=10).grid(row=2, column=1, sticky="w", padx=8)

        # EULA
        self.eula_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self, text="Toi dong y voi Minecraft EULA (aka.ms/MinecraftEULA)",
                         variable=self.eula_var).grid(row=5, column=0, columnspan=2, sticky="w", padx=10)

        # Status + nut tao
        self.status_var = tk.StringVar(value="")
        ttk.Label(self, textvariable=self.status_var, foreground="blue").grid(row=6, column=0, columnspan=2, padx=10, pady=6)

        ttk.Button(self, text="Tao server", command=self._create).grid(row=7, column=0, columnspan=2, pady=10)

        self._on_type_change()

    def _on_type_change(self):
        if self.type_var.get() == "paper":
            self.paper_frame.grid()
            self.custom_frame.grid_remove()
        else:
            self.paper_frame.grid_remove()
            self.custom_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=6)

    def _load_versions(self):
        def worker():
            try:
                self.status_var.set("Dang tai danh sach phien ban...")
                versions = get_paper_versions()
                self.version_combo["values"] = versions
                if versions:
                    self.version_var.set(versions[0])
                self.status_var.set("Da tai xong danh sach phien ban.")
            except Exception as e:
                self.status_var.set(f"Loi: {e}")
        threading.Thread(target=worker, daemon=True).start()

    def _browse_folder(self):
        path = filedialog.askdirectory(title="Chon thu muc server co san")
        if path:
            self.custom_path_var.set(path)

    def _browse_launch_file(self):
        path = filedialog.askopenfilename(title="Chon file khoi dong",
                                           filetypes=[("Jar/Bat", "*.jar;*.bat"), ("Tat ca", "*.*")])
        if path:
            self.custom_launch_var.set(path)

    def _create(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Loi", "Vui long nhap ten server")
            return
        if not self.eula_var.get():
            messagebox.showerror("Loi", "Ban can dong y Minecraft EULA de tiep tuc")
            return

        server_dir = os.path.join(SERVERS_ROOT, name)
        if os.path.exists(server_dir):
            already_tracked = name in getattr(self.master, "servers", {})
            if not already_tracked:
                # Thu muc con sot lai tu lan xoa truoc bi ket file, nhung server
                # nay khong con trong danh sach -> tu dong don dep roi tiep tuc.
                safe_rmtree(server_dir)
            if os.path.exists(server_dir):
                messagebox.showerror(
                    "Loi",
                    "Da ton tai server voi ten nay (thu muc van con tren o dia va dang bi khoa).\n"
                    "Hay doi it phut roi thu lai, hoac doi ten khac / tu xoa thu muc thu cong:\n"
                    f"{server_dir}"
                )
                return

        server_type = self.type_var.get()

        if server_type == "custom":
            src = self.custom_path_var.get().strip()
            launch_file = self.custom_launch_var.get().strip()
            if not src or not os.path.isdir(src):
                messagebox.showerror("Loi", "Vui long chon thu muc server hop le")
                return
            if not launch_file or not os.path.isfile(launch_file):
                messagebox.showerror("Loi", "Vui long chon file khoi dong (.jar hoac .bat) hop le")
                return

            entry = {
                "type": "custom",
                "path": src,
                "launch_file": os.path.relpath(launch_file, src) if launch_file.startswith(src) else launch_file,
                "xms": self.xms_var.get().strip() or "1G",
                "xmx": self.xmx_var.get().strip() or "4G",
                "port": self.port_var.get().strip() or "25565",
            }
            self._finish_create(name, entry, server_dir=src, is_new_folder=False)
            return

        # server_type == paper
        version = self.version_var.get().strip()
        if not version:
            messagebox.showerror("Loi", "Vui long tai va chon phien ban Minecraft")
            return

        os.makedirs(server_dir, exist_ok=True)
        plugins_dir = os.path.join(server_dir, "plugins")
        os.makedirs(plugins_dir, exist_ok=True)

        def log(msg):
            self.status_var.set(msg)

        def worker():
            try:
                log("Dang tai Paper server.jar...")
                jar_name = download_paper(version, server_dir, log=log)

                if self.geyser_var.get():
                    log("Dang cai Geyser + Floodgate...")
                    install_geyser_floodgate(plugins_dir, log=log)

                if self.via_var.get():
                    log("Dang cai ViaVersion / ViaBackwards / ViaRewind...")
                    install_via_suite(plugins_dir, log=log)

                # Ghi eula.txt
                with open(os.path.join(server_dir, "eula.txt"), "w", encoding="utf-8") as f:
                    f.write("eula=true\n")

                # Ghi server.properties toi thieu (port). Paper se tu dien phan con lai.
                props_path = os.path.join(server_dir, "server.properties")
                if not os.path.exists(props_path):
                    with open(props_path, "w", encoding="utf-8") as f:
                        f.write(f"server-port={self.port_var.get().strip() or '25565'}\n")
                        f.write("online-mode=true\n")

                entry = {
                    "type": "paper",
                    "path": server_dir,
                    "jar": jar_name,
                    "version": version,
                    "xms": self.xms_var.get().strip() or "1G",
                    "xmx": self.xmx_var.get().strip() or "4G",
                    "port": self.port_var.get().strip() or "25565",
                }
                self.after(0, lambda: self._finish_create(name, entry, server_dir, is_new_folder=True))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Loi", f"Khong the tao server: {e}"))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_create(self, name, entry, server_dir, is_new_folder):
        self.on_created(name, entry)
        self.status_var.set("Da tao server thanh cong!")
        messagebox.showinfo("Thanh cong", f"Da tao server '{name}'.\nThu muc: {server_dir}")
        self.destroy()


# ---------------------------------------------------------------------------
# Dialog: Sua dia chi (port) / RAM cua server da tao
# ---------------------------------------------------------------------------
class EditServerDialog(tk.Toplevel):
    def __init__(self, master, name, entry, on_saved):
        super().__init__(master)
        apply_secondary_theme(self)
        self.title(f"Sua cau hinh: {name}")
        self.geometry("400x260")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.name = name
        self.entry = entry
        self.on_saved = on_saved

        pad = {"padx": 10, "pady": 8}

        ttk.Label(self, text=f"Server: {name}", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", **pad)

        ttk.Label(self, text="Port server (Java):").grid(row=1, column=0, sticky="w", **pad)
        self.port_var = tk.StringVar(value=str(entry.get("port", "25565")))
        ttk.Entry(self, textvariable=self.port_var, width=15).grid(row=1, column=1, sticky="w", **pad)

        ttk.Label(self, text="RAM toi thieu:").grid(row=2, column=0, sticky="w", **pad)
        self.xms_var = tk.StringVar(value=entry.get("xms", "1G"))
        ttk.Entry(self, textvariable=self.xms_var, width=15).grid(row=2, column=1, sticky="w", **pad)

        ttk.Label(self, text="RAM toi da:").grid(row=3, column=0, sticky="w", **pad)
        self.xmx_var = tk.StringVar(value=entry.get("xmx", "4G"))
        ttk.Entry(self, textvariable=self.xmx_var, width=15).grid(row=3, column=1, sticky="w", **pad)

        note = ("Luu y: doi port se duoc ap dung sau khi ban Stop va Start lai server.\n"
                "Neu server dang chay, hay Stop truoc khi sua.")
        ttk.Label(self, text=note, wraplength=360, foreground="gray").grid(
            row=4, column=0, columnspan=2, sticky="w", padx=10, pady=(4, 8))

        ttk.Button(self, text="Luu", command=self._save).grid(row=5, column=0, columnspan=2, pady=8)

    def _save(self):
        port = self.port_var.get().strip()
        xms = self.xms_var.get().strip() or "1G"
        xmx = self.xmx_var.get().strip() or "4G"

        if not port.isdigit() or not (1 <= int(port) <= 65535):
            messagebox.showerror("Loi", "Port khong hop le (phai la so tu 1 den 65535)")
            return

        self.entry["port"] = port
        self.entry["xms"] = xms
        self.entry["xmx"] = xmx

        if self.entry.get("type") == "paper":
            try:
                update_server_port(self.entry["path"], port)
            except Exception as e:
                messagebox.showwarning("Canh bao", f"Khong the cap nhat server.properties: {e}")

        self.on_saved(self.name, self.entry)
        messagebox.showinfo("Thanh cong", "Da luu cau hinh. Hay Stop va Start lai server de ap dung.")
        self.destroy()


# ---------------------------------------------------------------------------
# Dialog: Quan ly nang cao - Tab Nguoi choi + Tab May chu
# ---------------------------------------------------------------------------
class ServerAdminDialog(tk.Toplevel):
    def __init__(self, master, name, entry, get_running, app=None):
        super().__init__(master)
        apply_secondary_theme(self)
        self.title(f"Advanced - {name}")
        self.geometry("920x760")
        self.minsize(820, 680)
        self.configure(bg=WINDOW_BG)
        self.transient(master)
        self.grab_set()
        self.name = name
        self.entry = entry
        self.get_running = get_running
        self.app = app

        # Modern dark ttk theme chi ap dung cho cua so Advanced.
        # Main window cua ban duoc giu nguyen.
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Advanced.TFrame", background=WINDOW_BG)
        style.configure("Advanced.TLabelframe", background=CARD, foreground=TEXT, bordercolor="#3F3F46", relief="solid")
        style.configure("Advanced.TLabelframe.Label", background=CARD, foreground=TITLE, font=("Segoe UI", 10, "bold"))
        style.configure("Advanced.TLabel", background=WINDOW_BG, foreground="#E5E7EB", font=("Segoe UI", 10))
        style.configure("Advanced.Bold.TLabel", background=WINDOW_BG, foreground=TEXT, font=("Segoe UI", 10, "bold"))
        style.configure("Advanced.TButton", background="#27272A", foreground=TEXT, bordercolor="#3F3F46", padding=(12, 7), font=("Segoe UI", 9, "bold"))
        style.map("Advanced.TButton", background=[("active", "#3B82F6"), ("pressed", "#2563EB")], foreground=[("active", "#FFFFFF")])
        style.configure("Advanced.TCheckbutton", background=CARD, foreground="#E5E7EB", font=("Segoe UI", 9))
        style.map("Advanced.TCheckbutton", background=[("active", CARD)], foreground=[("active", TEXT)])
        style.configure("Advanced.TRadiobutton", background=WINDOW_BG, foreground="#E5E7EB", font=("Segoe UI", 9))
        style.map("Advanced.TRadiobutton", background=[("active", WINDOW_BG)], foreground=[("active", TEXT)])
        style.configure("Advanced.TEntry", fieldbackground="#18181B", foreground=TEXT, insertcolor=TEXT, bordercolor="#3F3F46", padding=7)
        style.configure("Advanced.TCombobox", fieldbackground="#18181B", foreground=TEXT, background="#27272A", arrowcolor=TEXT, padding=6)
        style.configure("Advanced.TNotebook", background=WINDOW_BG, borderwidth=0)
        style.configure("Advanced.TNotebook.Tab", background="#27272A", foreground="#A1A1AA", padding=(18, 10), font=("Segoe UI", 9, "bold"))
        style.map("Advanced.TNotebook.Tab", background=[("selected", BUTTON)], foreground=[("selected", "#FFFFFF")])
        style.configure("Advanced.Vertical.TScrollbar", background="#27272A", troughcolor="#18181B", arrowcolor="#A1A1AA")

        # Header moi: gon, hien dai, nhin ro server nao dang duoc quan ly.
        header = ctk.CTkFrame(self, fg_color="#111827", corner_radius=14)
        header.pack(fill="x", padx=14, pady=(14, 8))
        ctk.CTkLabel(header, text="⚙  ADVANCED SERVER CONTROL", text_color=TITLE,
                     font=("Segoe UI", 17, "bold")).pack(side="left", padx=18, pady=14)
        ctk.CTkLabel(header, text=name, text_color="#E5E7EB",
                     font=("Segoe UI", 12, "bold")).pack(side="left", padx=8)
        ctk.CTkButton(header, text="Close", width=90, height=34, corner_radius=9,
                      fg_color="#27272A", hover_color="#3F3F46", command=self.destroy).pack(side="right", padx=14)

        notebook = ttk.Notebook(self, style="Advanced.TNotebook")
        notebook.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self.player_tab = ttk.Frame(notebook, style="Advanced.TFrame")
        self.server_tab = ttk.Frame(notebook, style="Advanced.TFrame")
        self.env_tab = ttk.Frame(notebook, style="Advanced.TFrame")
        notebook.add(self.player_tab, text="  " + tr("tab_player") + "  ")
        notebook.add(self.server_tab, text="  " + tr("tab_server") + "  ")
        notebook.add(self.env_tab, text="  " + tr("tab_world") + "  ")
        self._advanced_notebook = notebook
        notebook.bind("<<NotebookTabChanged>>", self._on_advanced_tab_changed)
        self._on_advanced_tab_changed()

        self._build_player_tab()
        self._build_server_tab()
        self._build_env_tab()

    def _on_advanced_tab_changed(self, event=None):
        try:
            idx = self._advanced_notebook.index(self._advanced_notebook.select())
            accent = [GREEN, BUTTON, ORANGE][min(idx, 2)]
            style = ttk.Style(self)
            style.configure("Advanced.TNotebook.Tab", background=CARD, foreground="#A1A1AA", padding=(18, 10), font=("Segoe UI", 9, "bold"))
            style.map("Advanced.TNotebook.Tab", background=[("selected", accent)], foreground=[("selected", "#FFFFFF")])
        except Exception:
            pass

    def refresh_language(self):
        try:
            self._advanced_notebook.tab(0, text="  " + tr("tab_player") + "  ")
            self._advanced_notebook.tab(1, text="  " + tr("tab_server") + "  ")
            self._advanced_notebook.tab(2, text="  " + tr("tab_world") + "  ")
            self._on_advanced_tab_changed()
            localize_tree(self, APP_SETTINGS["language"])
        except Exception:
            pass

    def _server_path(self):
        return self.entry["path"]

    def _make_scrollable(self, parent):
        """Tao 1 khung co thanh cuon doc, dam bao luon xem/bam duoc het cac nut
        du noi dung ben trong dai bao nhieu."""
        canvas = tk.Canvas(parent, highlightthickness=0, bg=WINDOW_BG)
        scrollbar = ttk.Scrollbar(parent, style="Advanced.Vertical.TScrollbar", orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas, style="Advanced.TFrame")

        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_wheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        return inner

    def _persist(self):
        if self.app:
            save_servers(self.app.servers)
        else:
            save_servers({self.name: self.entry})

    def _send_or_offline(self, cmd, offline_action=None, require_running=True):
        rs = self.get_running()
        if rs and rs.is_running():
            rs.send_command(cmd)
            return True
        if offline_action:
            offline_action()
            return True
        if require_running:
            messagebox.showwarning("Canh bao", "Server can dang chay de dung chuc nang nay.\nHay Start server truoc.")
        return False

    # ---------------- Tab Nguoi choi ----------------
    def _build_player_tab(self):
        f = self._make_scrollable(self.player_tab)
        pad = {"padx": 10, "pady": 6}

        crack_frame = ttk.LabelFrame(f, style="Advanced.TLabelframe", text="Che do Crack (cho tai khoan Minecraft lau nhu TLauncher)")
        crack_frame.pack(fill="x", padx=10, pady=8)

        online_mode = get_server_property(self._server_path(), "online-mode", "true")
        self.crack_var = tk.BooleanVar(value=(online_mode.strip().lower() == "false"))
        ttk.Checkbutton(
            crack_frame, style="Advanced.TCheckbutton",
            text="Bat Crack (online-mode = false)",
            variable=self.crack_var,
            command=self._toggle_crack
        ).pack(anchor="w", padx=8, pady=4)
        ttk.Label(
            crack_frame,
            text="Bat: chap nhan moi client, ke ca tai khoan lau (TLauncher...), khong xac thuc qua Mojang.\n"
                 "Tat (No Crack): chi tai khoan Minecraft that (co ban quyen) moi vao duoc.\n"
                 "Can Stop va Start lai server de ap dung thay doi.",
            foreground="gray", wraplength=480, justify="left"
        ).pack(anchor="w", padx=8, pady=(0, 6))

        player_frame = ttk.LabelFrame(f, style="Advanced.TLabelframe", text="Quan ly nguoi choi (theo ten)")
        player_frame.pack(fill="x", padx=10, pady=8)

        ttk.Label(player_frame, text="Ten nguoi choi:").grid(row=0, column=0, sticky="w", **pad)
        self.player_name_var = tk.StringVar()
        ttk.Entry(player_frame, textvariable=self.player_name_var, width=25).grid(row=0, column=1, columnspan=2, sticky="w", **pad)

        ttk.Button(player_frame, style="Advanced.TButton", text="Cap quyen OP", command=self._op_player).grid(row=1, column=0, sticky="ew", padx=6, pady=4)
        ttk.Button(player_frame, style="Advanced.TButton", text="Go quyen OP", command=self._deop_player).grid(row=1, column=1, sticky="ew", padx=6, pady=4)
        ttk.Button(player_frame, style="Advanced.TButton", text="Kick", command=self._kick_player).grid(row=1, column=2, sticky="ew", padx=6, pady=4)

        ttk.Button(player_frame, style="Advanced.TButton", text="Ban ten", command=self._ban_player).grid(row=2, column=0, sticky="ew", padx=6, pady=4)
        ttk.Button(player_frame, style="Advanced.TButton", text="Ban IP", command=self._banip_player).grid(row=2, column=1, sticky="ew", padx=6, pady=4)
        ttk.Button(player_frame, style="Advanced.TButton", text="Go Ban", command=self._unban_player).grid(row=2, column=2, sticky="ew", padx=6, pady=4)

        ttk.Button(player_frame, style="Advanced.TButton", text="Go Ban IP", command=self._unbanip_player).grid(row=3, column=0, sticky="ew", padx=6, pady=4)

        ttk.Button(player_frame, style="Advanced.TButton", text="Luon luon cap OP (tu dong op lai neu bi go)",
                   command=self._always_op_player).grid(row=4, column=0, columnspan=3, sticky="ew", padx=6, pady=(8, 4))

        ttk.Label(
            f,
            text="Cap OP / Go OP hoat dong ca khi server dang TAT (ghi truc tiep vao ops.json).\n"
                 "Kick / Ban / Ban IP / Go Ban / Go Ban IP can server dang CHAY (gui lenh qua console).\n"
                 "'Luon luon cap OP' se tu dong gui lai lenh op moi ~30 giay trong khi server chay.",
            foreground="gray", wraplength=480, justify="left"
        ).pack(anchor="w", padx=16, pady=4)

        ttk.Separator(f).pack(fill="x", padx=10, pady=6)
        ttk.Label(f, style="Advanced.TLabel", text="Trang thai nguoi choi da quan ly (ON = dang co hieu luc):",
                  font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=10)

        self.status_container = ttk.Frame(f)
        self.status_container.pack(fill="x", padx=10, pady=8)
        self._refresh_player_status()

    def _refresh_player_status(self):
        for w in self.status_container.winfo_children():
            w.destroy()
        players = self.entry.get("players", {})
        if not players:
            ttk.Label(self.status_container, text="(Chua co nguoi choi nao duoc quan ly)",
                      foreground="gray").pack(anchor="w")
            return
        col = 0
        row_frame = ttk.Frame(self.status_container, style="Advanced.TFrame")
        row_frame.pack(fill="x")
        for pname, flags in players.items():
            box = ttk.LabelFrame(row_frame, text=pname)
            box.grid(row=0, column=col, padx=6, pady=4, sticky="n")
            ttk.Label(box, text=f"OP: {'ON' if flags.get('op') else 'OFF'}",
                      foreground="#1a7f1a" if flags.get("op") else "#999999").pack(anchor="w", padx=6, pady=1)
            ttk.Label(box, text=f"Ban: {'ON' if flags.get('ban') else 'OFF'}",
                      foreground="#c0392b" if flags.get("ban") else "#999999").pack(anchor="w", padx=6, pady=1)
            ttk.Label(box, text=f"BanIP: {'ON' if flags.get('banip') else 'OFF'}",
                      foreground="#c0392b" if flags.get("banip") else "#999999").pack(anchor="w", padx=6, pady=1)
            ttk.Label(box, text=f"Luon OP: {'ON' if flags.get('always_op') else 'OFF'}",
                      foreground="#1a7f1a" if flags.get("always_op") else "#999999").pack(anchor="w", padx=6, pady=1)
            col += 1

    def _toggle_crack(self):
        value = "false" if self.crack_var.get() else "true"
        set_server_property(self._server_path(), "online-mode", value)
        messagebox.showinfo("Da luu", "Da cap nhat che do Crack. Hay Stop va Start lai server de ap dung.")

    def _get_player_name(self):
        name = self.player_name_var.get().strip()
        if not name:
            messagebox.showwarning("Canh bao", "Vui long nhap ten nguoi choi")
            return None
        return name

    def _op_player(self):
        name = self._get_player_name()
        if not name:
            return
        self._send_or_offline(
            f"op {name}",
            offline_action=lambda: add_op_offline(self._server_path(), name),
            require_running=False,
        )
        set_player_flag(self.entry, name, "op", True)
        self._persist()
        self._refresh_player_status()
        messagebox.showinfo("Xong", f"Da cap quyen OP cho '{name}'.")

    def _deop_player(self):
        name = self._get_player_name()
        if not name:
            return
        self._send_or_offline(
            f"deop {name}",
            offline_action=lambda: remove_op_offline(self._server_path(), name),
            require_running=False,
        )
        set_player_flag(self.entry, name, "op", False)
        set_player_flag(self.entry, name, "always_op", False)
        self._persist()
        self._refresh_player_status()
        messagebox.showinfo("Xong", f"Da go quyen OP cua '{name}'.")

    def _always_op_player(self):
        name = self._get_player_name()
        if not name:
            return
        self._send_or_offline(
            f"op {name}",
            offline_action=lambda: add_op_offline(self._server_path(), name),
            require_running=False,
        )
        set_player_flag(self.entry, name, "op", True)
        set_player_flag(self.entry, name, "always_op", True)
        self._persist()
        self._refresh_player_status()
        messagebox.showinfo("Xong", f"'{name}' se luon duoc tu dong cap lai OP khi server dang chay.")

    def _kick_player(self):
        name = self._get_player_name()
        if not name:
            return
        if self._send_or_offline(f"kick {name}"):
            messagebox.showinfo("Xong", f"Da gui lenh kick '{name}'.")

    def _ban_player(self):
        name = self._get_player_name()
        if not name:
            return
        if self._send_or_offline(f"ban {name}"):
            set_player_flag(self.entry, name, "ban", True)
            self._persist()
            self._refresh_player_status()
            messagebox.showinfo("Xong", f"Da ban '{name}'.")

    def _banip_player(self):
        name = self._get_player_name()
        if not name:
            return
        if self._send_or_offline(f"ban-ip {name}"):
            set_player_flag(self.entry, name, "banip", True)
            self._persist()
            self._refresh_player_status()
            messagebox.showinfo("Xong", f"Da gui lenh ban-ip cho '{name}'.")

    def _unban_player(self):
        name = self._get_player_name()
        if not name:
            return
        if self._send_or_offline(f"pardon {name}"):
            set_player_flag(self.entry, name, "ban", False)
            set_player_flag(self.entry, name, "banip", False)
            self._persist()
            self._refresh_player_status()
            messagebox.showinfo("Xong", f"Da go ban cho '{name}'.")

    def _unbanip_player(self):
        name = self._get_player_name()
        if not name:
            return
        if self._send_or_offline(f"pardon-ip {name}"):
            set_player_flag(self.entry, name, "banip", False)
            self._persist()
            self._refresh_player_status()
            messagebox.showinfo("Xong", f"Da go ban IP cho '{name}'.\n"
                                          f"(Neu day la ten nguoi choi, hay dam bao ban da nhap dung dia chi IP can go ban).")

    # ---------------- Tab May chu ----------------
    def _build_server_tab(self):
        f = self._make_scrollable(self.server_tab)
        pad = {"padx": 10, "pady": 6}

        ttk.Label(f, style="Advanced.TLabel", text=f"Server: {self.name}", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", **pad)

        ttk.Label(f, style="Advanced.TLabel", text="Seed (chi anh huong khi tao THE GIOI MOI):").grid(row=1, column=0, sticky="w", **pad)
        self.seed_var = tk.StringVar(value=get_server_property(self._server_path(), "level-seed", ""))
        ttk.Entry(f, textvariable=self.seed_var, width=20).grid(row=1, column=1, sticky="w", **pad)

        ttk.Label(f, style="Advanced.TLabel", text="So chunk hien thi (view-distance):").grid(row=2, column=0, sticky="w", **pad)
        self.view_var = tk.StringVar(value=get_server_property(self._server_path(), "view-distance", "10"))
        ttk.Spinbox(f, from_=3, to=32, textvariable=self.view_var, width=8).grid(row=2, column=1, sticky="w", **pad)

        ttk.Label(f, style="Advanced.TLabel", text="Simulation distance:").grid(row=3, column=0, sticky="w", **pad)
        self.sim_var = tk.StringVar(value=get_server_property(self._server_path(), "simulation-distance", "10"))
        ttk.Spinbox(f, from_=3, to=32, textvariable=self.sim_var, width=8).grid(row=3, column=1, sticky="w", **pad)

        ttk.Label(f, style="Advanced.TLabel", text="Do kho (difficulty):").grid(row=4, column=0, sticky="w", **pad)
        self.diff_var = tk.StringVar(value=get_server_property(self._server_path(), "difficulty", "easy"))
        ttk.Combobox(f, textvariable=self.diff_var, values=["peaceful", "easy", "normal", "hard"],
                     state="readonly", width=15).grid(row=4, column=1, sticky="w", **pad)

        ttk.Button(f, style="Advanced.TButton", text="Ap dung cac thay doi tren", command=self._apply_server_settings).grid(
            row=5, column=0, columnspan=2, pady=10)

        ttk.Label(
            f,
            text="Luu y: Seed / view-distance / simulation-distance can Stop va Start lai server de ap dung.\n"
                 "Do kho (difficulty) se duoc ap dung ngay neu server dang chay.",
            foreground="gray", wraplength=480, justify="left"
        ).grid(row=6, column=0, columnspan=2, sticky="w", padx=10)

        # ---- Icon server (vuong / tron) ----
        icon_frame = ttk.LabelFrame(f, style="Advanced.TLabelframe", text="Icon server (anh dai dien hien trong danh sach Multiplayer)")
        icon_frame.grid(row=7, column=0, columnspan=2, sticky="ew", padx=10, pady=8)

        self.icon_shape_var = tk.StringVar(value="square")
        shape_row = ttk.Frame(icon_frame, style="Advanced.TFrame")
        shape_row.pack(fill="x", padx=8, pady=(8, 4))
        ttk.Label(shape_row, style="Advanced.TLabel", text="Hinh dang icon:").pack(side="left", padx=(0, 10))
        ttk.Radiobutton(shape_row, text="Vuong", variable=self.icon_shape_var, value="square",
                         command=self._refresh_icon_preview_pending).pack(side="left")
        ttk.Radiobutton(shape_row, text="Tron", variable=self.icon_shape_var, value="round",
                         command=self._refresh_icon_preview_pending).pack(side="left", padx=(10, 0))

        preview_row = ttk.Frame(icon_frame, style="Advanced.TFrame")
        preview_row.pack(fill="x", padx=8, pady=(0, 4))
        self.icon_preview_label = tk.Label(preview_row, text="(chua co icon)", width=10, height=5,
                                            relief="groove", bg="#2c2c2c", fg="#aaaaaa")
        self.icon_preview_label.pack(side="left")
        ttk.Label(preview_row, style="Advanced.TLabel", text="  Anh se duoc tu dong resize ve 64x64px (chuan Minecraft).",
                  foreground="gray", wraplength=320, justify="left").pack(side="left", padx=8)

        icon_btn_row = ttk.Frame(icon_frame, style="Advanced.TFrame")
        icon_btn_row.pack(fill="x", padx=8, pady=(4, 8))
        ttk.Button(icon_btn_row, style="Advanced.TButton", text="Chon anh va ap dung", command=self._change_server_icon).pack(
            side="left", padx=4)
        ttk.Button(icon_btn_row, style="Advanced.TButton", text="Xoa icon (ve mac dinh)", command=self._remove_server_icon).pack(
            side="left", padx=4)

        self._pending_icon_path = None
        self._load_icon_preview()

        # ---- So luong nguoi choi toi da (Max Players) ----
        maxplayers_frame = ttk.LabelFrame(f, style="Advanced.TLabelframe", text="So luong nguoi choi toi da (Max Players)")
        maxplayers_frame.grid(row=8, column=0, columnspan=2, sticky="ew", padx=10, pady=8)

        current_max = get_server_property(self._server_path(), "max-players", "20")
        self.maxplayers_var = tk.StringVar(value=current_max)

        mp_row1 = ttk.Frame(maxplayers_frame, style="Advanced.TFrame")
        mp_row1.pack(fill="x", padx=8, pady=(8, 4))
        ttk.Label(mp_row1, style="Advanced.TLabel", text="So luong tuy chinh:").pack(side="left", padx=(0, 6))
        ttk.Entry(mp_row1, textvariable=self.maxplayers_var, width=10).pack(side="left")
        ttk.Button(mp_row1, style="Advanced.TButton", text="Luu", command=self._save_max_players).pack(side="left", padx=6)

        ttk.Label(maxplayers_frame, text="Hoac chon nhanh (ap dung ngay, khong can ghi so):").pack(
            anchor="w", padx=8, pady=(4, 2))

        mp_preset_row = ttk.Frame(maxplayers_frame, style="Advanced.TFrame")
        mp_preset_row.pack(fill="x", padx=8, pady=(0, 8))
        for val in [1, 20, 36, 50, 67, 100, 1000]:
            ttk.Button(mp_preset_row, text=str(val), width=6,
                       command=lambda v=val: self._quick_set_max_players(v)).pack(side="left", padx=3)

        ttk.Label(maxplayers_frame, text="Can Stop va Start lai server de so luong moi co hieu luc.",
                  foreground="gray").pack(anchor="w", padx=8, pady=(0, 6))

        # ---- Mo ta server + bang mau ----
        desc_frame = ttk.LabelFrame(f, style="Advanced.TLabelframe", text="Mo ta server")
        desc_frame.grid(row=9, column=0, columnspan=2, sticky="ew", padx=10, pady=8)

        self.desc_text = tk.Text(desc_frame, height=3, width=52, wrap="word")
        self.desc_text.pack(fill="x", padx=8, pady=(8, 4))
        self.desc_text.insert("1.0", self.entry.get("description", ""))

        color_row = ttk.Frame(desc_frame, style="Advanced.TFrame")
        color_row.pack(fill="x", padx=8, pady=(0, 4))
        ttk.Label(color_row, style="Advanced.TLabel", text="Bang mau mo ta:").pack(side="left", padx=(0, 6))

        self.desc_color_var = tk.StringVar(value=self.entry.get("description_color", "#000000"))

        palette_colors = [
            "#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#1abc9c",
            "#3498db", "#9b59b6", "#34495e", "#7f8c8d", "#000000",
        ]
        self.palette_canvas = tk.Canvas(color_row, bg=CARD, height=22, width=22 * len(palette_colors), highlightthickness=0)
        self.palette_canvas.pack(side="left")
        for i, c in enumerate(palette_colors):
            x0 = i * 22 + 2
            rect_id = self.palette_canvas.create_rectangle(x0, 2, x0 + 18, 20, fill=c, outline="#ffffff")
            self.palette_canvas.tag_bind(rect_id, "<Button-1>", lambda e, col=c: self._pick_palette_color(col))

        ttk.Button(color_row, text="Mau khac...", command=self._pick_custom_color).pack(side="left", padx=6)

        preview_row = ttk.Frame(desc_frame, style="Advanced.TFrame")
        preview_row.pack(fill="x", padx=8, pady=(4, 8))
        ttk.Label(preview_row, style="Advanced.TLabel", text="Xem truoc: ").pack(side="left")
        preview_text = self.entry.get("description", "").strip() or "(chua co mo ta)"
        self.desc_preview_label = tk.Label(preview_row, text=preview_text, fg=self.desc_color_var.get())
        self.desc_preview_label.pack(side="left")

        ttk.Button(desc_frame, style="Advanced.TButton", text="Luu mo ta", command=self._save_description).pack(anchor="e", padx=8, pady=(0, 8))

        # ---- Mo ta trong game (MOTD) + bang mau Minecraft rieng ----
        motd_frame = ttk.LabelFrame(f, style="Advanced.TLabelframe", text="Mo ta trong game (MOTD - hien trong danh sach server Minecraft)")
        motd_frame.grid(row=10, column=0, columnspan=2, sticky="ew", padx=10, pady=8)

        self.MC_COLORS = [
            ("0", "#000000"), ("1", "#0000AA"), ("2", "#00AA00"), ("3", "#00AAAA"),
            ("4", "#AA0000"), ("5", "#AA00AA"), ("6", "#FFAA00"), ("7", "#AAAAAA"),
            ("8", "#555555"), ("9", "#5555FF"), ("a", "#55FF55"), ("b", "#55FFFF"),
            ("c", "#FF5555"), ("d", "#FF55FF"), ("e", "#FFFF55"), ("f", "#FFFFFF"),
        ]

        self.motd_var = tk.StringVar(value=get_server_property(self._server_path(), "motd", "A Minecraft Server"))
        self.motd_entry = ttk.Entry(motd_frame, textvariable=self.motd_var, width=52)
        self.motd_entry.pack(fill="x", padx=8, pady=(8, 4))
        self.motd_entry.bind("<KeyRelease>", lambda e: self._update_motd_preview())

        ttk.Label(motd_frame, style="Advanced.TLabel", text="Bang mau Minecraft (rieng, khac bang mau mo ta o tren) - bam de chen ma mau:").pack(
            anchor="w", padx=8)

        swatch_row = ttk.Frame(motd_frame, style="Advanced.TFrame")
        swatch_row.pack(fill="x", padx=8, pady=(2, 4))
        motd_canvas = tk.Canvas(swatch_row, bg=CARD, height=22, width=22 * len(self.MC_COLORS), highlightthickness=0)
        motd_canvas.pack(side="left")
        for i, (code, hexcolor) in enumerate(self.MC_COLORS):
            x0 = i * 22 + 2
            rect_id = motd_canvas.create_rectangle(x0, 2, x0 + 18, 20, fill=hexcolor, outline="#ffffff")
            motd_canvas.tag_bind(rect_id, "<Button-1>", lambda e, c=code: self._insert_motd_color(c))
        ttk.Button(swatch_row, style="Advanced.TButton", text="Xuong dong", command=self._insert_motd_newline).pack(side="left", padx=6)

        ttk.Label(motd_frame, style="Advanced.TLabel", text="Xem truoc (giong khi hien trong game):").pack(anchor="w", padx=8, pady=(4, 0))
        self.motd_preview = tk.Text(motd_frame, height=2, width=52, bg="#18181B", fg="#ffffff",
                                     state="disabled", font=("Consolas", 10))
        self.motd_preview.pack(fill="x", padx=8, pady=(2, 6))

        ttk.Button(motd_frame, text="Luu MOTD", command=self._save_motd).pack(anchor="e", padx=8, pady=(0, 4))
        ttk.Label(motd_frame, style="Advanced.TLabel", text="Can Stop va Start lai server de MOTD moi hien ra trong game.",
                  foreground="gray").pack(anchor="w", padx=8, pady=(0, 8))

        self._update_motd_preview()

        ttk.Separator(f).grid(row=11, column=0, columnspan=2, sticky="ew", pady=10, padx=10)

        ttk.Label(f, style="Advanced.TLabel", text="Gui lenh truc tiep (khong can vao game):").grid(
            row=12, column=0, columnspan=2, sticky="w", padx=10)
        cmd_frame = ttk.Frame(f, style="Advanced.TFrame")
        cmd_frame.grid(row=13, column=0, columnspan=2, sticky="ew", padx=10, pady=4)
        self.cmd_var = tk.StringVar()
        entry = ttk.Entry(cmd_frame, textvariable=self.cmd_var, width=30)
        entry.pack(side="left", fill="x", expand=True)
        entry.bind("<Return>", lambda e: self._send_command())
        ttk.Button(cmd_frame, text="Gui lenh", command=self._send_command).pack(side="right", padx=4)

        ttk.Button(f, style="Advanced.TButton", text="Mo thu muc server", command=self._open_folder).grid(
            row=14, column=0, columnspan=2, pady=8)

    def _save_max_players(self):
        value = self.maxplayers_var.get().strip()
        if not value.isdigit() or int(value) <= 0:
            messagebox.showerror("Loi", "So luong nguoi choi phai la so nguyen duong")
            return
        set_server_property(self._server_path(), "max-players", value)
        messagebox.showinfo(
            "Da luu",
            f"Da luu so luong nguoi choi toi da: {value}.\nCan Stop va Start lai server de ap dung."
        )

    def _quick_set_max_players(self, value):
        self.maxplayers_var.set(str(value))
        set_server_property(self._server_path(), "max-players", str(value))
        messagebox.showinfo(
            "Da ap dung",
            f"Da dat so luong nguoi choi toi da: {value}.\nCan Stop va Start lai server de ap dung."
        )

    def _load_icon_preview(self):
        icon_path = os.path.join(self._server_path(), "server-icon.png")
        if not PIL_AVAILABLE:
            self.icon_preview_label.config(text="(can cai\nPillow)", image="")
            return
        if os.path.exists(icon_path):
            try:
                img = Image.open(icon_path).convert("RGBA").resize((64, 64))
                self._icon_preview_img = ImageTk.PhotoImage(img)
                self.icon_preview_label.config(image=self._icon_preview_img, text="")
            except Exception:
                self.icon_preview_label.config(text="(loi doc\nicon)", image="")
        else:
            self.icon_preview_label.config(text="(chua co\nicon)", image="")

    def _refresh_icon_preview_pending(self):
        if self._pending_icon_path:
            self._apply_icon_processing(self._pending_icon_path, preview_only=True)

    def _change_server_icon(self):
        if not PIL_AVAILABLE:
            messagebox.showerror(
                "Thieu thu vien",
                "Can cai thu vien Pillow de doi icon.\nMo Command Prompt, chay:\npip install Pillow\n"
                "Sau do mo lai app."
            )
            return
        path = filedialog.askopenfilename(
            title="Chon anh icon server",
            filetypes=[("Anh", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), ("Tat ca", "*.*")]
        )
        if not path:
            return
        self._pending_icon_path = path
        self._apply_icon_processing(path, preview_only=False)

    def _apply_icon_processing(self, src_path, preview_only=False):
        try:
            img = Image.open(src_path).convert("RGBA")
            w, h = img.size
            side = min(w, h)
            left = (w - side) // 2
            top = (h - side) // 2
            img = img.crop((left, top, left + side, top + side))
            img = img.resize((64, 64), Image.LANCZOS)

            if self.icon_shape_var.get() == "round":
                mask = Image.new("L", (64, 64), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, 64, 64), fill=255)
                img.putalpha(mask)

            if preview_only:
                self._icon_preview_img = ImageTk.PhotoImage(img)
                self.icon_preview_label.config(image=self._icon_preview_img, text="")
                return

            server_path = self._server_path()
            os.makedirs(server_path, exist_ok=True)
            dest_path = os.path.join(server_path, "server-icon.png")

            last_error = None
            saved = False
            for _ in range(5):
                try:
                    img.save(dest_path, "PNG")
                    saved = True
                    break
                except OSError as save_err:
                    last_error = save_err
                    os.makedirs(server_path, exist_ok=True)
                    time.sleep(0.4)

            if not saved:
                extra = ""
                if not os.path.isdir(server_path):
                    extra = f"\n(Thu muc server hien khong ton tai: {server_path})"
                elif not os.access(server_path, os.W_OK):
                    extra = "\n(Thu muc co the dang bi khoa boi OneDrive/antivirus, hay thu lai sau it giay.)"
                messagebox.showerror("Loi", f"Khong the luu icon: {last_error}{extra}")
                return

            self._icon_preview_img = ImageTk.PhotoImage(img)
            self.icon_preview_label.config(image=self._icon_preview_img, text="")
            messagebox.showinfo(
                "Xong",
                "Da doi icon server (dang " + ("tron" if self.icon_shape_var.get() == "round" else "vuong") +
                ").\nCan Stop va Start lai server de icon moi hien ra trong game."
            )
        except Exception as e:
            messagebox.showerror("Loi", f"Khong the xu ly anh: {e}")

    def _remove_server_icon(self):
        icon_path = os.path.join(self._server_path(), "server-icon.png")
        if os.path.exists(icon_path):
            try:
                os.remove(icon_path)
                messagebox.showinfo("Xong", "Da xoa icon. Server se dung icon mac dinh.\nCan Stop va Start lai de ap dung.")
            except Exception as e:
                messagebox.showerror("Loi", f"Khong the xoa icon: {e}")
        self._pending_icon_path = None
        self._load_icon_preview()

    def _insert_motd_color(self, code):
        self.motd_entry.insert(tk.INSERT, f"\u00A7{code}")
        self._update_motd_preview()

    def _insert_motd_newline(self):
        self.motd_entry.insert(tk.INSERT, "\\n")
        self._update_motd_preview()

    def _update_motd_preview(self):
        text = self.motd_var.get()
        color_map = dict(self.MC_COLORS)
        self.motd_preview.config(state="normal")
        self.motd_preview.delete("1.0", "end")
        current_color = "#ffffff"
        segment = ""
        i = 0

        def flush():
            nonlocal segment
            if segment:
                tagname = f"c_{current_color}"
                self.motd_preview.tag_config(tagname, foreground=current_color)
                self.motd_preview.insert("end", segment, tagname)
                segment = ""

        while i < len(text):
            if text[i] == "\u00A7" and i + 1 < len(text):
                flush()
                current_color = color_map.get(text[i + 1], current_color)
                i += 2
                continue
            if text[i] == "\\" and i + 1 < len(text) and text[i + 1] == "n":
                flush()
                self.motd_preview.insert("end", "\n")
                i += 2
                continue
            segment += text[i]
            i += 1
        flush()
        self.motd_preview.config(state="disabled")

    def _save_motd(self):
        motd = self.motd_var.get()
        set_server_property(self._server_path(), "motd", motd)
        self._update_motd_preview()
        messagebox.showinfo("Da luu", "Da luu MOTD. Hay Stop va Start lai server de ap dung trong game.")

    def _pick_palette_color(self, color):
        self.desc_color_var.set(color)
        self.desc_preview_label.config(fg=color)

    def _pick_custom_color(self):
        result = colorchooser.askcolor(color=self.desc_color_var.get(), title="Chon mau mo ta")
        if result and result[1]:
            self.desc_color_var.set(result[1])
            self.desc_preview_label.config(fg=result[1])

    def _save_description(self):
        text = self.desc_text.get("1.0", "end").strip()
        color = self.desc_color_var.get()
        self.entry["description"] = text
        self.entry["description_color"] = color
        self._persist()
        self.desc_preview_label.config(text=text or "(chua co mo ta)", fg=color)
        if self.app and hasattr(self.app, "_refresh_list"):
            self.app._refresh_list()
        messagebox.showinfo("Da luu", "Da luu mo ta server.")

    def _apply_server_settings(self):
        path = self._server_path()
        seed = self.seed_var.get().strip()
        view = self.view_var.get().strip()
        sim = self.sim_var.get().strip()
        diff = self.diff_var.get().strip()

        set_server_property(path, "level-seed", seed)
        set_server_property(path, "view-distance", view)
        set_server_property(path, "simulation-distance", sim)
        set_server_property(path, "difficulty", diff)

        rs = self.get_running()
        if rs and rs.is_running():
            rs.send_command(f"difficulty {diff}")

        messagebox.showinfo("Da luu", "Da luu cau hinh. Seed/view-distance/simulation-distance can Stop va Start lai de ap dung.")

    def _send_command(self):
        cmd = self.cmd_var.get().strip()
        if not cmd:
            return
        rs = self.get_running()
        if rs and rs.is_running():
            rs.send_command(cmd)
            self.cmd_var.set("")
        else:
            messagebox.showwarning("Canh bao", "Server can dang chay de gui lenh")

    def _open_folder(self):
        os.startfile(self._server_path())

    # ---------------- Tab Moi truong ----------------
    def _build_env_tab(self):
        f = self._make_scrollable(self.env_tab)
        pad = {"padx": 10, "pady": 6}

        ttk.Label(f, style="Advanced.TLabel", text="Loai the gioi (World Type):", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", **pad)

        current_level_type = get_server_property(self._server_path(), "level-type", "minecraft:normal")
        self.env_var = tk.StringVar(value=current_level_type)

        world_types = [
            ("minecraft:normal", "The gioi thuong (Normal)"),
            ("minecraft:flat", "The gioi phang (Flat)"),
            ("minecraft:large_biomes", "Large Biomes (dia hinh lon)"),
            ("minecraft:amplified", "Amplified (dia hinh cuc cao)"),
        ]
        row = 1
        for value, label in world_types:
            ttk.Radiobutton(f, style="Advanced.TRadiobutton", text=label, variable=self.env_var, value=value).grid(
                row=row, column=0, columnspan=2, sticky="w", padx=16, pady=2)
            row += 1

        ttk.Label(
            f,
            text="Luu y: chi anh huong THE GIOI MOI. The gioi hien tai da tao roi se KHONG tu doi.\n"
                 "Muon doi hoan toan (vi du tu The gioi thuong sang The gioi phang), phai xoa\n"
                 "the gioi cu de server tao lai tu dau (xem nut xoa ben duoi).",
            foreground="gray", wraplength=480, justify="left"
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=(8, 4))
        row += 1

        ttk.Button(f, style="Advanced.TButton", text="Ap dung loai the gioi (cho lan tao moi)", command=self._apply_world_type).grid(
            row=row, column=0, columnspan=2, pady=8)
        row += 1

        ttk.Separator(f).grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        row += 1

        ttk.Label(f, style="Advanced.TLabel", text="Sao luu / Phuc hoi the gioi:", font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=10)
        row += 1

        ttk.Label(
            f,
            text="Luu the gioi: dong goi the gioi hien tai thanh 1 file .zip luu tren may ban.\n"
                 "Tai the gioi: lay 1 file .zip da luu truoc do, thay the vao the gioi hien tai cua server.",
            foreground="gray", wraplength=480, justify="left"
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=(2, 6))
        row += 1

        backup_btn_frame = ttk.Frame(f)
        backup_btn_frame.grid(row=row, column=0, columnspan=2, pady=4)
        ttk.Button(backup_btn_frame, text="Luu the gioi (xuat ra may)", command=self._backup_world).pack(
            side="left", padx=6)
        ttk.Button(backup_btn_frame, text="Tai the gioi (nhap tu may)", command=self._load_world).pack(
            side="left", padx=6)
        row += 1

        ttk.Separator(f).grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        row += 1

        ttk.Label(f, style="Advanced.TLabel", text="Xoa the gioi hien tai va tao lai theo loai da chon o tren:",
                  font=("Segoe UI", 9, "bold")).grid(row=row, column=0, columnspan=2, sticky="w", padx=10)
        row += 1

        ttk.Label(
            f,
            text="CANH BAO: thao tac nay se XOA VINH VIEN toan bo the gioi hien tai\n"
                 "(nha cua, cong trinh, do dac...). Khong the hoan tac.\n"
                 "Can Stop server truoc khi xoa. Nen bam 'Luu the gioi' truoc neu muon giu lai.",
            foreground="#c0392b", wraplength=480, justify="left"
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=(2, 6))
        row += 1

        ttk.Button(f, style="Advanced.TButton", text="Xoa the gioi va tao lai (KHONG THE HOAN TAC)", command=self._reset_world).grid(
            row=row, column=0, columnspan=2, pady=8)

    def _apply_world_type(self):
        value = self.env_var.get()
        set_server_property(self._server_path(), "level-type", value)
        messagebox.showinfo(
            "Da luu",
            "Da luu loai the gioi. Se ap dung cho lan TAO THE GIOI MOI.\n"
            "Neu muon doi ngay lap tuc, hay dung nut 'Xoa the gioi va tao lai' ben duoi."
        )

    def _get_world_folders(self):
        server_path = self._server_path()
        level_name = get_server_property(server_path, "level-name", "world")
        folders = [level_name, f"{level_name}_nether", f"{level_name}_the_end"]
        return [f for f in folders if os.path.isdir(os.path.join(server_path, f))]

    def _backup_world(self):
        rs = self.get_running()
        if rs and rs.is_running():
            messagebox.showwarning("Canh bao", "Hay Stop server truoc khi luu the gioi (tranh loi/mat du lieu).")
            return

        server_path = self._server_path()
        existing = self._get_world_folders()
        if not existing:
            messagebox.showinfo("Thong bao", "Chua co the gioi nao de luu (server chua tung duoc khoi dong).")
            return

        dest_zip = filedialog.asksaveasfilename(
            title="Luu the gioi ra file zip",
            defaultextension=".zip",
            filetypes=[("Zip files", "*.zip")],
            initialfile=f"{self.name}_the_gioi_backup.zip"
        )
        if not dest_zip:
            return

        try:
            with zipfile.ZipFile(dest_zip, "w", zipfile.ZIP_DEFLATED) as zf:
                for folder in existing:
                    folder_path = os.path.join(server_path, folder)
                    for root, dirs, files in os.walk(folder_path):
                        for file in files:
                            full_file = os.path.join(root, file)
                            arcname = os.path.relpath(full_file, server_path)
                            zf.write(full_file, arcname)
            messagebox.showinfo("Xong", f"Da luu the gioi vao:\n{dest_zip}")
        except Exception as e:
            messagebox.showerror("Loi", f"Khong the luu the gioi: {e}")

    def _load_world(self):
        rs = self.get_running()
        if rs and rs.is_running():
            messagebox.showwarning("Canh bao", "Hay Stop server truoc khi tai the gioi.")
            return

        src_zip = filedialog.askopenfilename(
            title="Chon file zip the gioi da luu truoc do",
            filetypes=[("Zip files", "*.zip"), ("Tat ca", "*.*")]
        )
        if not src_zip:
            return

        if not messagebox.askyesno(
            "Xac nhan",
            "Tai the gioi nay se THAY THE hoan toan the gioi hien tai cua server.\n"
            "The gioi hien tai (neu co) se bi xoa. Ban co chac chan muon tiep tuc?"
        ):
            return

        server_path = self._server_path()
        existing = self._get_world_folders()
        failed = []
        for folder in existing:
            full_path = os.path.join(server_path, folder)
            if not safe_rmtree(full_path):
                failed.append(folder)
        if failed:
            messagebox.showerror(
                "Loi",
                f"Khong the xoa the gioi hien tai ({', '.join(failed)}) de thay the.\nHay Stop server va thu lai."
            )
            return

        try:
            with zipfile.ZipFile(src_zip, "r") as zf:
                zf.extractall(server_path)
            messagebox.showinfo("Xong", "Da tai the gioi vao server. Bam Start de kiem tra.")
        except Exception as e:
            messagebox.showerror("Loi", f"Khong the giai nen/tai the gioi: {e}")

    def _reset_world(self):
        rs = self.get_running()
        if rs and rs.is_running():
            messagebox.showwarning("Canh bao", "Hay Stop server truoc khi xoa the gioi.")
            return
        if not messagebox.askyesno(
            "Xac nhan XOA THE GIOI",
            "Ban co CHAC CHAN muon xoa toan bo the gioi hien tai va tao lai tu dau?\n"
            "Hanh dong nay KHONG THE HOAN TAC."
        ):
            return

        server_path = self._server_path()
        level_name = get_server_property(server_path, "level-name", "world")
        folders_to_delete = [level_name, f"{level_name}_nether", f"{level_name}_the_end"]

        failed = []
        for folder in folders_to_delete:
            full_path = os.path.join(server_path, folder)
            if os.path.exists(full_path):
                if not safe_rmtree(full_path):
                    failed.append(folder)

        set_server_property(server_path, "level-type", self.env_var.get())

        if failed:
            messagebox.showwarning(
                "Canh bao",
                f"Da xoa mot phan, nhung khong xoa duoc: {', '.join(failed)}\n"
                f"Co the dang bi khoa boi tien trinh khac, hay doi it phut roi thu lai."
            )
        else:
            messagebox.showinfo(
                "Xong",
                "Da xoa the gioi cu. The gioi MOI (theo loai da chon) se duoc tao\n"
                "khi ban Start server lan toi."
            )




# ---------------------------------------------------------------------------
# Dialog: Tab Servers (co mat khau) - xem tat ca server theo ID + dieu khien nhanh
# ---------------------------------------------------------------------------
SERVERS_TAB_PASSWORD = "nguyentrangiabao"


class ServersOverviewDialog(tk.Toplevel):
    def __init__(self, master, app):
        super().__init__(master)
        apply_secondary_theme(self)
        self.title("Servers - Quan tri (rieng tu)")
        self.geometry("480x600")
        self.app = app
        self.transient(master)

        ttk.Label(self, text="Danh sach tat ca server", font=("Segoe UI", 11, "bold")).pack(
            anchor="w", padx=10, pady=8)

        self.list_frame = ttk.Frame(self)
        self.list_frame.pack(fill="both", expand=True, padx=10)

        ttk.Label(
            self,
            text="● Xanh la = dang hoat dong    ● Vang = dang khoi dong\n"
                 "● Do = co van de (loi/crash)    ● Den = khong khoi dong",
            foreground="gray"
        ).pack(anchor="w", padx=10, pady=6)

        ttk.Separator(self).pack(fill="x", padx=10, pady=6)

        ctrl = ttk.LabelFrame(self, text="Dieu khien nhanh (theo ID)")
        ctrl.pack(fill="x", padx=10, pady=8)

        ttk.Label(ctrl, text="ID server:").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        self.id_var = tk.StringVar()
        ttk.Entry(ctrl, textvariable=self.id_var, width=8).grid(row=0, column=1, sticky="w", padx=8, pady=4)
        ttk.Button(ctrl, text="Tat server (theo ID)", command=self._stop_by_id).grid(
            row=0, column=2, sticky="w", padx=8, pady=4)

        ttk.Label(ctrl, text="Ten nguoi choi:").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        self.player_var = tk.StringVar()
        ttk.Entry(ctrl, textvariable=self.player_var, width=15).grid(row=1, column=1, sticky="w", padx=8, pady=4)

        btn_row = ttk.Frame(ctrl)
        btn_row.grid(row=2, column=0, columnspan=3, sticky="w", padx=8, pady=6)
        ttk.Button(btn_row, text="Cap OP", command=self._op_by_id).pack(side="left", padx=4)
        ttk.Button(btn_row, text="Ban nguoi choi", command=self._ban_by_id).pack(side="left", padx=4)

        self._refresh_rows()
        self._poll()

    def _name_by_id(self, id_str):
        try:
            idx = int(id_str.strip())
        except ValueError:
            messagebox.showerror("Loi", "ID khong hop le")
            return None
        names = list(self.app.servers.keys())
        if idx < 1 or idx > len(names):
            messagebox.showerror("Loi", "Khong tim thay server voi ID nay")
            return None
        return names[idx - 1]

    def _stop_by_id(self):
        name = self._name_by_id(self.id_var.get())
        if not name:
            return
        rs = self.app.running.get(name)
        if rs and rs.is_running():
            rs.stop()
            messagebox.showinfo("Xong", f"Da gui lenh tat server '{name}' (ID {self.id_var.get()})")
            return
        entry = self.app.servers.get(name, {})
        pid = entry.get("pid")
        if pid and is_pid_alive(pid):
            if force_kill_pid(pid):
                messagebox.showinfo("Xong", f"Da tat cuong buc server '{name}' (PID {pid})")
            else:
                messagebox.showerror("Loi", "Khong the tat tien trinh nay")
        else:
            messagebox.showinfo("Thong bao", f"Server '{name}' hien khong chay")

    def _op_by_id(self):
        name = self._name_by_id(self.id_var.get())
        if not name:
            return
        player = self.player_var.get().strip()
        if not player:
            messagebox.showwarning("Canh bao", "Nhap ten nguoi choi truoc")
            return
        entry = self.app.servers.get(name, {})
        rs = self.app.running.get(name)
        if rs and rs.is_running():
            rs.send_command(f"op {player}")
        else:
            add_op_offline(entry["path"], player)
        set_player_flag(entry, player, "op", True)
        save_servers(self.app.servers)
        messagebox.showinfo("Xong", f"Da cap OP cho '{player}' tren server '{name}'")

    def _ban_by_id(self):
        name = self._name_by_id(self.id_var.get())
        if not name:
            return
        player = self.player_var.get().strip()
        if not player:
            messagebox.showwarning("Canh bao", "Nhap ten nguoi choi truoc")
            return
        rs = self.app.running.get(name)
        if not (rs and rs.is_running()):
            messagebox.showwarning("Canh bao", f"Server '{name}' can dang chay de ban nguoi choi")
            return
        rs.send_command(f"ban {player}")
        entry = self.app.servers.get(name, {})
        set_player_flag(entry, player, "ban", True)
        save_servers(self.app.servers)
        messagebox.showinfo("Xong", f"Da ban '{player}' tren server '{name}'")

    def _refresh_rows(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        for i, name in enumerate(self.app.servers.keys(), start=1):
            color, status_text = get_status_color(self.app, name)
            row = ttk.Frame(self.list_frame)
            row.pack(fill="x", pady=2)
            canvas = tk.Canvas(row, width=14, height=14, highlightthickness=0)
            canvas.pack(side="left", padx=(0, 6))
            canvas.create_oval(2, 2, 12, 12, fill=color, outline=color)
            ttk.Label(row, text=f"ID {i}  -  {name}   ({status_text})").pack(side="left")

    def _poll(self):
        if not self.winfo_exists():
            return
        self._refresh_rows()
        self.after(2000, self._poll)


# ---------------------------------------------------------------------------
# App chinh
# ---------------------------------------------------------------------------
class ServerManagerApp(tk.Tk):
    
    def _get_public_ip(self):
        try:
            with urllib.request.urlopen(
                "https://api.ipify.org",
                timeout=5
            ) as response:
                return response.read().decode().strip()

        except Exception as e:
            print("[NETWORK] Khong lay duoc Public IP:", e)
            return "N/A"


    def _check_possible_cgnat(self):
        """
        Kiem tra nhanh xem mang co dau hieu CGNAT/NAT hay khong.

        Luu y:
        Day la kiem tra nhanh, khong the xac nhan 100%
        CGNAT neu chua biet WAN IP cua router.
        """

        try:
            hostname = socket.gethostname()

            local_ip = socket.gethostbyname(hostname)

            public_ip = self._get_public_ip()

            print("[NETWORK] Local IP :", local_ip)
            print("[NETWORK] Public IP:", public_ip)

            if not public_ip:
                return "unknown"

            try:
                ip = ipaddress.ip_address(local_ip)
            except ValueError:
                return "unknown"

            if not ip.is_private:
                return "public"

            print("[NETWORK] May dang nam sau NAT.")

            return "nat"

        except Exception as e:
            print("[NETWORK] Check error:", e)
            return "unknown"

    def _get_system_usage(self):
        """Lay CPU/RAM usage hien tai; cap nhat moi lan dashboard poll."""
        try:
            cpu = float(psutil.cpu_percent(interval=None))
        except Exception:
            cpu = 0.0
        try:
            ram = float(psutil.virtual_memory().percent)
        except Exception:
            ram = 0.0
        return cpu, ram

    def _update_dashboard(self):
        auto_resize_buttons(self)

        total = len(self.servers)

        online = 0

        for rs in self.running.values():
            if rs.is_running():
                online += 1
    
        self.server_card.configure(
            text=str(total)
        )


        self.cpu_card.configure(
            text=f"{psutil.cpu_percent():.0f}%"
        )

        ram = psutil.virtual_memory()

        self.ram_card.configure(
            text=f"{ram.percent:.0f}%"
        )

        public_ip = self._get_public_ip()

        getattr(self, "public_ip_card", None) and getattr(self, "public_ip_card", None) and self.public_ip_card.configure(
            text=public_ip
        )

        self.after(750, self._update_dashboard)
    
    
    def _start_server(self):
        name = self._current_name()

        if not name:
            messagebox.showinfo(
                "Thong bao",
                "Chon mot server truoc"
            )
            return

        if name in self.running and self.running[name].is_running():
            messagebox.showinfo(
                "Thong bao",
                "Server nay dang chay roi"
            )
            return

        entry = self.servers[name]

        try:
            # =========================
            # LAY THU MUC SERVER
            # =========================

            server_path = os.path.abspath(
                os.path.expanduser(
                    str(entry.get("path", "")).strip()
                )
            )

            if not server_path:
                messagebox.showerror(
                    "Loi",
                    "Server chua co duong dan thu muc."
                )
                return

            if not os.path.isdir(server_path):
                messagebox.showerror(
                    "Loi",
                    f"Thu muc server khong ton tai:\n\n{server_path}"
                )
                return

            # =========================
            # PAPER
            # =========================

            if entry.get("type") == "paper":

                jar = str(
                    entry.get("jar", "server.jar")
                ).strip()

                jar_path = jar

                if not os.path.isabs(jar_path):
                    jar_path = os.path.join(
                        server_path,
                        jar_path
                    )

                jar_path = os.path.abspath(jar_path)

                if not os.path.isfile(jar_path):
                    messagebox.showerror(
                        "Loi",
                        f"Khong tim thay file server:\n\n{jar_path}"
                    )
                    return

                cmd = [
                    "java",
                    f"-Xms{entry.get('xms', '1G')}",
                    f"-Xmx{entry.get('xmx', '2G')}",
                    "-jar",
                    os.path.basename(jar_path),
                    "nogui"
                ]

                cwd = os.path.dirname(jar_path)

            # =========================
            # CUSTOM
            # =========================

            else:

                launch_file = str(
                    entry.get("launch_file", "")
                ).strip()

                if not launch_file:
                    messagebox.showerror(
                        "Loi",
                        "Chua co launch_file."
                    )
                    return

                full_launch = launch_file

                if not os.path.isabs(full_launch):
                    full_launch = os.path.join(
                        server_path,
                        full_launch
                    )

                full_launch = os.path.abspath(
                    full_launch
                )

                if not os.path.isfile(full_launch):
                    messagebox.showerror(
                        "Loi",
                        f"Khong tim thay file launch:\n\n{full_launch}"
                    )
                    return

                cwd = os.path.dirname(full_launch)

                if full_launch.lower().endswith(".jar"):

                    cmd = [
                        "java",
                        f"-Xms{entry.get('xms', '1G')}",
                        f"-Xmx{entry.get('xmx', '2G')}",
                        "-jar",
                        os.path.basename(full_launch),
                        "nogui"
                    ]

                elif full_launch.lower().endswith(".bat"):

                    cmd = [
                        "cmd",
                        "/c",
                        os.path.basename(full_launch)
                    ]

                elif full_launch.lower().endswith(".cmd"):

                    cmd = [
                        "cmd",
                        "/c",
                        os.path.basename(full_launch)
                    ]

                else:

                    cmd = [
                        full_launch
                    ]

            # =========================
            # DEBUG
            # =========================

            print("================================")
            print("START SERVER")
            print("NAME :", name)
            print("CMD  :", cmd)
            print("CWD  :", cwd)
            print("================================")

            # =========================
            # WINDOWS FLAGS
            # =========================

            creation_flags = 0

            if hasattr(
                subprocess,
                "CREATE_NO_WINDOW"
            ):
                creation_flags |= (
                    subprocess.CREATE_NO_WINDOW
                )

            if hasattr(
                subprocess,
                "CREATE_NEW_PROCESS_GROUP"
            ):
                creation_flags |= (
                    subprocess.CREATE_NEW_PROCESS_GROUP
                )

            # =========================
            # START
            # =========================

            proc = subprocess.Popen(
                cmd,
                cwd=TUNNEL_ROOT,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                creationflags=creation_flags
            )

            self.running[name] = RunningServer(
                name,
                proc
            )

            entry["pid"] = proc.pid

            save_servers(
                self.servers
            )

            self.console.delete(
                "1.0",
                tk.END
            )

            self.console.insert(
                tk.END,
                f"=== Dang khoi dong '{name}' ===\n"
            )

            self.console.insert(
                tk.END,
                f"PID: {proc.pid}\n"
            )

            self.console.insert(
                tk.END,
                f"Folder: {cwd}\n"
            )

            self.console.insert(
                tk.END,
                "Command: "
                + " ".join(cmd)
                + "\n\n"
            )

            if hasattr(
                self,
                "status_label"
            ):
                self.status_label.configure(
                    text="🟢 Server running",
                    text_color="#22C55E"
                )

        except FileNotFoundError as e:

            messagebox.showerror(
                "Loi",
                "Khong tim thay Java hoac file server.\n\n"
                f"{e}"
            )

        except PermissionError as e:

            messagebox.showerror(
                "Loi",
                "Khong co quyen chay server.\n\n"
                f"{e}"
            )

        except Exception as e:

            messagebox.showerror(
                "Loi",
                f"Khong the khoi dong server:\n\n{e}"
            )
    
    def __init__(self):
        super().__init__()

        self.title("Minecraft Server Manager")
        self.geometry("1600x900")

        self.servers = load_servers()
        self.running = {}

        self.tunnel_processes = {}
        self.public_addresses = {}
        self._secondary_windows = []

        ctk.set_appearance_mode(APP_SETTINGS["appearance"])

        self._build_ui()
        self._refresh_list()

        self.after(750, self._update_dashboard)
        self.after(150, self._poll_logs)
        self.after(5000, self._poll_always_op)
        self.after(2000, self._poll_auto_restart)

        self.protocol("WM_DELETE_WINDOW", self._on_close)
    # --- Preferences / theme / language ---
    def _register_secondary(self, window):
        self._secondary_windows.append(window)
        try:
            window.bind("<Destroy>", lambda e, w=window: self._forget_secondary(w), add="+")
        except Exception:
            pass
        return window

    def _forget_secondary(self, window):
        self._secondary_windows = [
            w for w in self._secondary_windows
            if w is not window and w.winfo_exists()
        ]

    def set_appearance(self, mode, refresh_dialogs=True):
        if mode not in ("Dark", "Light"):
            mode = "Dark"
        APP_SETTINGS["appearance"] = mode
        ctk.set_appearance_mode(mode)
        self._apply_main_theme(mode)
        if refresh_dialogs:
            for window in list(self._secondary_windows):
                try:
                    if window.winfo_exists():
                        apply_secondary_theme(window, mode)
                except Exception:
                    pass

    def _apply_main_theme(self, mode=None):
        """Live light/dark theme for the main window, similar to modern chat apps."""
        p = theme_palette(mode)
        mapping = {
            WINDOW_BG: p["window"], SIDEBAR_BG: p["surface"], CARD: p["surface"],
            "#20242D": p["surface"], "#1F2937": p["entry"], "#18181B": p["window"],
            "#111827": p["surface"],
        }
        def walk(w):
            try:
                if isinstance(w, ctk.CTkFrame):
                    old = w.cget("fg_color")
                    if isinstance(old, str) and old in mapping: w.configure(fg_color=mapping[old])
                    elif isinstance(old, tuple) and old[0] in mapping: w.configure(fg_color=(mapping.get(old[0],old[0]), mapping.get(old[1],old[1])))
                elif isinstance(w, ctk.CTkLabel):
                    # Re-map neutral text for Light/Dark while preserving intentional accents.
                    old = w.cget("text_color")
                    neutral_colors = {
                        "white", "#FFFFFF", TEXT,
                        "#E5E7EB", "#D1D5DB", "#A1A1AA",
                        "gray60", "gray70", "gray80", "grey60", "grey70", "grey80",
                    }
                    if old in neutral_colors:
                        w.configure(text_color=p["text"])
                elif isinstance(w, tk.Listbox):
                    w.configure(bg=p["entry"], fg=p["text"], selectbackground=p["button"])
                elif isinstance(w, tk.Text):
                    w.configure(bg=p["console"], fg=p["console_text"])
            except Exception: pass
            try:
                for c in w.winfo_children(): walk(c)
            except Exception: pass
        walk(self)

    def apply_preferences(self, appearance, language):
        APP_SETTINGS["appearance"] = appearance if appearance in ("Dark", "Light") else "Dark"
        APP_SETTINGS["language"] = language if language in LANGUAGES else "Tiếng Việt"
        save_app_settings(APP_SETTINGS)
        self.set_appearance(APP_SETTINGS["appearance"])
        self._refresh_language()
        messagebox.showinfo(tr("settings"), tr("saved"))

    def _open_settings(self):
        self._register_secondary(AppSettingsDialog(self, self, language_only=False))

    def _refresh_language(self):
        localize_tree(self, APP_SETTINGS["language"])
        for key, widget in getattr(self, "_language_widgets", {}).items():
            try:
                widget.configure(text=tr(key))
            except Exception:
                pass
        for window in list(getattr(self, "_secondary_windows", [])):
            try:
                if window.winfo_exists():
                    localize_tree(window, APP_SETTINGS["language"])
                    if hasattr(window, "refresh_language"):
                        window.refresh_language()
            except Exception:
                pass
        try:
            self.dashboard_title.configure(text=tr("no_server"))
            self.selected_label.configure(text=tr("no_server"))
            self.console_frame_title.configure(text=tr("console"))
            self.cmd_entry.configure(
                placeholder_text="Type a Minecraft command..."
                if APP_SETTINGS["language"] == "English"
                else "Nhập lệnh Minecraft..."
            )
        except Exception:
            pass

    # --- UI ---
    def _build_ui(self):
        left = ctk.CTkFrame(
            self,
            width=250,
            fg_color="#111827",
            corner_radius=0,
        )

        left.pack(
            side="left",
            fill="y",
        )

        ctk.CTkLabel(
            left,
            text="🔥 BAOTOP HOST",
            text_color="#60A5FA",
            font=("Arial", 24, "bold")
        ).pack(
            pady=(25, 20)
        )

        utility_bar = ctk.CTkFrame(left, fg_color="transparent")
        utility_bar.pack(fill="x", padx=12, pady=(0, 8))

        self.settings_btn = ctk.CTkButton(
            utility_bar, text=tr("settings_button"), height=38, corner_radius=9,
            fg_color="#374151", hover_color="#4B5563", command=self._open_settings)
        self.settings_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self._language_widgets = {"settings_button": self.settings_btn}

        self.listbox = tk.Listbox(
            left,
            width=28,
            height=22,
            bg="#1F2937",
            fg="white",
            selectbackground="#2563EB",
            relief="flat",
            bd=0
        )
        self.listbox.pack(fill="y", expand=True, pady=6)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        menu = ctk.CTkFrame(
            left,
            fg_color="transparent"
        )

        menu.pack(
            fill="x",
            padx=12,
            pady=8
        )

        self.new_server_btn = ctk.CTkButton(
            menu,
            text=tr("new_server"),
            height=42,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self._new_server
        ).pack(fill="x", pady=4)

        self.open_folder_btn = ctk.CTkButton(
            menu,
            text=tr("open_folder"),
            height=42,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self._open_folder
        ).pack(fill="x", pady=4)

        self.plugins_btn = ctk.CTkButton(
            menu,
            text=tr("plugins"),
            height=42,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self._open_plugins_folder
        ).pack(fill="x", pady=4)

        self.address_btn = ctk.CTkButton(
            menu,
            text=tr("address"),
            height=42,
            fg_color="#F59E0B",
            hover_color="#D97706",
            command=self._edit_server
        ).pack(fill="x", pady=4)

        self.advanced_btn = ctk.CTkButton(
            menu,
            text=tr("advanced"),
            height=42,
            fg_color="#7C3AED",
            hover_color="#6D28D9",
            command=self._open_admin_dialog
        ).pack(fill="x", pady=4)

        self.delete_btn = ctk.CTkButton(
            menu,
            text=tr("delete"),
            height=42,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=self._delete_server
        ).pack(fill="x", pady=4)

        ctk.CTkLabel(
            menu,
            text="────────────",
            text_color="gray60"
        ).pack(pady=8)

        self.overview_btn = ctk.CTkButton(
            menu,
            text=tr("overview"),
            height=42,
            fg_color="#374151",
            hover_color="#4B5563",
            command=self._open_servers_overview
        ).pack(fill="x", pady=4)

        self._language_widgets.update({
            "new_server": self.new_server_btn,
            "open_folder": self.open_folder_btn,
            "plugins": self.plugins_btn,
            "address": self.address_btn,
            "advanced": self.advanced_btn,
            "delete": self.delete_btn,
            "overview": self.overview_btn,
        })

        right = ctk.CTkFrame(
            self,
            fg_color="#18181B",
            corner_radius=0,
        )

        right.pack(
            side="right",
            fill="both",
            expand=True,
        )

        # ==========================
        # Dashboard
        # ==========================

        dashboard = ctk.CTkFrame(
            right,
            fg_color="#20242D",
            corner_radius=12
        )

        dashboard.pack(
            fill="x",
            padx=15,
            pady=(15,10)
        )

        top = ctk.CTkFrame(
            dashboard,
            fg_color="transparent"
        )

        top.pack(fill="x", padx=15, pady=(12,6))

        self.dashboard_title = ctk.CTkLabel(
            top,
            text="🖥 No Server Selected",
            font=("Arial",22,"bold")
        )

        self.dashboard_title.pack(side="left")

        self.dashboard_status = ctk.CTkLabel(
            top,
            text="🔴 Offline",
            text_color="#EF4444",
            font=("Arial",18,"bold")
        )

        self.dashboard_status.pack(side="right")

        cards = ctk.CTkFrame(
            dashboard,
            fg_color="transparent"
        )

        cards.pack(fill="x", padx=10, pady=(0,12))

        self.card_servers = ctk.CTkFrame(cards, corner_radius=10)
        self.card_servers.pack(side="left", expand=True, fill="both", padx=4)

        ctk.CTkLabel(
            self.card_servers,
            text="Servers",
            font=("Arial",14)
        ).pack(pady=(10,0))

        self.server_card = ctk.CTkLabel(
            self.card_servers,
            text="0",
            font=("Arial",28,"bold")
        )

        self.server_card.pack(pady=(0,10))

        self.card_players = ctk.CTkFrame(cards, corner_radius=10)
        self.card_players.pack(side="left", expand=True, fill="both", padx=4)

        ctk.CTkLabel(
            self.card_players,
            text="Players",
            font=("Arial",14)
        ).pack(pady=(10,0))

        self.player_card = ctk.CTkLabel(
            self.card_players,
            text="0",
            font=("Arial",28,"bold")
        )

        self.player_card.pack(pady=(0,10))

        self.card_ram = ctk.CTkFrame(cards, corner_radius=10)
        self.card_ram.pack(side="left", expand=True, fill="both", padx=4)

        ctk.CTkLabel(
           self.card_ram,
           text="RAM",
           font=("Arial",14)
        ).pack(pady=(10,0))

        self.ram_card = ctk.CTkLabel(
            self.card_ram,
            text="0 MB",
            font=("Arial",28,"bold")
        )

        self.ram_card.pack(pady=(0,10))

        self.card_cpu = ctk.CTkFrame(cards, corner_radius=10)
        self.card_cpu.pack(side="left", expand=True, fill="both", padx=4)

        ctk.CTkLabel(
           self.card_cpu,
           text="CPU",
           font=("Arial",14)
        ).pack(pady=(10,0))

        self.cpu_card = ctk.CTkLabel(
            self.card_cpu,
            text="0%",
            font=("Arial",28,"bold")
        )

        self.cpu_card.pack(pady=(0,10))

        # =========================
        # HEADER
        # =========================

        header = ctk.CTkFrame(
            right,
            fg_color="#27272A",
            corner_radius=12
        )

        header.pack(
            fill="x",
            padx=15,
            pady=15
        )

        self.selected_label = ctk.CTkLabel(
            header,
            text="🖥 No Server Selected",
            text_color="white",
            font=("Arial",22,"bold")
        )

        self.selected_label.pack(
            side="left",
            padx=20,
            pady=18
        )

        self.start_btn = ctk.CTkButton(
            header,
            text=tr("start"),
            width=110,
            height=38,
            fg_color="#22C55E",
            hover_color="#16A34A",
            command=self._start_server
        )

        self.start_btn.pack(
            side="right",
            padx=(6,20)
        )

        self.stop_btn = ctk.CTkButton(
            header,
            text=tr("stop"),
            width=110,
            height=38,
            fg_color="#EF4444",
            hover_color="#DC2626",
            command=self._stop_server
        )

        self.stop_btn.pack(
            side="right",
            padx=6
        )

        self.continuous_stop_btn = ctk.CTkButton(
            header, text=tr("no_auto"), width=105, height=38,
            fg_color="#6B7280", hover_color="#4B5563",
            command=self._stop_continuous
        )
        self.continuous_stop_btn.pack(side="right", padx=6)

        self.continuous_start_btn = ctk.CTkButton(
            header, text=tr("auto"), width=105, height=38,
            fg_color="#F59E0B", hover_color="#D97706",
            command=self._start_server_continuous
        )
        self.continuous_start_btn.pack(side="right", padx=6)

        # =========================
        # ADDRESS
        # =========================

        address = ctk.CTkFrame(
            right,
            fg_color="#27272A",
            corner_radius=12
        )

        address.pack(
            fill="x",
            padx=15,
            pady=(0,10)
        )

        self.address_var = tk.StringVar(value="")

        ctk.CTkLabel(
            address,
            textvariable=self.address_var,
            text_color="#60A5FA",
            font=("Arial",15,"bold")
        ).pack(
            side="left",
            padx=20,
            pady=12
        )

        ctk.CTkButton(
            address,
            text="LAN",
            width=80,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self._copy_lan_address
        ).pack(
            side="right",
            padx=8
        )

        ctk.CTkButton(
            address,
            text="Localhost",
            width=100,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self._copy_localhost_address
        ).pack(
            side="right",
            padx=8
        )

        # =========================
        # DESCRIPTION
        # =========================

        self.desc_display_var = tk.StringVar(value="")

        self.desc_display_label = ctk.CTkLabel(
            right,
            textvariable=self.desc_display_var,
            text_color="gray80",
            anchor="w",
            font=("Arial",14)
        )

        self.desc_display_label.pack(
            fill="x",
            padx=20,
            pady=(0,10)
        )

        # =========================
        # CONSOLE
        # =========================

        console_frame = ctk.CTkFrame(
            right,
            fg_color="#27272A",
            corner_radius=12
        )

        console_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0,15)
        )

        self.console_frame_title = ctk.CTkLabel(
            console_frame,
            text=tr("console"),
            text_color="#60A5FA",
            font=("Arial",18,"bold")
        )
        self.console_frame_title.pack(
            anchor="w",
            padx=15,
            pady=(15,10)
        )

        self.console = ctk.CTkTextbox(
            console_frame,
            fg_color="#0F172A",
            text_color="#22C55E",
            font=("Consolas",13),
            wrap="word"
        )

        self.console.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0,15)
        )

        # =========================
        # COMMAND BAR
        # =========================

        bottom = ctk.CTkFrame(
            right,
            fg_color="transparent"
        )

        bottom.pack(
            fill="x",
            padx=15,
            pady=(0,15)
        )

        self.cmd_var = tk.StringVar()

        self.cmd_entry = ctk.CTkEntry(
            bottom,
            textvariable=self.cmd_var,
            placeholder_text="Type a Minecraft command..."
        )

        self.cmd_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0,10)
        )

        self.cmd_entry.bind(
            "<Return>",
            lambda e: self._send_command()
        )

        self.send_btn = ctk.CTkButton(
            bottom,
            text=tr("send"),
            width=110,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self._send_command
        ).pack(
            side="left",
            padx=4
        )

        self.clear_btn = ctk.CTkButton(
            bottom,
            text=tr("clear"),
            width=100,
            fg_color="#374151",
            hover_color="#4B5563",
            command=lambda: self.console.delete("1.0", "end")
        ).pack(
            side="left"
        )

        # =========================
        # STATUS BAR
        # =========================

        self.status_bar = ctk.CTkFrame(
            right,
            fg_color="#111827",
            height=40,
            corner_radius=10
        )

        self.status_bar.pack(
            fill="x",
            padx=15,
            pady=(0,15)
        )

        self._language_widgets.update({
            "start": self.start_btn,
            "stop": self.stop_btn,
            "no_auto": self.continuous_stop_btn,
            "auto": self.continuous_start_btn,
            "send": self.send_btn,
            "clear": self.clear_btn,
        })

        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="🔴 No server running",
            text_color="#EF4444",
            font=("Arial",13,"bold")
        )

        self.status_label.pack(
            side="left",
            padx=15,
            pady=8
        )

        self.time_label = ctk.CTkLabel(
            self.status_bar,
            text="BAOTOP Host",
            text_color="gray80"
        )

        self.time_label.pack(
            side="right",
            padx=15
        )

    # ==========================
    # DASHBOARD
    # ==========================

    def _create_stat_card(self, parent, title, value, color):

        card = ctk.CTkFrame(
            parent,
            fg_color="#27272A",
            corner_radius=12
        )

        card.pack(
            side="left",
            expand=True,
            fill="both",
            padx=8
        )

        ctk.CTkLabel(
            card,
            text=title,
            text_color="gray80",
            font=("Arial",15)
        ).pack(
            pady=(18,5)
        )

        value_label = ctk.CTkLabel(
            card,
            text=value,
            text_color=color,
            font=("Arial",30,"bold")
        )

        value_label.pack(
            pady=(0,18)
        )

        return value_label

    def _current_name(self):
        sel = self.listbox.curselection()
        if not sel:
            return None
        return self.listbox.get(sel[0])

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        for name in sorted(self.servers.keys()):
            self.listbox.insert(tk.END, name)
            entry = self.servers.get(name, {})
            color = entry.get("description_color")
            if color:
                self.listbox.itemconfig(tk.END, fg=color)

    def _get_public_address(self, name):
        try:
            entry = self.servers.get(name, {})
            port = entry.get("port", "25565")

            try:
                with urllib.request.urlopen(
                    "https://api.ipify.org",
                    timeout=5
                ) as response:
                    public_ip = response.read().decode().strip()
            except Exception:
                public_ip = "Khong lay duoc IP"

            return f"{public_ip}:{port}"

        except Exception:
            return "Khong lay duoc dia chi"

    def _on_select(self, event=None):
        name = self._current_name()
        if name:
            self.selected_label.configure(text=f"🖥 Server: {name}")
            entry = self.servers.get(name, {})
            port = entry.get("port", "25565")
            lan_ip = get_lan_ip()
            self.address_var.set(f"Dia chi: localhost:{port}  |  LAN: {lan_ip}:{port}")

            public_address = self._get_public_address(name)

            self.address_var.set(
                f"Local: localhost:{port} | "
                f"LAN: {lan_ip}:{port} | "
                f"Public: {public_address}"
)

            desc = entry.get("description", "").strip()
            desc_color = entry.get("description_color", "#555555")
            self.desc_display_var.set(desc if desc else "")
            self.desc_display_label.configure(text_color=desc_color if desc else "#555555")
            self.console.delete("1.0", tk.END)
        else:
            self.address_var.set("")
            self.desc_display_var.set("")

    def _edit_server(self):
        name = self._current_name()
        if not name:
            messagebox.showinfo("Thong bao", "Chon mot server truoc")
            return
        if name in self.running and self.running[name].is_running():
            messagebox.showwarning("Canh bao", "Hay Stop server truoc khi sua cau hinh")
            return

        def on_saved(server_name, updated_entry):
            self.servers[server_name] = updated_entry
            save_servers(self.servers)
            self._on_select()

        EditServerDialog(self, name, self.servers[name], on_saved)

    def _open_admin_dialog(self):
        name = self._current_name()
        if not name:
            messagebox.showinfo("Thong bao", "Chon mot server truoc")
            return
        entry = self.servers[name]
        if entry.get("type") != "paper":
            messagebox.showinfo(
                "Thong bao",
                "Chuc nang nay hien chi ho tro server loai Paper (dung server.properties)."
            )
            return
        ServerAdminDialog(self, name, entry, lambda: self.running.get(name), self)

    def _open_servers_overview(self):
        pw = simpledialog.askstring("Mat khau", "Nhap mat khau de vao tab Servers:", show="*", parent=self)
        if pw is None:
            return
        if pw != SERVERS_TAB_PASSWORD:
            messagebox.showerror("Loi", "Mat khau khong dung")
            return
        ServersOverviewDialog(self, self)

    def _copy_lan_address(self):
        name = self._current_name()
        if not name:
            return
        port = self.servers[name].get("port", "25565")
        addr = f"{get_lan_ip()}:{port}"
        self.clipboard_clear()
        self.clipboard_append(addr)
        messagebox.showinfo("Da copy", f"Da copy dia chi: {addr}")

    def _copy_localhost_address(self):
        name = self._current_name()
        if not name:
            return
        port = self.servers[name].get("port", "25565")
        addr = f"localhost:{port}"
        self.clipboard_clear()
        self.clipboard_append(addr)
        messagebox.showinfo("Da copy", f"Da copy dia chi: {addr}")

    # --- Tao / xoa ---
    def _new_server(self):
        def on_created(name, entry):
            self.servers[name] = entry
            save_servers(self.servers)
            self._refresh_list()

        NewServerDialog(self, on_created)

    def _delete_server(self):
        name = self._current_name()
        if not name:
            return
        if name in self.running and self.running[name].is_running():
            messagebox.showerror("Loi", "Hay Stop server truoc khi xoa")
            return
        if not messagebox.askyesno("Xac nhan", f"Xoa server '{name}'? (Neu la server do app tu tao, thu muc se bi xoa luon)"):
            return
        entry = self.servers.get(name, {})
        if entry.get("type") == "paper":
            if not safe_rmtree(entry["path"]):
                messagebox.showwarning(
                    "Canh bao",
                    f"Khong the xoa het thu muc server (co the dang bi khoa boi tien trinh khac,\n"
                    f"vi du Java chua giai phong file, hoac antivirus dang quet):\n{entry['path']}\n\n"
                    f"Server van se duoc go khoi danh sach. Neu muon tao lai server voi TEN NAY,\n"
                    f"hay doi it phut roi thu lai, hoac tu xoa thu cong thu muc tren."
                )
        del self.servers[name]
        save_servers(self.servers)
        self._refresh_list()
        self.console.delete("1.0", tk.END)
        self.selected_label.configure(text="Chua chon server")

    def _open_folder(self):
        name = self._current_name()
        if not name:
            return
        path = self.servers[name]["path"]
        os.startfile(path)

    def _open_plugins_folder(self):
        name = self._current_name()
        if not name:
            return
        entry = self.servers[name]
        candidates = ["plugins", "mods"]
        for c in candidates:
            p = os.path.join(entry["path"], c)
            if os.path.isdir(p):
                os.startfile(p)
                return
        os.makedirs(os.path.join(entry["path"], "plugins"), exist_ok=True)
        os.startfile(os.path.join(entry["path"], "plugins"))

    # --- Start / stop / console ---
    def _start_tunnel(self, name, port):
        if name in self.tunnel_processes:
            proc = self.tunnel_processes[name]

            if proc.poll() is None:
                return

        if not os.path.exists(PLAYIT_EXE):
            self.console.insert(
                tk.END,
                "\n[TUNNEL] Khong tim thay playit.exe\n"
            )
            self.console.see(tk.END)
            return

        try:
            self.console.insert(
                tk.END,
                f"\n[TUNNEL] Dang khoi dong Playit cho '{name}'...\n"
            )
            self.console.see(tk.END)

            proc = subprocess.Popen(
                [PLAYIT_EXE],
                cwd=TUNNEL_ROOT,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=False,
                bufsize=0,
                creationflags=(
                    getattr(
                        subprocess,
                        "CREATE_NEW_PROCESS_GROUP",
                        0
                    )
                )
            )

            self.tunnel_processes[name] = proc

            threading.Thread(
                target=self._tunnel_reader,
                args=(name, proc),
                daemon=True
            ).start()

        except Exception as e:
            self.console.insert(
                tk.END,
                f"[TUNNEL] Loi: {e}\n"
            )
            self.console.see(tk.END)

    def _tunnel_reader(self, name, proc):

        try:
            while proc.poll() is None:
 
                raw_line = proc.stdout.readline()

                if not raw_line:
                    continue

                line = raw_line.decode(
                    "utf-8",
                    errors="replace"
                ).rstrip()

                # Đưa việc cập nhật GUI về Tkinter thread
                self.after(
                    0,
                    lambda n=name, l=line:
                        self._handle_tunnel_line(n, l)
                )

        except Exception as e:

            self.after(
                0,
                lambda err=str(e):
                    self.console.insert(
                        tk.END,
                        f"[TUNNEL] Read error: {err}\n"
                    )
            )

    def _handle_tunnel_line(self, name, line):

        self.console.insert(
            tk.END,
            f"[PLAYIT] {line}\n"
        )

        self.console.see(tk.END)

        match = re.search(
            r'([a-zA-Z0-9.-]+\.playit\.gg(?::\d+)?)',
            line
        )

        if not match:
            return

        address = match.group(1)

        self.public_addresses[name] = address

        entry = self.servers.get(name)

        if entry is not None:
            entry["public_address"] = address
            save_servers(self.servers)

        self.address_var.set(
            f"Public: {address}"
        )

        self.status_label.configure(
            text=f"🟢 {address}",
            text_color="#22C55E"
        )

        self.console.insert(
             tk.END,
            f"\n🌐 PUBLIC ADDRESS: {address}\n"
        )

        self.console.see(tk.END)
     
    def _append_tunnel_console(self, name, line):

        self.console.insert(
            tk.END,
            f"[TUNNEL] {line}\n"
        )

        self.console.see(tk.END)

        # Tim public address trong output tunnel
        match = re.search(
            r"(?:https?://)?([A-Za-z0-9.-]+(?::\d+)?)",
            line
        )

        if match:

            address = match.group(1)

            if (
                "." in address
                and "127.0.0.1" not in address
                and "localhost" not in address
            ):

                self.public_addresses[name] = address

                self.console.insert(
                    tk.END,
                    f"[PUBLIC] {address}\n"
                )

                self.console.see(tk.END)               

    def _start_server(self, auto_restart=False):
        name = self._current_name()
        if not name:
            messagebox.showinfo("Thong bao", "Chon mot server truoc")
            return
        if name in self.running and self.running[name].is_running():
            messagebox.showinfo("Thong bao", "Server nay dang chay roi")
            return

        entry = self.servers[name]
        try:
            if entry["type"] == "paper":
                cmd = ["java", f"-Xms{entry['xms']}", f"-Xmx{entry['xmx']}",
                       "-jar", entry["jar"], "nogui"]
                cwd = entry["path"]
            else:  # custom
                launch_file = entry["launch_file"]
                full_launch = launch_file if os.path.isabs(launch_file) else os.path.join(entry["path"], launch_file)
                if full_launch.lower().endswith(".jar"):
                    cmd = ["java", f"-Xms{entry['xms']}", f"-Xmx{entry['xmx']}",
                           "-jar", os.path.basename(full_launch), "nogui"]
                    cwd = os.path.dirname(full_launch)
                else:
                    cmd = [full_launch]
                    cwd = os.path.dirname(full_launch)

            creation_flags = 0
            if hasattr(subprocess, "CREATE_NO_WINDOW"):
                creation_flags |= subprocess.CREATE_NO_WINDOW
            if hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
                creation_flags |= subprocess.CREATE_NEW_PROCESS_GROUP

            proc = subprocess.Popen(
                cmd, cwd=cwd,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1,
                creationflags=creation_flags
            )
            self.running[name] = RunningServer(name, proc)
            try:
                port = int(entry.get("port", 25565))
            except Exception:
                port = 25565
                
            self.after(
                3000,
                lambda n=name, p=port:
                    self._start_tunnel(n, p)
                )
            

            self.after(
                2000,
                lambda n=name, p=port: self._start_tunnel(n, p)
            )
            entry["pid"] = proc.pid
            save_servers(self.servers)
            self.console.delete("1.0", tk.END)
            self.console.insert(tk.END, f"=== Dang khoi dong '{name}'" + (" (che do tu khoi dong)" if auto_restart else "") + " ===\n")
        except FileNotFoundError:
            messagebox.showerror("Loi", "Khong tim thay 'java'. Hay cai dat JDK va them vao PATH.")
        except Exception as e:
            messagebox.showerror("Loi", f"Khong the khoi dong server: {e}")

    def _start_server_continuous(self):
        name = self._current_name()
        if not name:
            messagebox.showinfo("Thong bao", "Chon mot server truoc")
            return
        rs = self._start_server(auto_restart=True)
        if rs is not None:
            messagebox.showinfo(
                "Da bat che do chay lien tuc",
                f"Server '{name}' se tu dong khoi dong lai neu bi crash/dung bat ngo."
            )

    def _stop_continuous(self):
        name = self._current_name()
        if not name:
            messagebox.showinfo("Thong bao", "Chon mot server truoc")
            return
        rs = self.running.get(name)
        if not rs:
            messagebox.showinfo("Thong bao", "Server chua chay.")
            return
        rs.auto_restart = False
        messagebox.showinfo("Da tat", f"Da tat che do tu khoi dong cho '{name}'.")


    def _stop_server(self):
        name = self._current_name()
        if not name or name not in self.running:
            return
        rs = self.running[name]
        if rs.is_running():
            rs.stop()
            self.console.insert(tk.END, "=== Dang gui lenh stop... ===\n")

    def _send_command(self):
        name = self._current_name()
        if not name or name not in self.running:
            return
        cmd = self.cmd_var.get().strip()
        if not cmd:
            return
        self.running[name].send_command(cmd)
        self.cmd_var.set("")

    def _poll_auto_restart(self):
        for name, rs in list(self.running.items()):
            if (not rs.is_running() and rs.auto_restart and not rs.intentional_stop
                    and not rs.restart_scheduled):
                rs.restart_scheduled = True
                if name == self._current_name():
                    self.console.insert(
                        "end",
                        f"=== Server '{name}' dung bat ngo; tu khoi dong lai sau 3 giay... ===\n"
                    )
                    self.console.see("end")
                self.after(3000, lambda n=name, old_rs=rs: self._try_auto_restart(n, old_rs))
        self.after(2000, self._poll_auto_restart)

    def _try_auto_restart(self, name, old_rs):
        if not old_rs.auto_restart or old_rs.intentional_stop:
            return
        if name in self.running and self.running[name].is_running():
            return
        new_rs = self._start_server(auto_restart=True) if name == self._current_name() else self._start_server_for_name(name, auto_restart=True)
        if new_rs is None:
            old_rs.restart_scheduled = False
        else:
            old_rs.restart_scheduled = False

    def _start_server_for_name(self, name, auto_restart=False):
        old_current = None
        try:
            old_current = self.listbox.curselection()
            names = list(self.servers.keys())
            idx = names.index(name)
            self.listbox.selection_clear(0, "end")
            self.listbox.selection_set(idx)
            self.listbox.activate(idx)
            self._on_select()
            return self._start_server(auto_restart=auto_restart)
        finally:
            pass


    def _poll_always_op(self):
        for name, rs in list(self.running.items()):
            if not rs.is_running():
                continue
            entry = self.servers.get(name, {})
            players = entry.get("players", {})
            for pname, flags in players.items():
                if flags.get("always_op"):
                    rs.send_command(f"op {pname}")
        self.after(30000, self._poll_always_op)

    def _poll_logs(self):
        current = self._current_name()
        for name, rs in list(self.running.items()):
            try:
                while True:
                    line = rs.log_queue.get_nowait()
                    if line == "__PROCESS_ENDED__":
                        if name == current:
                            self.console.insert(tk.END, f"=== Server '{name}' da dung ===\n")
                            self.console.see(tk.END)
                        continue
                    if name == current:
                        self.console.insert(tk.END, line + "\n")
                        self.console.see(tk.END)
            except queue.Empty:
                pass
        self.after(150, self._poll_logs)

    def _on_close(self):
        running_names = [n for n, rs in self.running.items() if rs.is_running()]
        if running_names:
            messagebox.showinfo(
                "Server van chay nen",
                "Cac server sau se TIEP TUC chay trong nen sau khi dong app:\n" +
                ", ".join(running_names) +
                "\n\nMo lai app va bam Stop (hoac dung tab Servers) de tat han."
            )
        self.destroy()


if __name__ == "__main__":
    if sys.platform != "win32":
        print("Luu y: app nay duoc thiet ke cho Windows (dung os.startfile).")
    app = ServerManagerApp()
    app.mainloop()
