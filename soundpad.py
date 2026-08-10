import ctypes
import json
import locale
import os
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import keyboard
import numpy as np
from scipy.signal import butter, sosfilt
import sounddevice as sd
import soundfile as sf
from tkinterdnd2 import DND_FILES, TkinterDnD

APP_DATA_DIR = os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), ".sys_pad_config"
)
CONFIG_FILE = os.path.join(APP_DATA_DIR, "config.json")
STARTUP_DIR = os.path.join(
    os.environ.get("APPDATA", ""),
    r"Microsoft\Windows\Start Menu\Programs\Startup",
)
SHORTCUT_PATH = os.path.join(STARTUP_DIR, "PythonSoundpadPro.lnk")

os.makedirs(APP_DATA_DIR, exist_ok=True)

# Словник локалізації
TRANSLATIONS = {
    "uk": {
        "tab_main": " 🎵 Саундпад ",
        "tab_settings": " ⚙️ Налаштування ",
        "list_frame": " Список звуків (Drag & Drop аудіофайлів сюди) ",
        "col_hotkey": "Клавіша",
        "col_file": "Файл",
        "col_vol": "Гучність",
        "col_loop": "Loop",
        "control_frame": " Налаштування обраного звуку ",
        "lbl_vol": "Гучність:",
        "btn_loop_on": "🔁 Loop: УВІМК",
        "btn_loop_off": "🔁 Loop: ВИМК",
        "btn_rebind": "Змінити клавішу",
        "btn_delete": "Видалити",
        "play_frame": " Ручний запуск ",
        "btn_play_both": "▶ / ⏹ Запустити/Зупинити (В обидва пристрої)",
        "btn_play_mic": "🎙 Лише в мікрофон",
        "btn_play_hp": "🎧 В навушники",
        "boost_frame": " Підсилення (Boost) та Потужні Баси ",
        "lbl_boost": "Загальний Буст (Gain):",
        "lbl_bass": "Потужний Бас (5 LVL):",
        "bass_off": "Рівень 0 (Вимк.)",
        "bass_lvl": "Рівень {}",
        "eq_frame": " Децибельний Еквалайзер ",
        "btn_reset_eq": "↺ Скинути EQ & Boost",
        "btn_hide_eq": "▲ Сховати EQ",
        "btn_show_eq": "▼ Показати EQ",
        "btn_add": "+ Додати файл",
        "btn_stop": "⏹ Зупинити все",
        "dev_frame": " Вибір аудіопристроїв ",
        "lbl_hp": "Навушники (C-Media):",
        "lbl_mic": "Мікрофон (VB-Cable):",
        "eq_opts_frame": " Параметри Еквалайзера та Звуку ",
        "chk_use_eq": "Увімкнути обробку еквалайзера та бусту",
        "chk_keep_global": "Застосовувати однакові налаштування EQ/Boost/Bass до ВСІХ файлів",
        "sys_frame": " Системні налаштування ",
        "chk_autostart": "Запускати програму разом з Windows",
        "lang_frame": " Мова інтерфейсу / Language ",
        "lbl_lang": "Оберіть мову:",
        "default_dev": "За замовчуванням",
        "warn_select_sound": "Спочатку оберіть звук зі списку!",
        "win_rebind_title": "Призначення клавіші",
        "win_rebind_lbl": "Введіть комбінацію (наприклад: num 1, f1, ctrl+alt+1):",
        "btn_save": "Зберегти",
        "err_title": "Помилка",
        "warn_title": "Увага",
        "yes": "Так",
        "no": "Ні",
    },
    "ru": {
        "tab_main": " 🎵 Саундпад ",
        "tab_settings": " ⚙️ Настройки ",
        "list_frame": " Список звуков (Drag & Drop аудиофайлов сюда) ",
        "col_hotkey": "Клавиша",
        "col_file": "Файл",
        "col_vol": "Громкость",
        "col_loop": "Loop",
        "control_frame": " Настройки выбранного звука ",
        "lbl_vol": "Громкость:",
        "btn_loop_on": "🔁 Loop: ВКЛ",
        "btn_loop_off": "🔁 Loop: ВЫКЛ",
        "btn_rebind": "Изменить клавишу",
        "btn_delete": "Удалить",
        "play_frame": " Ручной запуск ",
        "btn_play_both": "▶ / ⏹ Запустить/Остановить (В оба устройства)",
        "btn_play_mic": "🎙 Только в микрофон",
        "btn_play_hp": "🎧 В наушники",
        "boost_frame": " Усиление (Boost) и Мощный Басс ",
        "lbl_boost": "Общий Буст (Gain):",
        "lbl_bass": "Мощный Басс (5 LVL):",
        "bass_off": "Уровень 0 (Выкл.)",
        "bass_lvl": "Уровень {}",
        "eq_frame": " Децибельный Эквалайзер ",
        "btn_reset_eq": "↺ Сбросить EQ & Boost",
        "btn_hide_eq": "▲ Скрыть EQ",
        "btn_show_eq": "▼ Показать EQ",
        "btn_add": "+ Добавить файл",
        "btn_stop": "Остановить всё",
        "dev_frame": " Выбор аудиоустройств ",
        "lbl_hp": "Наушники (C-Media):",
        "lbl_mic": "Микрофон (VB-Cable):",
        "eq_opts_frame": " Параметры Эквалайзера и Звука ",
        "chk_use_eq": "Включить обработку эквалайзера и буста",
        "chk_keep_global": "Применять одинаковые настройки EQ/Boost/Bass ко ВСЕМ файлам",
        "sys_frame": " Системные настройки ",
        "chk_autostart": "Запускать программу вместе с Windows",
        "lang_frame": " Язык интерфейса / Language ",
        "lbl_lang": "Выберите язык:",
        "default_dev": "По умолчанию",
        "warn_select_sound": "Сначала выберите звук из списка!",
        "win_rebind_title": "Назначение клавиши",
        "win_rebind_lbl": "Введите комбинацию (например: num 1, f1, ctrl+alt+1):",
        "btn_save": "Сохранить",
        "err_title": "Ошибка",
        "warn_title": "Внимание",
        "yes": "Да",
        "no": "Нет",
    },
    "en": {
        "tab_main": " 🎵 Soundpad ",
        "tab_settings": " ⚙️ Settings ",
        "list_frame": " Sound List (Drag & Drop audio files here) ",
        "col_hotkey": "Hotkey",
        "col_file": "File",
        "col_vol": "Volume",
        "col_loop": "Loop",
        "control_frame": " Selected Sound Settings ",
        "lbl_vol": "Volume:",
        "btn_loop_on": "🔁 Loop: ON",
        "btn_loop_off": "🔁 Loop: OFF",
        "btn_rebind": "Change Key",
        "btn_delete": "Delete",
        "play_frame": " Manual Playback ",
        "btn_play_both": "▶ / ⏹ Play/Stop (Both Devices)",
        "btn_play_mic": "🎙 Microphone Only",
        "btn_play_hp": "🎧 Headphones Only",
        "boost_frame": " Boost & Powerful Bass ",
        "lbl_boost": "Master Boost (Gain):",
        "lbl_bass": "Powerful Bass (5 LVL):",
        "bass_off": "Level 0 (Off)",
        "bass_lvl": "Level {}",
        "eq_frame": " Decibel Equalizer ",
        "btn_reset_eq": "↺ Reset EQ & Boost",
        "btn_hide_eq": "▲ Hide EQ",
        "btn_show_eq": "▼ Show EQ",
        "btn_add": "+ Add File",
        "btn_stop": "Stop All",
        "dev_frame": " Audio Devices Selection ",
        "lbl_hp": "Headphones (C-Media):",
        "lbl_mic": "Microphone (VB-Cable):",
        "eq_opts_frame": " Equalizer & Audio Options ",
        "chk_use_eq": "Enable Equalizer & Boost processing",
        "chk_keep_global": "Apply same EQ/Boost/Bass settings to ALL files",
        "sys_frame": " System Settings ",
        "chk_autostart": "Run on Windows startup",
        "lang_frame": " Interface Language ",
        "lbl_lang": "Select Language:",
        "default_dev": "Default",
        "warn_select_sound": "Please select a sound first!",
        "win_rebind_title": "Rebind Hotkey",
        "win_rebind_lbl": "Enter key combination (e.g. num 1, f1, ctrl+alt+1):",
        "btn_save": "Save",
        "err_title": "Error",
        "warn_title": "Warning",
        "yes": "Yes",
        "no": "No",
    },
}


class SoundpadApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Python Soundpad Pro")
        self.root.geometry("780x870")
        self.root.minsize(680, 700)

        self.current_lang = self.detect_system_language()

        self.sounds = {}
        self.default_eq = {
            "preamp": 1.0,
            "boost": 1.0,
            "bass_level": 0,
            "60": 1.0,
            "250": 1.0,
            "1k": 1.0,
            "2k": 1.0,
            "4k": 1.0,
            "8k": 1.0,
            "16k": 1.0,
        }
        self.global_eq = self.default_eq.copy()
        self.active_streams = {}

        self.setup_ui()
        self.load_devices()
        self.load_config()
        self.update_ui_language()

        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self.on_drop)

        threading.Thread(target=self.listen_hotkeys, daemon=True).start()

    def detect_system_language(self):
        detected_lang = None

        try:
            sys_lang, _ = locale.getdefaultlocale()
            if sys_lang:
                detected_lang = sys_lang.lower()
        except Exception:
            pass

        if not detected_lang and hasattr(ctypes, "windll"):
            try:
                windll = ctypes.windll.kernel32
                lang_id = windll.GetUserDefaultUILanguage() & 0x3FF
                if lang_id == 0x22:
                    return "uk"
                elif lang_id in (0x19, 0x02, 0x1A, 0x23):
                    return "ru"
            except Exception:
                pass

        if detected_lang:
            if any(code in detected_lang for code in ["uk", "ua"]):
                return "uk"
            elif any(
                code in detected_lang
                for code in ["ru", "bg", "sr", "be", "kk"]
            ):
                return "ru"

        return "en"

    def tr(self, key):
        return TRANSLATIONS.get(self.current_lang, TRANSLATIONS["en"]).get(
            key, key
        )

    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.tab_main = ttk.Frame(self.notebook)
        self.tab_settings = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_main, text=self.tr("tab_main"))
        self.notebook.add(self.tab_settings, text=self.tr("tab_settings"))

        # Main Tab
        self.tab_main.columnconfigure(0, weight=1)
        self.tab_main.rowconfigure(0, weight=1)

        self.list_frame = ttk.LabelFrame(
            self.tab_main, text=self.tr("list_frame")
        )
        self.list_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        self.list_frame.rowconfigure(0, weight=1)
        self.list_frame.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            self.list_frame,
            columns=("hotkey", "name", "volume", "loop"),
            show="headings",
            selectmode="browse",
        )
        self.tree.column("hotkey", width=110, anchor="center")
        self.tree.column("name", width=380, anchor="w")
        self.tree.column("volume", width=80, anchor="center")
        self.tree.column("loop", width=70, anchor="center")

        tree_scroll = ttk.Scrollbar(
            self.list_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=5)
        tree_scroll.grid(row=0, column=1, sticky="ns", padx=(0, 5), pady=5)

        self.tree.bind("<<TreeviewSelect>>", self.on_select_sound)

        controls_frame = ttk.Frame(self.tab_main)
        controls_frame.grid(row=1, column=0, sticky="ew")
        controls_frame.columnconfigure(0, weight=1)

        self.control_frame = ttk.LabelFrame(
            controls_frame, text=self.tr("control_frame")
        )
        self.control_frame.pack(fill="x", padx=10, pady=3)
        self.control_frame.columnconfigure(1, weight=1)

        self.lbl_vol_title = ttk.Label(
            self.control_frame, text=self.tr("lbl_vol")
        )
        self.lbl_vol_title.grid(row=0, column=0, padx=5, pady=5)

        self.vol_slider = ttk.Scale(
            self.control_frame,
            from_=0.0,
            to=2.0,
            value=1.0,
            command=self.update_selected_volume,
        )
        self.vol_slider.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self.vol_lbl = ttk.Label(self.control_frame, text="100%", width=6)
        self.vol_lbl.grid(row=0, column=2, padx=2, pady=5)

        self.btn_reset_vol = ttk.Button(
            self.control_frame, text="↺ 100%", width=7, command=self.reset_volume
        )
        self.btn_reset_vol.grid(row=0, column=3, padx=3, pady=5)

        self.btn_loop = ttk.Button(
            self.control_frame,
            text=self.tr("btn_loop_off"),
            command=self.toggle_loop,
        )
        self.btn_loop.grid(row=0, column=4, padx=3, pady=5)

        self.btn_bind_key = ttk.Button(
            self.control_frame,
            text=self.tr("btn_rebind"),
            command=self.rebind_key,
        )
        self.btn_bind_key.grid(row=0, column=5, padx=3, pady=5)

        self.btn_delete = ttk.Button(
            self.control_frame,
            text=self.tr("btn_delete"),
            command=self.delete_sound,
        )
        self.btn_delete.grid(row=0, column=6, padx=3, pady=5)

        self.play_btn_frame = ttk.LabelFrame(
            controls_frame, text=self.tr("play_frame")
        )
        self.play_btn_frame.pack(fill="x", padx=10, pady=3)

        self.btn_play_both = ttk.Button(
            self.play_btn_frame,
            text=self.tr("btn_play_both"),
            command=lambda: self.play_selected("both"),
        )
        self.btn_play_both.pack(side="left", expand=True, fill="x", padx=3, pady=5)

        self.btn_play_mic = ttk.Button(
            self.play_btn_frame,
            text=self.tr("btn_play_mic"),
            command=lambda: self.play_selected("mic"),
        )
        self.btn_play_mic.pack(side="left", expand=True, fill="x", padx=3, pady=5)

        self.btn_play_hp = ttk.Button(
            self.play_btn_frame,
            text=self.tr("btn_play_hp"),
            command=lambda: self.play_selected("hp"),
        )
        self.btn_play_hp.pack(side="left", expand=True, fill="x", padx=3, pady=5)

        self.boost_frame = ttk.LabelFrame(
            controls_frame, text=self.tr("boost_frame")
        )
        self.boost_frame.pack(fill="x", padx=10, pady=3)
        self.boost_frame.columnconfigure(1, weight=1)

        self.lbl_boost_title = ttk.Label(
            self.boost_frame,
            text=self.tr("lbl_boost"),
            font=("Segoe UI", 9, "bold"),
        )
        self.lbl_boost_title.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.boost_slider = ttk.Scale(
            self.boost_frame,
            from_=1.0,
            to=3.0,
            value=1.0,
            command=self.on_boost_change,
        )
        self.boost_slider.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.boost_lbl = ttk.Label(self.boost_frame, text="1.0x (0dB)", width=12)
        self.boost_lbl.grid(row=0, column=2, padx=5, pady=5)

        self.lbl_bass_title = ttk.Label(
            self.boost_frame,
            text=self.tr("lbl_bass"),
            font=("Segoe UI", 9, "bold"),
        )
        self.lbl_bass_title.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.bass_slider = ttk.Scale(
            self.boost_frame,
            from_=0,
            to=5,
            value=0,
            command=self.on_bass_change,
        )
        self.bass_slider.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.bass_lbl = ttk.Label(self.boost_frame, text="", width=14)
        self.bass_lbl.grid(row=1, column=2, padx=5, pady=5)

        self.eq_outer_frame = ttk.LabelFrame(
            controls_frame, text=self.tr("eq_frame")
        )
        self.eq_outer_frame.pack(fill="x", padx=10, pady=3)

        eq_top_bar = ttk.Frame(self.eq_outer_frame)
        eq_top_bar.pack(fill="x", padx=5, pady=2)

        self.btn_reset_eq = ttk.Button(
            eq_top_bar,
            text=self.tr("btn_reset_eq"),
            command=self.reset_eq_settings,
        )
        self.btn_reset_eq.pack(side="left", padx=5)

        self.eq_visible = True
        self.btn_toggle_eq = ttk.Button(
            eq_top_bar, text=self.tr("btn_hide_eq"), command=self.toggle_eq_panel
        )
        self.btn_toggle_eq.pack(side="right", padx=5)

        self.sliders_frame = ttk.Frame(self.eq_outer_frame)
        self.sliders_frame.pack(fill="x", padx=5, pady=3)

        bands = [
            ("Preamp", "preamp"),
            ("60Hz", "60"),
            ("250Hz", "250"),
            ("1kHz", "1k"),
            ("2kHz", "2k"),
            ("4kHz", "4k"),
            ("8kHz", "8k"),
            ("16kHz", "16k"),
        ]

        for col in range(len(bands)):
            self.sliders_frame.columnconfigure(col, weight=1)

        self.eq_scales = {}

        for col, (label_text, key) in enumerate(bands):
            b_frame = ttk.Frame(self.sliders_frame)
            b_frame.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")

            ttk.Label(
                b_frame, text=label_text, font=("Segoe UI", 8, "bold")
            ).pack()

            scale = ttk.Scale(
                b_frame,
                from_=3.0,
                to=0.0,
                orient="vertical",
                value=1.0,
                command=lambda val, k=key: self.on_eq_change(k, val),
            )
            scale.pack(fill="y", expand=True, pady=2)

            val_label = ttk.Label(b_frame, text="0.0 dB", font=("Consolas", 8))
            val_label.pack()

            self.eq_scales[key] = (scale, val_label)

        bottom_frame = ttk.Frame(controls_frame)
        bottom_frame.pack(fill="x", padx=10, pady=6)

        self.btn_add = ttk.Button(
            bottom_frame,
            text=self.tr("btn_add"),
            command=self.add_sound_dialog,
        )
        self.btn_add.pack(side="left", padx=5)

        self.btn_stop = ttk.Button(
            bottom_frame, text=self.tr("btn_stop"), command=self.stop_all
        )
        self.btn_stop.pack(side="right", padx=5)

        # Settings Tab
        self.tab_settings.columnconfigure(0, weight=1)

        self.lang_frame = ttk.LabelFrame(
            self.tab_settings, text=self.tr("lang_frame")
        )
        self.lang_frame.pack(fill="x", padx=15, pady=8)
        self.lang_frame.columnconfigure(1, weight=1)

        self.lbl_lang_title = ttk.Label(
            self.lang_frame, text=self.tr("lbl_lang")
        )
        self.lbl_lang_title.grid(row=0, column=0, padx=10, pady=8, sticky="w")

        self.lang_combo = ttk.Combobox(
            self.lang_frame,
            state="readonly",
            values=["Українська", "Русский", "English"],
        )
        self.lang_combo.grid(row=0, column=1, sticky="w", padx=10, pady=8)

        lang_map_rev = {"uk": 0, "ru": 1, "en": 2}
        self.lang_combo.current(lang_map_rev.get(self.current_lang, 2))
        self.lang_combo.bind("<<ComboboxSelected>>", self.on_language_change)

        self.dev_frame = ttk.LabelFrame(
            self.tab_settings, text=self.tr("dev_frame")
        )
        self.dev_frame.pack(fill="x", padx=15, pady=8)
        self.dev_frame.columnconfigure(1, weight=1)

        self.lbl_hp_title = ttk.Label(self.dev_frame, text=self.tr("lbl_hp"))
        self.lbl_hp_title.grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.hp_combo = ttk.Combobox(self.dev_frame, state="readonly")
        self.hp_combo.grid(row=0, column=1, sticky="ew", padx=10, pady=8)

        self.lbl_mic_title = ttk.Label(self.dev_frame, text=self.tr("lbl_mic"))
        self.lbl_mic_title.grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.mic_combo = ttk.Combobox(self.dev_frame, state="readonly")
        self.mic_combo.grid(row=1, column=1, sticky="ew", padx=10, pady=8)

        self.eq_opts_frame = ttk.LabelFrame(
            self.tab_settings, text=self.tr("eq_opts_frame")
        )
        self.eq_opts_frame.pack(fill="x", padx=15, pady=8)

        self.use_eq_var = tk.BooleanVar(value=False)
        self.chk_use_eq = ttk.Checkbutton(
            self.eq_opts_frame,
            text=self.tr("chk_use_eq"),
            variable=self.use_eq_var,
            command=self.save_config,
        )
        self.chk_use_eq.pack(anchor="w", padx=10, pady=8)

        self.keep_global_eq_var = tk.BooleanVar(value=False)
        self.chk_keep_global = ttk.Checkbutton(
            self.eq_opts_frame,
            text=self.tr("chk_keep_global"),
            variable=self.keep_global_eq_var,
            command=self.on_keep_global_toggle,
        )
        self.chk_keep_global.pack(anchor="w", padx=10, pady=8)

        self.sys_frame = ttk.LabelFrame(
            self.tab_settings, text=self.tr("sys_frame")
        )
        self.sys_frame.pack(fill="x", padx=15, pady=8)

        self.autostart_var = tk.BooleanVar(value=False)
        self.chk_autostart = ttk.Checkbutton(
            self.sys_frame,
            text=self.tr("chk_autostart"),
            variable=self.autostart_var,
            command=self.toggle_autostart,
        )
        self.chk_autostart.pack(anchor="w", padx=10, pady=8)

    def on_language_change(self, event=None):
        idx = self.lang_combo.current()
        langs = ["uk", "ru", "en"]
        if 0 <= idx < len(langs):
            self.current_lang = langs[idx]
            self.update_ui_language()
            self.save_config()

    def update_ui_language(self):
        self.notebook.tab(0, text=self.tr("tab_main"))
        self.notebook.tab(1, text=self.tr("tab_settings"))

        self.list_frame.config(text=self.tr("list_frame"))
        self.tree.heading("hotkey", text=self.tr("col_hotkey"))
        self.tree.heading("name", text=self.tr("col_file"))
        self.tree.heading("volume", text=self.tr("col_vol"))
        self.tree.heading("loop", text=self.tr("col_loop"))

        self.control_frame.config(text=self.tr("control_frame"))
        self.lbl_vol_title.config(text=self.tr("lbl_vol"))
        self.btn_bind_key.config(text=self.tr("btn_rebind"))
        self.btn_delete.config(text=self.tr("btn_delete"))

        self.play_btn_frame.config(text=self.tr("play_frame"))
        self.btn_play_both.config(text=self.tr("btn_play_both"))
        self.btn_play_mic.config(text=self.tr("btn_play_mic"))
        self.btn_play_hp.config(text=self.tr("btn_play_hp"))

        self.boost_frame.config(text=self.tr("boost_frame"))
        self.lbl_boost_title.config(text=self.tr("lbl_boost"))
        self.lbl_bass_title.config(text=self.tr("lbl_bass"))

        self.eq_outer_frame.config(text=self.tr("eq_frame"))
        self.btn_reset_eq.config(text=self.tr("btn_reset_eq"))
        self.btn_toggle_eq.config(
            text=self.tr("btn_hide_eq")
            if self.eq_visible
            else self.tr("btn_show_eq")
        )

        self.btn_add.config(text=self.tr("btn_add"))
        self.btn_stop.config(text=self.tr("btn_stop"))

        self.lang_frame.config(text=self.tr("lang_frame"))
        self.lbl_lang_title.config(text=self.tr("lbl_lang"))

        self.dev_frame.config(text=self.tr("dev_frame"))
        self.lbl_hp_title.config(text=self.tr("lbl_hp"))
        self.lbl_mic_title.config(text=self.tr("lbl_mic"))

        self.eq_opts_frame.config(text=self.tr("eq_opts_frame"))
        self.chk_use_eq.config(text=self.tr("chk_use_eq"))
        self.chk_keep_global.config(text=self.tr("chk_keep_global"))

        self.sys_frame.config(text=self.tr("sys_frame"))
        self.chk_autostart.config(text=self.tr("chk_autostart"))

        self.update_eq_ui_sliders()
        self.on_select_sound(None)

    def reset_volume(self):
        selected = self.tree.selection()
        if selected:
            s_id = selected[0]
            self.sounds[s_id]["volume"] = 1.0
            self.vol_slider.set(1.0)
            self.vol_lbl.config(text="100%")
            self.refresh_tree()
            self.save_config()

    def toggle_loop(self):
        selected = self.tree.selection()
        if selected:
            s_id = selected[0]
            is_loop = self.sounds[s_id].get("loop", False)
            self.sounds[s_id]["loop"] = not is_loop

            btn_text = (
                self.tr("btn_loop_on")
                if not is_loop
                else self.tr("btn_loop_off")
            )
            self.btn_loop.config(text=btn_text)

            self.refresh_tree()
            self.save_config()

    def reset_eq_settings(self):
        target_dict = self.default_eq.copy()
        selected = self.tree.selection()

        if self.keep_global_eq_var.get() or not selected:
            self.global_eq = target_dict.copy()
            if self.keep_global_eq_var.get():
                for s_id in self.sounds:
                    self.sounds[s_id]["eq"] = target_dict.copy()
        else:
            s_id = selected[0]
            self.sounds[s_id]["eq"] = target_dict.copy()

        self.update_eq_ui_sliders()
        self.save_config()

    def toggle_eq_panel(self):
        if self.eq_visible:
            self.sliders_frame.pack_forget()
            self.btn_toggle_eq.config(text=self.tr("btn_show_eq"))
            self.eq_visible = False
        else:
            self.sliders_frame.pack(fill="x", padx=5, pady=3)
            self.btn_toggle_eq.config(text=self.tr("btn_hide_eq"))
            self.eq_visible = True

    def on_boost_change(self, val):
        b_val = round(float(val), 2)
        selected = self.tree.selection()

        if self.keep_global_eq_var.get() or not selected:
            self.global_eq["boost"] = b_val
        else:
            s_id = selected[0]
            if "eq" not in self.sounds[s_id]:
                self.sounds[s_id]["eq"] = self.default_eq.copy()
            self.sounds[s_id]["eq"]["boost"] = b_val

        db = 20 * np.log10(b_val) if b_val > 0 else 0
        self.boost_lbl.config(text=f"{b_val:.2f}x (+{db:.1f}dB)")
        self.save_config()

    def on_bass_change(self, val):
        lvl = int(round(float(val)))
        selected = self.tree.selection()

        if self.keep_global_eq_var.get() or not selected:
            self.global_eq["bass_level"] = lvl
        else:
            s_id = selected[0]
            if "eq" not in self.sounds[s_id]:
                self.sounds[s_id]["eq"] = self.default_eq.copy()
            self.sounds[s_id]["eq"]["bass_level"] = lvl

        lbl_text = (
            self.tr("bass_off")
            if lvl == 0
            else f"{self.tr('bass_lvl').format(lvl)} 🔥"
        )
        self.bass_lbl.config(text=lbl_text)
        self.save_config()

    def load_devices(self):
        devices = sd.query_devices()
        def_name = self.tr("default_dev")
        out_devices = [def_name]
        self.dev_map = {def_name: None}

        c_media_index = None
        cable_index = None

        for i, dev in enumerate(devices):
            if dev["max_output_channels"] > 0:
                name = f"{i}: {dev['name']}"
                out_devices.append(name)
                self.dev_map[name] = i

                dev_lower = dev["name"].lower()
                if "c-media" in dev_lower and c_media_index is None:
                    c_media_index = name
                if "cable input" in dev_lower and cable_index is None:
                    cable_index = name

        self.hp_combo["values"] = out_devices
        self.mic_combo["values"] = out_devices

        self.hp_combo.current(0)
        self.mic_combo.current(0)

        if c_media_index:
            self.hp_combo.set(c_media_index)
        if cable_index:
            self.mic_combo.set(cable_index)

    def on_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        for f in files:
            if f.lower().endswith((".mp3", ".wav", ".ogg", ".flac")):
                self.add_sound_file(f)
        self.save_config()

    def add_sound_dialog(self):
        files = filedialog.askopenfilenames(
            title="Audio Files",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.flac")],
        )
        for f in files:
            self.add_sound_file(f)
        self.save_config()

    def add_sound_file(self, file_path):
        sound_id = str(hash(file_path))
        if sound_id in self.sounds:
            return

        name = os.path.basename(file_path)
        self.sounds[sound_id] = {
            "id": sound_id,
            "name": name,
            "path": file_path,
            "hotkey": "None",
            "volume": 1.0,
            "loop": False,
            "eq": self.global_eq.copy(),
        }
        self.refresh_tree()

    def refresh_tree(self):
        selected_id = self.tree.selection()
        self.tree.delete(*self.tree.get_children())
        for s_id, s_data in self.sounds.items():
            vol_pct = f"{int(s_data['volume'] * 100)}%"
            loop_str = (
                self.tr("yes")
                if s_data.get("loop", False)
                else self.tr("no")
            )
            self.tree.insert(
                "",
                "end",
                iid=s_id,
                values=(
                    s_data["hotkey"].upper(),
                    s_data["name"],
                    vol_pct,
                    loop_str,
                ),
            )
        if selected_id and selected_id[0] in self.sounds:
            self.tree.selection_set(selected_id[0])
        self.register_all_hotkeys()

    def get_current_eq(self):
        selected = self.tree.selection()
        if not self.keep_global_eq_var.get() and selected:
            s_id = selected[0]
            if "eq" not in self.sounds[s_id]:
                self.sounds[s_id]["eq"] = self.default_eq.copy()
            return self.sounds[s_id]["eq"]
        return self.global_eq

    def on_select_sound(self, event):
        selected = self.tree.selection()
        if selected:
            s_id = selected[0]
            vol = self.sounds[s_id]["volume"]
            self.vol_slider.set(vol)
            self.vol_lbl.config(text=f"{int(vol * 100)}%")

            is_loop = self.sounds[s_id].get("loop", False)
            btn_text = (
                self.tr("btn_loop_on") if is_loop else self.tr("btn_loop_off")
            )
            self.btn_loop.config(text=btn_text)

            self.update_eq_ui_sliders()

    def update_eq_ui_sliders(self):
        current_eq = self.get_current_eq()

        b_val = current_eq.get("boost", 1.0)
        self.boost_slider.set(b_val)
        db_b = 20 * np.log10(b_val) if b_val > 0 else 0
        self.boost_lbl.config(text=f"{b_val:.2f}x (+{db_b:.1f}dB)")

        bass_lvl = current_eq.get("bass_level", 0)
        self.bass_slider.set(bass_lvl)
        lbl_text = (
            self.tr("bass_off")
            if bass_lvl == 0
            else f"{self.tr('bass_lvl').format(bass_lvl)} 🔥"
        )
        self.bass_lbl.config(text=lbl_text)

        for key, (scale, label) in self.eq_scales.items():
            val = current_eq.get(key, 1.0)
            scale.set(val)
            db = 20 * np.log10(val) if val > 0.01 else -40.0
            label.config(text=f"{db:+.1f}dB")

    def on_eq_change(self, key, val):
        gain_float = float(val)
        selected = self.tree.selection()

        if self.keep_global_eq_var.get() or not selected:
            self.global_eq[key] = gain_float
            if self.keep_global_eq_var.get():
                for s_id in self.sounds:
                    if "eq" not in self.sounds[s_id]:
                        self.sounds[s_id]["eq"] = self.default_eq.copy()
                    self.sounds[s_id]["eq"][key] = gain_float
        else:
            s_id = selected[0]
            if "eq" not in self.sounds[s_id]:
                self.sounds[s_id]["eq"] = self.default_eq.copy()
            self.sounds[s_id]["eq"][key] = gain_float

        db = 20 * np.log10(gain_float) if gain_float > 0.01 else -40.0
        if key in self.eq_scales:
            self.eq_scales[key][1].config(text=f"{db:+.1f}dB")

        self.save_config()

    def on_keep_global_toggle(self):
        if self.keep_global_eq_var.get():
            for s_id in self.sounds:
                self.sounds[s_id]["eq"] = self.global_eq.copy()
        self.update_eq_ui_sliders()
        self.save_config()

    def apply_equalizer(self, data, fs, eq_settings):
        preamp = eq_settings.get("preamp", 1.0)
        boost = eq_settings.get("boost", 1.0)
        out_data = data * preamp * boost

        bass_lvl = eq_settings.get("bass_level", 0)
        if bass_lvl > 0:
            bass_gain = 1.0 + (bass_lvl * 0.8)
            try:
                sos_bass = butter(
                    2, 180.0 / (fs / 2.0), btype="lowpass", output="sos"
                )
                bass_part = sosfilt(sos_bass, out_data, axis=0)
                out_data = out_data + bass_part * (bass_gain - 1.0)
            except Exception as e:
                print(f"Bass Boost error: {e}")

        freq_map = {
            "60": 60.0,
            "250": 250.0,
            "1k": 1000.0,
            "2k": 2000.0,
            "4k": 4000.0,
            "8k": 8000.0,
            "16k": 16000.0,
        }

        for key, center_freq in freq_map.items():
            gain = eq_settings.get(key, 1.0)
            if abs(gain - 1.0) < 0.01:
                continue

            bandwidth = center_freq * 0.8
            low_f = max(center_freq - bandwidth / 2.0, 10.0)
            high_f = min(center_freq + bandwidth / 2.0, (fs / 2.0) - 50.0)

            if low_f >= high_f:
                continue

            try:
                sos = butter(
                    2,
                    [low_f / (fs / 2.0), high_f / (fs / 2.0)],
                    btype="bandpass",
                    output="sos",
                )
                band_part = sosfilt(sos, out_data, axis=0)
                out_data = out_data + band_part * (gain - 1.0)
            except Exception as e:
                print(f"EQ error {key}Hz: {e}")

        return out_data

    def process_audio(self, sound_data, target_fs=48000):
        data, fs = sf.read(sound_data["path"], dtype="float32")

        if len(data.shape) == 1:
            data = np.column_stack((data, data))
        elif data.shape[1] > 2:
            data = data[:, :2]

        if fs != target_fs:
            num_samples = int(len(data) * target_fs / fs)
            data = np.array([
                np.interp(
                    np.linspace(0, len(data), num_samples, endpoint=False),
                    np.arange(len(data)),
                    data[:, c],
                )
                for c in range(data.shape[1])
            ]).T
            fs = target_fs

        if self.use_eq_var.get():
            eq_to_apply = sound_data.get("eq", self.global_eq)
            data = self.apply_equalizer(data, fs, eq_to_apply)

        processed = data * sound_data["volume"]
        processed = np.clip(processed, -1.0, 1.0)

        return processed.astype(np.float32), fs

    def update_selected_volume(self, val):
        selected = self.tree.selection()
        v_float = round(float(val), 2)
        self.vol_lbl.config(text=f"{int(v_float * 100)}%")
        if selected:
            s_id = selected[0]
            self.sounds[s_id]["volume"] = v_float
            self.refresh_tree()
            self.save_config()

    def rebind_key(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                self.tr("warn_title"), self.tr("warn_select_sound")
            )
            return

        s_id = selected[0]
        key_win = tk.Toplevel(self.root)
        key_win.title(self.tr("win_rebind_title"))
        key_win.geometry("320x130")
        key_win.grab_set()

        ttk.Label(key_win, text=self.tr("win_rebind_lbl")).pack(pady=10)
        entry = ttk.Entry(key_win)
        entry.pack(pady=5)
        entry.focus()

        def save_key():
            new_key = entry.get().strip().lower()
            if new_key:
                self.sounds[s_id]["hotkey"] = new_key
                self.refresh_tree()
                self.save_config()
                key_win.destroy()

        ttk.Button(key_win, text=self.tr("btn_save"), command=save_key).pack(
            pady=5
        )

    def delete_sound(self):
        selected = self.tree.selection()
        if selected:
            s_id = selected[0]
            self.stop_sound(s_id)
            del self.sounds[s_id]
            self.refresh_tree()
            self.save_config()

    def stop_sound(self, sound_id):
        if sound_id in self.active_streams:
            streams = self.active_streams.pop(sound_id, [])
            for st in streams:
                try:
                    st.stop()
                    st.close()
                except Exception:
                    pass

    def stop_all(self):
        active_ids = list(self.active_streams.keys())
        for s_id in active_ids:
            self.stop_sound(s_id)

        try:
            sd.stop()
        except Exception:
            pass

    def play_sound(self, sound_data, mode="both"):
        sound_id = sound_data.get("id", str(hash(sound_data["path"])))

        if sound_id in self.active_streams:
            self.stop_sound(sound_id)
            return

        def _play():
            try:
                hp_dev = self.dev_map.get(self.hp_combo.get())
                mic_dev = self.dev_map.get(self.mic_combo.get())

                def get_dev_fs(dev_id):
                    if dev_id is None:
                        return 48000
                    try:
                        return int(sd.query_devices(dev_id)["default_samplerate"])
                    except Exception:
                        return 48000

                streams = []
                audio_hp, audio_mic = None, None

                if mode in ("both", "hp"):
                    fs_hp = get_dev_fs(hp_dev)
                    audio_hp, fs_hp = self.process_audio(
                        sound_data, target_fs=fs_hp
                    )
                    st_hp = sd.OutputStream(
                        device=hp_dev,
                        samplerate=fs_hp,
                        channels=2,
                        dtype="float32",
                        blocksize=2048,
                    )
                    st_hp.start()
                    streams.append(st_hp)

                if mode in ("both", "mic"):
                    fs_mic = get_dev_fs(mic_dev)
                    audio_mic, fs_mic = self.process_audio(
                        sound_data, target_fs=fs_mic
                    )
                    st_mic = sd.OutputStream(
                        device=mic_dev,
                        samplerate=fs_mic,
                        channels=2,
                        dtype="float32",
                        blocksize=2048,
                    )
                    st_mic.start()
                    streams.append(st_mic)

                if not streams:
                    return

                self.active_streams[sound_id] = streams

                chunk_size = 2048
                is_loop = sound_data.get("loop", False)

                while True:
                    max_len = max(
                        len(audio_hp) if audio_hp is not None else 0,
                        len(audio_mic) if audio_mic is not None else 0,
                    )

                    for i in range(0, max_len, chunk_size):
                        if sound_id not in self.active_streams:
                            return

                        if audio_hp is not None:
                            chunk_hp = audio_hp[i : i + chunk_size]
                            if len(chunk_hp) > 0:
                                st_hp.write(chunk_hp)

                        if audio_mic is not None:
                            chunk_mic = audio_mic[i : i + chunk_size]
                            if len(chunk_mic) > 0:
                                st_mic.write(chunk_mic)

                    if not is_loop or sound_id not in self.active_streams:
                        break

            except Exception as e:
                print(f"Playback error: {e}")
            finally:
                self.stop_sound(sound_id)

        threading.Thread(target=_play, daemon=True).start()

    def play_selected(self, mode):
        selected = self.tree.selection()
        if selected:
            s_id = selected[0]
            self.play_sound(self.sounds[s_id], mode=mode)
        else:
            messagebox.showwarning(
                self.tr("warn_title"), self.tr("warn_select_sound")
            )

    def register_all_hotkeys(self):
        keyboard.unhook_all_hotkeys()
        for s_id, s_data in self.sounds.items():
            hk = s_data["hotkey"]
            if hk and hk != "none":
                try:
                    keyboard.add_hotkey(
                        hk, lambda d=s_data: self.play_sound(d, mode="both")
                    )
                except Exception as e:
                    print(f"Hotkey bind failed ({hk}): {e}")

    def listen_hotkeys(self):
        keyboard.wait()

    def toggle_autostart(self):
        enable = self.autostart_var.get()
        try:
            if enable:
                target_path = os.path.abspath(sys.argv[0])
                working_dir = os.path.dirname(target_path)

                ps_script = (
                    f'$WshShell = New-Object -ComObject WScript.Shell; $Shortcut ='
                    f' $WshShell.CreateShortcut("{SHORTCUT_PATH}");'
                    f' $Shortcut.TargetPath = "{sys.executable if target_path.endswith(".py") else target_path}";'
                    f' $Shortcut.Arguments = "{target_path if target_path.endswith(".py") else ""}";'
                    f' $Shortcut.WorkingDirectory = "{working_dir}"; $Shortcut.Save()'
                )
                os.system(f'powershell -Command "{ps_script}"')
            else:
                if os.path.exists(SHORTCUT_PATH):
                    os.remove(SHORTCUT_PATH)
            self.save_config()
        except Exception as e:
            messagebox.showerror(
                self.tr("err_title"), f"Autostart error: {e}"
            )

    def save_config(self):
        data = {
            "lang": self.current_lang,
            "sounds": self.sounds,
            "global_eq": self.global_eq,
            "use_eq": self.use_eq_var.get(),
            "keep_global_eq": self.keep_global_eq_var.get(),
            "autostart": self.autostart_var.get(),
            "hp_dev": self.hp_combo.get(),
            "mic_dev": self.mic_combo.get(),
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Save config error: {e}")

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

                self.current_lang = data.get("lang", self.current_lang)
                lang_map_rev = {"uk": 0, "ru": 1, "en": 2}
                self.lang_combo.current(lang_map_rev.get(self.current_lang, 2))

                self.sounds = data.get("sounds", {})
                self.global_eq = data.get("global_eq", self.default_eq.copy())
                self.use_eq_var.set(data.get("use_eq", False))
                self.keep_global_eq_var.set(data.get("keep_global_eq", False))

                is_autostart = data.get(
                    "autostart", os.path.exists(SHORTCUT_PATH)
                )
                self.autostart_var.set(is_autostart)

                if data.get("hp_dev") in self.hp_combo["values"]:
                    self.hp_combo.set(data["hp_dev"])
                if data.get("mic_dev") in self.mic_combo["values"]:
                    self.mic_combo.set(data["mic_dev"])

                self.refresh_tree()
                self.update_ui_language()
        except Exception as e:
            print(f"Load config error: {e}")


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = SoundpadApp(root)
    root.mainloop()