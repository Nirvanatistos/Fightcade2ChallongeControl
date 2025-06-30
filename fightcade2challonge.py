import tkinter as tk
from tkinter import ttk, messagebox, Canvas, PhotoImage, filedialog
from tkinter import PhotoImage
from pathlib import Path
import math
import challonge
import os
import json

# Ruta relativa a los assets
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


# Constantes
CREDENTIALS_FILE = "challonge_credentials.json"
FC_DIRECTORY_FILE = "fightcade_directory.txt"

# Traducciones
LANGUAGES = {
    "es": {
        "title": "FightCade2Challonge Control v1",
        "connect": "Conectar",
        "user": "Usuario:",
        "api_key": "API Key:",
        "select_tournament": "Selecciona un Torneo:",
        "select_match": "Selecciona un Partido:",
        "submit_result": "Subir Resultados",
        "no_tournament": "No tienes torneos en progreso.",
        "no_match": "Primero debes cargar un match.",
        "connection_success": "Sesión Iniciada!",
        "tournament_loaded": "Torneo cargado!",
        "match_loaded": "Match cargado!",
        "result_uploaded": "Bracket actualizado.",
        "tie_error": "No puede haber empate. Debe haber un ganador.",
        "change_winner_title": "Cambio de Ganador",
        "change_winner_msg": "Estás por cambiar el ganador de '{old}' a '{new}'. Esto podría afectar la estructura del torneo. ¿Deseas continuar?",
        "incomplete_match": "Match incompleto. Falta un participante.",
        "credentials": "Ingresa tu nombre de usuario y tu API Key.",
        "invalid_creds": "Credenciales inválidas o sin conexión a internet.",
        "error_updating": "No se pudo actualizar el Match.",
        "no_tournament_selected": "No hay torneo seleccionado."
    }
}
texts = LANGUAGES["es"]

class ChallongeScoreboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FightCade2Challonge Control v1")
        self.root.geometry("1366x768")
        self.root.configure(bg="#FFFFFF")
        self.root.resizable(False, False)
        try:
            self.root.iconbitmap("assets/frame0/ico.ico")
        except Exception as e:
            print("No se pudo cargar el ícono.", e)
        def center_window(self, width=1366, height=768):
            # Establecer tamaño de la ventana
            self.root.geometry(f"{width}x{height}")

            # Obtener dimensiones de la pantalla
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            # Calcular posición X e Y para centrar la ventana
            x = (screen_width // 2) - (width // 2)
            y = (screen_height // 2) - (height // 2)

            # Aplicar posición centrada
            self.root.geometry(f"+{x}+{y}")

        # --- Variables Configuración y credenciales ---
        self.user_var = tk.StringVar()
        self.api_key_var = tk.StringVar()
        self.ft_tournament_var = tk.StringVar()
        self.ft_final_var = tk.StringVar()
        self.tournament_var = tk.StringVar()
        self.match_var = tk.StringVar()
        self.directory_var = tk.StringVar()
        
        # Control de autolectura de archivos
        self.auto_update_enabled = True
        self.auto_update_id = None
        self._auto_check_id = None
        
        # --- Variables UI y Widgets ---
        self.mode_button = tk.Button(
            self.root,
            text="Modo FightCade",
            font=("Arial", 8),
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            command=self.toggle_mode_text
        )
        
        self.mode_button.place(x=1133.0, y=98.0, width=140.0, height=20.0)
        
        self.entry_dir = tk.Entry(
            self.root,
            textvariable=self.directory_var,
            font=("Arial", 8),
        )
        
        # --- Estado del partido actual ---
        self.loaded_match = None
        self.original_match_data = {}
        self.current_tournament_id = None
        self.matches_data = []
        self.tournaments_list = []
        
        # --- Variables Control de modo (FightCade) ---
        self.mode_var = tk.StringVar(value="manual")
        self.manual_order_confirmed = False
        self.auto_update_paused = False
        
        # --- Variables Puntajes y notificaciones ---
        self.score1 = tk.IntVar()
        self.score2 = tk.IntVar()
        self.after_id = None
        self.auto_update_id = None
        
        # --- Variables Set Default Botones gráficos ---
        self.button_submit = None
        self.button_reopen = None
        
        # --- Variable para next_match ---
        self.next_match_var = tk.StringVar()
        
        # Cargar directorio de FightCade desde archivo
        if os.path.exists(FC_DIRECTORY_FILE):
            with open(FC_DIRECTORY_FILE, "r") as f:
                dir_path = f.read().strip()
            if os.path.isdir(dir_path):
                self.directory_var.set(dir_path)
                self.entry_dir.delete(0, tk.END)
                self.entry_dir.insert(0, dir_path)

        # Cargar credenciales guardadas
        self.load_saved_credentials()

        # Crear widgets
        self.create_widgets()

        # Conectar automáticamente si ya hay credenciales
        if self.user_var.get() and self.api_key_var.get():
            self.connect_to_challonge()
            
        # Boton Subir a challonge deshabilitado
        if hasattr(self, "button_submit"):
            self.button_submit.config(state="disabled")

    def create_widgets(self):
        # Canvas principal
        self.canvas = Canvas(
            self.root,
            bg="#FFFFFF",
            height=768,
            width=1366,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)

        # Imagen fondo (ui_background.png)
        try:
            self.image_image_1 = PhotoImage(file=relative_to_assets("ui_background.png"))
            self.image_1 = self.canvas.create_image(683.0, 384.0, image=self.image_image_1)
        except Exception as e:
            print("Error al cargar ui_background.png.", e)
                
        # Notificaciones
        self.notification_label = tk.Label(
            self.root,
            text="",
            bg="#24000c",
            fg="#FFFFFF",
            wraplength=319,
            font=("Arial Black", 12, "bold"),
            anchor="center"
        )
        self.notification_label.place(x=550.0, y=10.0, width=319.0, height=30.0)

        # Combobox Seleccionar Torneo
        self.combobox_tournament = ttk.Combobox(
            self.root,
            textvariable=self.tournament_var,
            state="readonly",
            font=("Arial", 8)
        )
        self.combobox_tournament.place(x=119.0, y=34.0, width=209.0, height=20.0)
        self.combobox_tournament.bind("<<ComboboxSelected>>", lambda e: self.load_matches())

        # Combobox Seleccionar Match
        self.combobox_match = ttk.Combobox(
            self.root,
            textvariable=self.match_var,
            state="readonly",
            font=("Arial", 8)
        )
        self.combobox_match.place(x=119.0, y=66.0, width=209.0, height=20.0)
        self.combobox_match.bind("<<ComboboxSelected>>", lambda e: (self.load_selected_match(e)))
        
        # Combobox Next Match
        self.combobox_next_match = ttk.Combobox(
            self.root,
            textvariable=self.next_match_var,
            state="readonly",
            font=("Arial", 8),
            values=[]
        )
        self.combobox_next_match.place(x=1153.0, y=140.0, width=199.0, height=20.0)
        self.combobox_next_match.set("")  # Iniciar vacío

        # Vincular evento de selección
        self.combobox_next_match.bind("<<ComboboxSelected>>", self.on_next_match_selected)

        # Entry Usuario
        self.entry_user = tk.Entry(
            self.root,
            textvariable=self.user_var,
            font=("Arial Black", 8),
            show=""
        )
        self.entry_user.place(x=1153.0, y=48.0, width=140.0, height=20.0)

        # Entry API Key
        self.entry_apikey = tk.Entry(
            self.root,
            textvariable=self.api_key_var,
            font=("Arial Black", 8),
            show="*"
        )
        self.entry_apikey.place(x=1153.0, y=78.0, width=140.0, height=20.0)

        # Botón conectar (login.png)
        try:
            self.button_connect_image = PhotoImage(file=relative_to_assets("login.png"))
            self.button_connect = tk.Button(
                image=self.button_connect_image,
                borderwidth=0,
                highlightthickness=0,
                command=self.connect_to_challonge,
                relief="flat"
            )
            self.button_connect.place(x=1303.0, y=50.0, width=45.0, height=45.0)
        except Exception as e:
            print("Error al cargar login.png.", e)

        # Etiqueta "Usuario:"
        self.canvas.create_text(
            1098.0,
            50.0,
            anchor="nw",
            text="Usuario:",
            fill="#FFFFFF",
            font=("Arial Black", 8, "bold")
        )

        # Etiqueta "APIKEY:"
        self.canvas.create_text(
            1098.0,
            80.0,
            anchor="nw",
            text="APIKEY:",
            fill="#FFFFFF",
            font=("Arial Black", 8, "bold")
        )
        
        # Etiqueta "Next Match:"
        self.canvas.create_text(
            1062.0,
            142.0,
            anchor="nw",
            text="NEXT MATCH:",
            fill="#FFFFFF",
            font=("Arial Black", 8, "bold")
        )

        # Botón Examinar (examinar.png)
        try:
            self.examine_button_image = PhotoImage(file=relative_to_assets("examinar.png"))
            self.button_browse = tk.Button(
                image=self.examine_button_image,
                borderwidth=0,
                highlightthickness=0,
                command=self.browse_directory,
                relief="flat"
            )
            self.button_browse.place(x=309.0, y=125.0, width=20.0, height=20.0)
            
        except Exception as e:
            print("Error al crear examinar.png", e)

        # Campo Directorio
        self.entry_dir = tk.Entry(
            self.root,
            textvariable=self.directory_var,
            font=("Arial", 8),
            bg="#FFFFFF",
            fg="#000716"
        )
        self.entry_dir.place(x=119.0, y=125.0, width=181.0, height=20.0)
        self.entry_dir.config(state="disabled")

        # Jugadores (Nick Player1 y Nick Player2 - texto por defecto)
        self.player1_name = self.canvas.create_text(
            450.0,
            85.0,
            anchor="center",
            text="Nick Player1",
            fill="#FFFFFF",
            font=("Arial Black", 15, "bold"),
            justify="center",
            width=150
        )

        self.player2_name = self.canvas.create_text(
            930.0,
            85.0,
            anchor="center",
            text="Nick Player2",
            fill="#FFFFFF",
            font=("Arial Black", 15, "bold"),
            justify="center",
            width=150
        )

        # Puntajes (0 por defecto)
        self.score1 = tk.IntVar(value=0)
        self.score2 = tk.IntVar(value=0)
        
        # Etiqueta para mostrar ronda ("Round 1", "Final", etc.)
        self.round_info_label = self.canvas.create_text(
            1500.0,
            75.0,
            anchor="nw",
            text="Round Info",
            fill="#FFFFFF",
            font=("Arial", 10, "bold"),
            justify="center"
        )
        self.score1_label = self.canvas.create_text(
            592.0,
            40.0,
            anchor="nw",
            text="0",
            fill="#FFFFFF",
            font=("Arial Black", 48, "bold"),
            justify="center",
            width=100
        )
        self.score2_label = self.canvas.create_text(
            738.0,
            40.0,
            anchor="nw",
            text="0",
            fill="#FFFFFF",
            font=("Arial Black", 48, "bold"),
            justify="center",
            width=100
        )
        self.vs_label = self.canvas.create_text(
            683.0,
            67.0,
            anchor="nw",
            text="V/S",
            fill="#FFFFFF",
            font=("Arial Black", 20, "bold"),
            justify="center",
            width=70
        )

        # Botones de +1/-1
        try:
            self.button_add1 = tk.Button(
                self.root,
                text="+1",
                command=self.add_point_player1,
                font=("Arial", 10, "bold"),
                bg="#00FF15",
                fg="#000716"
            )
            self.button_add1.place(x=380.0, y=15.0, width=25.0, height=25.0)
        except Exception as e:
            print("Error al cargar botón +1 (player1).", e)

        try:
            self.button_minus1 = tk.Button(
                self.root,
                text="-1",
                command=self.minus_point_player1,
                font=("Arial", 10, "bold"),
                bg="#cf0000",
                fg="#000716"
            )
            self.button_minus1.place(x=350.0, y=15.0, width=25.0, height=25.0)
        except Exception as e:
            print("Error al cargar botón -1 (player1).", e)

        try:
            self.button_add2 = tk.Button(
                self.root,
                text="+1",
                command=self.add_point_player2,
                font=("Arial", 10, "bold"),
                bg="#00FF15",
                fg="#000716"
            )
            self.button_add2.place(x=1023.0, y=15.0, width=25.0, height=25.0)
        except Exception as e:
            print("Error al cargar botón +1 (player2)", e)

        try:
            self.button_minus2 = tk.Button(
                self.root,
                text="-1",
                command=self.minus_point_player2,
                font=("Arial", 10, "bold"),
                bg="#cf0000",
                fg="#000716"
            )
            self.button_minus2.place(x=993.0, y=15.0, width=25.0, height=25.0)
        except Exception as e:
            print("Error al cargar botón -1 (player2).", e)

        # Botón Subir Resultados (upload_results.png)
        try:
            self.submit_results_image = PhotoImage(file=relative_to_assets("upload_results.png"))
            self.button_submit = tk.Button(
                image=self.submit_results_image,
                borderwidth=0,
                highlightthickness=0,
                command=self.submit_result,
                relief="flat"
            )
            self.button_submit.image = self.submit_results_image  # Evitar garbage collection
            self.button_submit.place(x=563.0, y=135.0, width=300.0, height=30.0)
            self.button_submit.config(state="disabled")
        except Exception as e:
            print("Error al cargar upload_results.png.", e)
            
        # Botón Re-Abrir Match (reopen_match.png)
        try:
            self.reopen_match_image = PhotoImage(file=relative_to_assets("reopen_match.png"))
            self.button_reopen = tk.Button(
                image=self.reopen_match_image,
                borderwidth=0,
                highlightthickness=0,
                command=self.reopen_match,
                relief="flat"
            )
            self.button_reopen.image = self.reopen_match_image
            self.button_reopen.place(x=879.0, y=10.0, width=30.0, height=30.0)
            self.button_reopen.config(state="disabled")
            if hasattr(self, "button_reopen"):
                self.button_reopen.config(state="disabled")
                
        except Exception as e:
            print("Error al cargar reopen_match.png.", e)

        # Combobox FT Torneo
        self.combo_ft_tournament = ttk.Combobox(
            self.root,
            textvariable=self.ft_tournament_var,
            values=["FT1", "FT2", "FT3", "FT4", "FT5", "FT6", "FT7", "FT8", "FT9", "FT10"],
            state="readonly",
            font=("Arial", 8)
        )
        self.combo_ft_tournament.place(x=119.0, y=96.0, width=50.0, height=20.0)

        # Combobox FT Final
        self.combo_ft_final = ttk.Combobox(
            self.root,
            textvariable=self.ft_final_var,
            values=["FT1", "FT2", "FT3", "FT4", "FT5", "FT6", "FT7", "FT8", "FT9", "FT10"],
            state="readonly",
            font=("Arial", 8)
        )
        self.combo_ft_final.place(x=278.0, y=96.0, width=50.0, height=20.0)
        
        self.combo_ft_tournament.bind("<<ComboboxSelected>>", self.on_ft_change)
        self.combo_ft_final.bind("<<ComboboxSelected>>", self.on_ft_change)

        # Winners Bracket
        
        self.winners_frame = tk.Frame(self.root, bg="#FFFFFF")
        self.winners_frame.place(x=10.0, y=201.0, width=1346.0, height=200.0)

        self.winners_canvas = Canvas(self.winners_frame, bg="#FFFFFF", highlightthickness=0)
        self.winners_scroll_x = tk.Scrollbar(self.winners_frame, orient="horizontal", command=self.winners_canvas.xview)
        self.winners_scroll_y = tk.Scrollbar(self.winners_frame, orient="vertical", command=self.winners_canvas.yview)

        self.winners_container = tk.Frame(self.winners_canvas, bg="#FFFFFF", height=260)
        self.winners_container.pack_propagate(False)

        self.winners_canvas.configure(
            xscrollcommand=self.winners_scroll_x.set,
            yscrollcommand=self.winners_scroll_y.set
        )
        self.winners_canvas.create_window((0, 0), window=self.winners_container, anchor="nw", width=3000, tags="winners_window")
        self.winners_canvas.pack(side="left", fill="both", expand=True)
        self.winners_scroll_x.place(x=0, y=185, width=1346, height=15)
        self.winners_scroll_y.place(x=1326, y=0, width=15, height=180)

        def on_configure_winners(e):
            self.winners_canvas.configure(scrollregion=self.winners_canvas.bbox("all"))

        self.winners_container.bind("<Configure>", on_configure_winners)
        self.winners_canvas.bind("<Configure>", lambda e: self.winners_canvas.configure(scrollregion=self.winners_canvas.bbox("all")))


        # Losers Bracket
        self.losers_frame = tk.Frame(self.root, bg="#FFFFFF")
        self.losers_frame.place(x=10.0, y=446.0, width=1346.0, height=222.0)

        self.losers_canvas = Canvas(self.losers_frame, bg="#FFFFFF", highlightthickness=0)
        self.losers_scroll_x = tk.Scrollbar(self.losers_frame, orient="horizontal", command=self.losers_canvas.xview)
        self.losers_scroll_y = tk.Scrollbar(self.losers_frame, orient="vertical", command=self.losers_canvas.yview)

        self.losers_container = tk.Frame(self.losers_canvas, bg="#FFFFFF", height=260)
        self.losers_container.pack_propagate(False)

        self.losers_canvas.configure(
            xscrollcommand=self.losers_scroll_x.set,
            yscrollcommand=self.losers_scroll_y.set
        )
        self.losers_canvas.create_window((0, 0), window=self.losers_container, anchor="nw", width=3000, tags="losers_window")
        self.losers_canvas.pack(side="left", fill="both", expand=True)
        self.losers_scroll_x.place(x=0, y=207, width=1346, height=15)
        self.losers_scroll_y.place(x=1326, y=0, width=15, height=202)

        def on_configure_losers(e):
            self.losers_canvas.configure(scrollregion=self.losers_canvas.bbox("all"))

        self.losers_container.bind("<Configure>", on_configure_losers)
        self.losers_canvas.bind("<Configure>", lambda e: self.losers_canvas.configure(scrollregion=self.losers_canvas.bbox("all")))

        def on_mousewheel_winners(event):
            self.winners_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def on_shift_mousewheel_winners(event):
            self.winners_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

        def on_mousewheel_losers(event):
            self.losers_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def on_shift_mousewheel_losers(event):
            self.losers_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

        # Asignar eventos de scroll con rueda del mouse
        self.winners_canvas.bind("<MouseWheel>", on_mousewheel_winners)
        self.winners_canvas.bind("<Shift-MouseWheel>", on_shift_mousewheel_winners)
        self.losers_canvas.bind("<MouseWheel>", on_mousewheel_losers)
        self.losers_canvas.bind("<Shift-MouseWheel>", on_shift_mousewheel_losers)
        
        # Textos selección de torneo, match y directorio FC2
        self.canvas.create_text(
            22.0,
            36.0,
            anchor="nw",
            text="Selec. Torneo:",
            fill="#FFFFFF",
            font=("Arial Black", 8, "bold")
        )
        self.canvas.create_text(
            27.0,
            68.0,
            anchor="nw",
            text="Selec. Match:",
            fill="#FFFFFF",
            font=("Arial Black", 8, "bold")
        )
        self.canvas.create_text(
            60.0,
            127.0,
            anchor="nw",
            text="FC2 Dir:",
            fill="#FFFFFF",
            font=("Arial Black", 8, "bold")
        )
        self.canvas.create_text(
            45.0,
            98.0,
            anchor="nw",
            text="FT Torneo:",
            fill="#FFFFFF",
            font=("Arial Black", 8, "bold")
        )
        self.canvas.create_text(
            218.0,
            98.0,
            anchor="nw",
            text="FT Final:",
            fill="#FFFFFF",
            font=("Arial Black", 8, "bold")
        )
        
        self.update_score_display()

    def load_saved_credentials(self):
        if os.path.exists(CREDENTIALS_FILE):
            with open(CREDENTIALS_FILE, "r") as f:
                data = json.load(f)
                self.user_var.set(data.get("user", ""))
                self.api_key_var.set(data.get("api_key", ""))

    def save_credentials(self):
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump({
                "user": self.user_var.get(),
                "api_key": self.api_key_var.get()
            }, f)

    def connect_to_challonge(self):
        user = self.user_var.get().strip()
        api_key = self.api_key_var.get().strip()

        if not user or not api_key:
            messagebox.showerror("Error", texts["credentials"])
            return

        try:
            challonge.set_credentials(user, api_key)

            # Cargar lista completa de torneos
            tournaments = challonge.tournaments.index()
            double_elimination_tournaments = []

            for t in tournaments:
                if t["state"] in ["in_progress", "underway"]:
                    full_tournament = challonge.tournaments.show(t["id"])
                    tournament_type = full_tournament.get("tournament_type", "").strip().lower()
                    if tournament_type == "double elimination":
                        double_elimination_tournaments.append(t)

            if not double_elimination_tournaments:
                messagebox.showinfo("Sin torneos de doble eliminación.", texts["no_tournament"])
                return

            self.save_credentials()
            self.tournaments_list = double_elimination_tournaments
            self.combobox_tournament["values"] = [t["name"] for t in double_elimination_tournaments]
            self.combobox_tournament.config(state="readonly")
            self.combobox_tournament.set("")

            # Deshabilitar partido hasta que haya torneo elegido
            self.combobox_match.config(state="disabled")
            self.combobox_match.set("")
            self.notification_label.config(text="")

            # Mostrar mensaje en notificación
            self.show_notification("FC2Challonge Control v1.0", duration=3000, permanent=True)

            # Forzar revisión de FT después de conectar
            self.root.after(2000, self.on_ft_change)
            
            
            if hasattr(self, "combobox_match"):
                self.combobox_match.config(state="disabled")

        except Exception as e:
            print("Error al conectar con Challonge.", str(e))
            messagebox.showerror("Error", f"{texts['invalid_creds']}\n{str(e)}")

    def show_notification(self, message, duration=2000, permanent=False):
        #Muestra una notificación en pantalla y maneja los after_ids de forma segura
        # Limpiar notificación anterior si existe
        if hasattr(self, "_notification_after_id") and self._notification_after_id is not None:
            try:
                self.root.after_cancel(self._notification_after_id)
            except:
                pass

        # Actualizar texto de notificación
        self.notification_label.config(text=message)

        # Si no es permanente, programar limpieza después de X segundos
        if not permanent:
            self._notification_after_id = self.root.after(duration, lambda: self.notification_label.config(text=""))
        else:
            self._notification_after_id = None

    def load_matches(self, event=None):
        ft_tournament = self.combo_ft_tournament.get()
        ft_final = self.combo_ft_final.get()

        if not ft_tournament or not ft_final:
            messagebox.showwarning(
                "Configuración incompleta.",
                "Por favor selecciona valores en ambos campos 'FT Torneo' y 'FT Final' antes de cargar un Match."
            )
            return

        tournament_index = self.combobox_tournament.current()
        if tournament_index == -1:
            return

        tournament = self.tournaments_list[tournament_index]
        tournament_id = tournament["id"]
        self.current_tournament_id = tournament_id

        try:
            matches = challonge.matches.index(tournament_id)
            participants = {p["id"]: p["name"] for p in challonge.participants.index(tournament_id)}

            self.matches_data = []
            match_list = []

            for match in matches:
                p1_name = participants.get(match["player1_id"], "") or match.get("player1_placeholder_text", "?")
                p2_name = participants.get(match["player2_id"], "") or match.get("player2_placeholder_text", "?")

                # Verificar que ambos jugadores estén definidos y el partido no esté cerrado
                if (p1_name not in ["?", "?"] and 
                    p2_name not in ["?", "?"] and 
                    match["state"] == "open"):

                    display_text = f"{p1_name} vs {p2_name}"
                    match_list.append(display_text)
                    match["p1_name"] = p1_name
                    match["p2_name"] = p2_name
                    self.matches_data.append(match)

            # Actualizar combobox_match
            self.combobox_match["values"] = match_list
            if match_list:
                self.combobox_match.config(state="readonly")
                self.combobox_match.set("")
                self.notification_label.config(text="Elija Partido!", fg="#FFFFFF")
            else:
                self.combobox_match.config(state="disabled")
                self.combobox_match.set("")
                self.notification_label.config(text="No hay Matches disponibles.")

            self.draw_bracket()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los matches.\n{str(e)}")
        
    def draw_bracket(self):
        for widget in self.winners_container.winfo_children():
            widget.destroy()
        for widget in self.losers_container.winfo_children():
            widget.destroy()
        if not self.current_tournament_id:
            return
        try:
            matches = challonge.matches.index(self.current_tournament_id)
            participants = {p["id"]: p["name"] for p in challonge.participants.index(self.current_tournament_id)}
            if not participants:
                raise ValueError("No se encontraron participantes para este torneo.")
            winners_by_round = {}
            losers_by_round = {}
            total_players = len(participants) if participants else 8
            rounds_before_finals = int(math.log2(total_players)) if total_players > 0 else 3

            # Organizar partidos por ronda
            for match in matches:
                rnd = match["round"]
                if rnd > 0:
                    if rnd == rounds_before_finals:
                        key = 1000  # WB Final
                    elif rnd == rounds_before_finals + 1:
                        key = 1001  # Grand Final
                    elif rnd == rounds_before_finals + 2:
                        key = 1002  # Grand Final
                    elif rnd == rounds_before_finals + 3:
                        key = 1003  # Grand Final Reset
                    else:
                        key = rnd  # Ronda normal
                    if key not in winners_by_round:
                        winners_by_round[key] = []
                    winners_by_round[key].append(match)
                elif rnd < 0:
                    abs_rnd = abs(rnd)
                    if abs_rnd not in losers_by_round:
                        losers_by_round[abs_rnd] = []
                    losers_by_round[abs_rnd].append(match)

            # Dibujar partidos en orden lógico
            self.display_horizontal_bracket(self.winners_container, winners_by_round, participants, is_losers=False)
            self.display_horizontal_bracket(self.losers_container, losers_by_round, participants, is_losers=True)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo dibujar el bracket.\n{str(e)}")

    def display_horizontal_bracket(self, container, rounds_dict, participants, is_losers=False):
        # Separar claves normales y especiales
        normal_keys = []
        special_keys_order = {
            1000: "WB Final",
            1001: "Grand Final",
            1002: "Grand Final",
            1003: "Grand Final Reset"
        }

        for key in rounds_dict.keys():
            if key in special_keys_order:
                continue
            else:
                normal_keys.append(key)

        # Ordenar rondas normales ascendentemente
        normal_keys.sort()

        # Construir custom_order: rondas normales + rondas especiales en orden fijo
        custom_order = []

        # Añadir rondas normales con sus títulos
        for key in normal_keys:
            title = self.get_round_description(key, len(participants)) if not is_losers else self.get_round_description(-key, len(participants))
            custom_order.append((key, title))

        # Añadir rondas especiales en orden definido
        for key, title in special_keys_order.items():
            if key in rounds_dict:
                custom_order.append((key, title))

        # Limpiar contenedor previo
        for widget in container.winfo_children():
            widget.destroy()

        # Dibujar columnas en el orden correcto
        for key_tuple in custom_order:
            key = key_tuple[0]
            title = key_tuple[1]

            frame = tk.Frame(container, bg="#f5f5f5")
            frame.pack(side="left", fill="y", padx=5, pady=5)

            # Título del round ENCIMA de los partidos
            tk.Label(frame, text=title, font=("Arial", 10, "bold"), bg="#f5f5f5").pack(anchor="n", pady=(0, 5))
            inner = tk.Frame(frame, bg="#ffffff")
            inner.pack(fill="y")

            # Mostrar partidos en este frame
            for match in rounds_dict.get(key, []):
                p1 = participants.get(match["player1_id"], "") or match.get("player1_placeholder_text", "?")
                p2 = participants.get(match["player2_id"], "") or match.get("player2_placeholder_text", "?")
                scores_csv = match.get("scores_csv", "")

                # Estilizar partido según estado
                if match["state"] == "complete" and scores_csv:
                    match_str = f"{p1} ({scores_csv}) {p2}"
                    label = tk.Label(inner, text=match_str, font=("Arial black", 10), bg="#f5f5f5", fg="#808080")
                elif p1 == "?" or p2 == "?":
                    match_str = f"{p1} vs {p2}"
                    label = tk.Label(inner, text=match_str, font=("Arial black", 10), bg="#f5f5f5", fg="#aaaaaa")
                else:
                    match_str = f"{p1} vs {p2}"
                    label = tk.Label(inner, text=match_str, font=("Arial black", 10), bg="#f5f5f5", fg="#2ecc71")
                label.pack(pady=1)
                label.bind("<Button-1>", lambda e, m=match: self.on_click_match(m, participants, label, is_losers))

    # Actualizar scroll region después de dibujar todo
    def update_scroll_region(self, container=None):
        canvas = container.master
        canvas.configure(scrollregion=canvas.bbox("all"))

        container.update_idletasks()
        self.root.after(100, self.update_scroll_region)

    def get_round_description(self, round_num, total_participants):
        # Para partidos del Losers Bracket
        if round_num < 0:
            abs_rnd = abs(round_num)
            try:
                losers_rounds = set()
                for match in challonge.matches.index(self.current_tournament_id):
                    if match["round"] < 0:
                        losers_rounds.add(abs(match["round"]))
                max_losers_round = max(losers_rounds) if losers_rounds else 1

                if abs_rnd == max_losers_round:
                    return "LB Final"
                elif abs_rnd == max_losers_round - 1:
                    return "LB Semifinales"
                else:
                    return f"LB Round {abs_rnd}"
            except Exception as e:
                print("Error al obtener rondas del Losers:", e)
                return f"LB Round {abs_rnd}"

        # Para partidos del Winners Bracket
        try:
            participants = challonge.participants.index(self.current_tournament_id)
            total_players = len(participants)
        except Exception as e:
            total_players = total_participants or 8

        rounds_before_finals = int(math.log2(total_players)) if total_players > 0 else 3

        if round_num == rounds_before_finals:
            return "WB SemiFinal"
        elif round_num == rounds_before_finals + 1:
            return "Grand Final"
        elif round_num == rounds_before_finals + 2:
            return "Grand Final"
        elif round_num == rounds_before_finals + 3:
            return "Grand Final Reset"
        else:
            return f"Ronda {round_num}"

    def on_click_match(self, match, participants, label, is_losers=False):
        p1_id = match["player1_id"]
        p2_id = match["player2_id"]

        try:
            tournament_id = self.current_tournament_id
            p1 = challonge.participants.show(tournament_id, p1_id)
            p2 = challonge.participants.show(tournament_id, p2_id)
        except Exception as e:
            print("Error al cargar jugadores desde Challonge:", e)
            return

        if p1["name"] == "?" or p2["name"] == "?":
            messagebox.showinfo("Partido incompleto", texts["incomplete_match"])
            return

        # Obtener estado del partido desde Challonge
        try:
            match_data = challonge.matches.show(tournament_id, match["id"])
            match_state = match_data["state"]
        except Exception as e:
            print("Error al obtener estado del partido:", e)
            match_state = "open"

        # Si partido cerrado → pregunta si continuar sin reiniciar
        if match_state == "complete":
            response = messagebox.askyesno(
                "Advertencia",
                "Este partido ya está finalizado.\n"
                "Modificarlo podría alterar demasiado el bracket.\n"
                "¿Deseas continuar?"
            )
            if not response:
                return

        # Guardar datos del partido cargado
        self.loaded_match = {
            "tournament_id": self.current_tournament_id,
            "match_id": match["id"],
            "player1_id": p1_id,
            "player2_id": p2_id,
            "player1": p1,
            "player2": p2,
            "state": match_state,
            "old_winner_id": match.get("winner_id")
        }

        # Actualizar nombres en pantalla
        self.canvas.itemconfig(self.player1_name, text=p1["name"])
        self.canvas.itemconfig(self.player2_name, text=p2["name"])

        # Cargar puntaje desde Challonge si está cerrado
        if match_state == "complete" and match_data.get("scores_csv"):
            scores = match_data["scores_csv"].split("-")
            self.score1.set(int(scores[0]))
            self.score2.set(int(scores[1]))
            self.update_score_display()
        else:
            if self.mode_button["text"] == "Modo FightCade":
                score1, score2 = self.read_scores_from_files()
                if score1 is not None and score2 is not None:
                    self.score1.set(score1)
                    self.score2.set(score2)
                    self.update_score_display()
                else:
                    self.score1.set(0)
                    self.score2.set(0)
                    self.update_score_display()
            else:
                self.score1.set(0)
                self.score2.set(0)
                self.update_score_display()

        # Resaltar partido seleccionado
        container = self.winners_container if not is_losers else self.losers_container
        for child in container.winfo_children():
            for w in child.winfo_children():
                if isinstance(w, tk.Label):
                    w.config(bg="#f5f5f5")
        label.config(bg="#f1c40f")

        # Mostrar notificación de partido en curso
        self.show_notification("Match en curso...", permanent=True)

        # Habilitar/deshabilitar botones según estado
        if match_state == "open":
            if hasattr(self, "button_submit"):
                self.button_submit.config(state="normal")
            if hasattr(self, "button_reopen"):
                self.button_reopen.config(state="disabled")
        else:
            if hasattr(self, "button_submit"):
                self.button_submit.config(state="disabled")
            if hasattr(self, "button_reopen"):
                self.button_reopen.config(state="normal")

        self.update_next_match_combobox()
        self.update_match_combobox()

        # Vaciar archivo next_match.txt si tiene contenido
        selected_dir = self.directory_var.get()
        if selected_dir:
            next_match_path = os.path.join(selected_dir, "next_match.txt")
            try:
                with open(next_match_path, "w") as f:
                    f.write("")
            except Exception as e:
                print("No se pudo limpiar next_match.txt", e)

        # Reiniciar modo automático para próximo partido
        self.auto_update_enabled = True
        if hasattr(self, "button_submit"):
            self.button_submit.config(state="disabled")

        # Iniciar autolectura periódica cada segundo
        if self._auto_check_id:
            self.root.after_cancel(self._auto_check_id)
        self._auto_check_id = self.root.after(1000, self.check_score_auto_update)
        
    def add_point_player1(self):
        if not self.auto_update_enabled:
            current = self.score1.get()
            self.score1.set(current + 1)
            self.update_score_display()
            score1 = self.score1.get()
            score2 = self.score2.get()
            self.check_auto_submit_result(score1, score2)
            return

        response = messagebox.askyesno(
            "Advertencia",
            "Modificar los puntajes manualmente desactivará la lectura automática de FightCade.\n"
            "¿Deseas continuar?"
        )
        if not response:
            return

        # Desactivar autolectura y habilitar botón de submit
        self.auto_update_enabled = False
        if hasattr(self, "button_submit"):
            self.button_submit.config(state="normal")

        current = self.score1.get()
        self.score1.set(current + 1)
        self.update_score_display()
        score1 = self.score1.get()
        score2 = self.score2.get()
        self.check_auto_submit_result(score1, score2)

    def minus_point_player1(self):
        if not self.auto_update_enabled:
            current = self.score1.get()
            if current > 0:
                self.score1.set(current - 1)
                self.update_score_display()
                score1 = self.score1.get()
                score2 = self.score2.get()
                self.check_auto_submit_result(score1, score2)
            return

        response = messagebox.askyesno(
            "Advertencia",
            "Modificar los puntajes manualmente desactivará la lectura automática de FightCade.\n"
            "¿Deseas continuar?"
        )
        if not response:
            return

        # Desactivar autolectura y habilitar botón de submit
        self.auto_update_enabled = False
        if hasattr(self, "button_submit"):
            self.button_submit.config(state="normal")

        current = self.score1.get()
        if current > 0:
            self.score1.set(current - 1)
            self.update_score_display()
            score1 = self.score1.get()
            score2 = self.score2.get()
            self.check_auto_submit_result(score1, score2)

    def add_point_player2(self):
        if not self.auto_update_enabled:
            current = self.score2.get()
            self.score2.set(current + 1)
            self.update_score_display()
            score1 = self.score1.get()
            score2 = self.score2.get()
            self.check_auto_submit_result(score1, score2)
            return

        response = messagebox.askyesno(
            "Advertencia",
            "Modificar los puntajes manualmente desactivará la lectura automática de FightCade.\n"
            "¿Deseas continuar?"
        )
        if not response:
            return

        # Desactivar autolectura y habilitar botón de submit
        self.auto_update_enabled = False
        if hasattr(self, "button_submit"):
            self.button_submit.config(state="normal")

        current = self.score2.get()
        self.score2.set(current + 1)
        self.update_score_display()
        score1 = self.score1.get()
        score2 = self.score2.get()
        self.check_auto_submit_result(score1, score2)

    def minus_point_player2(self):
        if not self.auto_update_enabled:
            current = self.score2.get()
            if current > 0:
                self.score2.set(current - 1)
                self.update_score_display()
                score1 = self.score1.get()
                score2 = self.score2.get()
                self.check_auto_submit_result(score1, score2)
            return

        response = messagebox.askyesno(
            "Advertencia",
            "Modificar los puntajes manualmente desactivará la lectura automática de FightCade.\n"
            "¿Deseas continuar?"
        )
        if not response:
            return

        # Desactivar autolectura y habilitar botón de submit
        self.auto_update_enabled = False
        if hasattr(self, "button_submit"):
            self.button_submit.config(state="normal")

        current = self.score2.get()
        if current > 0:
            self.score2.set(current - 1)
            self.update_score_display()
            score1 = self.score1.get()
            score2 = self.score2.get()
            self.check_auto_submit_result(score1, score2)
            
    def toggle_manual_mode_warning(self):
        if not self.auto_update_enabled:
            return

        response = messagebox.askyesno(
            "Advertencia",
            "Modificar los puntajes manualmente desactivará la lectura automática de FightCade.\n"
            "Deberás usar 'Upload Results' para enviar los resultados."
        )
        if response:
            self.auto_update_enabled = True
            if hasattr(self, "button_submit"):
                self.button_submit.config(state="normal")
        else:
            # Restaurar valores anteriores
            score1, score2 = self.read_scores_from_files()
            if score1 is not None and score2 is not None:
                self.score1.set(score1)
                self.score2.set(score2)
                self.update_score_display()

    def submit_result(self, auto=False, force_winner=None):
        if not self.loaded_match:
            messagebox.showwarning("Advertencia", texts["no_match"])
            return

        tournament_id = self.loaded_match["tournament_id"]
        match_id = self.loaded_match["match_id"]
        p1 = self.loaded_match["player1"]
        p2 = self.loaded_match["player2"]

        score1 = self.score1.get()
        score2 = self.score2.get()

        if auto and force_winner:
            winner = p1["id"] if force_winner == "p1" else p2["id"]
        else:
            if score1 == score2:
                messagebox.showerror("Error", texts["tie_error"])
                return
            winner = p1["id"] if score1 > score2 else p2["id"]

        try:
            challonge.matches.update(
                tournament_id,
                match_id,
                scores_csv=f"{score1}-{score2}",
                winner_id=winner,
                state="complete"
            )

            # Limpiar marca de envío
            if hasattr(self, "_submitting"):
                self._submitting = False

            # Resetear puntajes en pantalla
            self.score1.set(0)
            self.score2.set(0)
            self.canvas.itemconfig(self.score1_label, text="00")
            self.canvas.itemconfig(self.score2_label, text="00")
            self.reset_scores_files_and_ui()

            # Mostrar notificación y refrescar bracket
            self.show_notification(texts["result_uploaded"], duration=2000)
            self.draw_bracket()
            self.load_matches()
            self.update_match_combobox()

            # Reiniciar la interfaz para seleccionar un nuevo partido
            self.show_notification("Elija Partido!", duration=3000)

            # Reiniciar nombres visuales a valores por defecto
            self.canvas.itemconfig(self.player1_name, text="Nick Player1")
            self.canvas.itemconfig(self.player2_name, text="Nick Player2")

            # Limpiar next_match (interfaz y archivo)
            self.combobox_next_match.set("")
            selected_dir = self.directory_var.get()
            if selected_dir:
                next_match_path = os.path.join(selected_dir, "next_match.txt")
                try:
                    with open(next_match_path, "w") as f:
                        f.write("")
                except Exception as e:
                    print("No se pudo limpiar next_match.txt", e)

            # Deshabilitar botones tras subir resultado
            if hasattr(self, "button_submit"):
                self.button_submit.config(state="disabled")

            # Reiniciar modo automático para próximo partido
            self.auto_update_enabled = True

        except Exception as e:
            # Manejo de errores + restaurar estado
            print("Error al enviar resultado:", str(e))
            self.show_notification("ERROR AL ACTUALIZAR PARTIDO", duration=4000, permanent=True)
            self._submitting = False  # Liberar bandera

            # Mostrar mensaje de error más amigable
            messagebox.showerror("Error", f"No se pudo actualizar el partido.\n{str(e)}")

    def load_selected_match(self, event=None):
        match_index = self.combobox_match.current()
        if match_index == -1:
            return
        match = self.matches_data[match_index]
        tournament_index = self.combobox_tournament.current()
        if tournament_index == -1:
            return
        tournament = self.tournaments_list[tournament_index]
        tournament_id = tournament["id"]
        self.current_tournament_id = tournament_id
        try:
            p1 = challonge.participants.show(tournament_id, match["player1_id"])
            p2 = challonge.participants.show(tournament_id, match["player2_id"])
            # Cargar estado del partido desde Challonge
            match_data = challonge.matches.show(tournament_id, match["id"])
            match_state = match_data["state"]
            # Actualizar nombres en pantalla
            self.canvas.itemconfig(self.player1_name, text=p1["name"])
            self.canvas.itemconfig(self.player2_name, text=p2["name"])
            # Reiniciar archivos p1score.txt y p2score.txt a "0"
            selected_dir = self.directory_var.get()
            if selected_dir:
                p1_path = os.path.join(selected_dir, "p1score.txt")
                p2_path = os.path.join(selected_dir, "p2score.txt")
                try:
                    with open(p1_path, "w") as f:
                        f.write("0")
                    with open(p2_path, "w") as f:
                        f.write("0")
                    self.score1.set(0)
                    self.score2.set(0)
                    self.update_score_display()
                except Exception as e:
                    print("No se pudieron resetear los archivos.", e)

            # Guardar datos del partido cargado
            self.loaded_match = {
                "tournament_id": tournament_id,
                "match_id": match["id"],
                "player1": p1,
                "player2": p2,
                "old_winner_id": match.get("winner_id"),
                "state": match_state
            }

            # Mostrar notificación y habilitar botones
            if match_state == "open":
                self.show_notification("Match en curso...", permanent=True)
                if hasattr(self, "button_submit"):
                    self.button_submit.config(state="normal")
                if hasattr(self, "button_reopen"):
                    self.button_reopen.config(state="disabled")
            else:
                self.show_notification("", permanent=True)
                if hasattr(self, "button_submit"):
                    self.button_submit.config(state="disabled")
                if hasattr(self, "button_reopen"):
                    self.button_reopen.config(state="normal")

            self.update_next_match_combobox()
            self.update_match_combobox()

            # Vaciar archivo next_match.txt si tiene contenido
            if selected_dir:
                next_match_path = os.path.join(selected_dir, "next_match.txt")
                try:
                    with open(next_match_path, "w") as f:
                        f.write("")
                except Exception as e:
                    print("No se pudo limpiar next_match.txt", e)

            # Reiniciar modo automático para próximo partido
            self.auto_update_enabled = True
            if hasattr(self, "button_submit"):
                self.button_submit.config(state="disabled")

            # Iniciar autolectura periódica cada segundo
            if self._auto_check_id:
                self.root.after_cancel(self._auto_check_id)
            self._auto_check_id = self.root.after(1000, self.check_score_auto_update)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el match.\n{str(e)}")
            
    def is_valid_fightcade_root(self, path):
        """Verifica que el directorio tenga la estructura correcta: \emulator\fbneo\fightcade\ """
        path_parts = os.path.normpath(path).split(os.sep)

        # Verificar estructura de carpetas
        if len(path_parts) < 3:
            return False

        if path_parts[-1].lower() != "fightcade":
            return False
        if path_parts[-2].lower() != "fbneo":
            return False
        if path_parts[-3].lower() != "emulator":
            return False

        # Verificar que existan los archivos de puntaje
        p1_path = os.path.join(path, "p1score.txt")
        p2_path = os.path.join(path, "p2score.txt")
        if not (os.path.exists(p1_path) and os.path.exists(p2_path)):
            return False

        return True

    def browse_directory(self):
        selected_dir = filedialog.askdirectory()
        if not selected_dir:
            return

        p1_path = os.path.join(selected_dir, "p1score.txt")
        p2_path = os.path.join(selected_dir, "p2score.txt")

        # Verificar estructura del directorio
        if not self.is_valid_fightcade_root(selected_dir):
            messagebox.showwarning(
                "Directorio incorrecto",
                "Debe seleccionar el directorio raíz de FightCade:\n"
                "Ejemplo: \\emulator\\fbneo\\fightcade\\"
            )
            return

        # Verificar que existan los archivos p1score.txt y p2score.txt
        if not (os.path.exists(p1_path) and os.path.exists(p2_path)):
            messagebox.showwarning(
                "Archivos faltantes",
                "No se encontraron los archivos p1score.txt y/o p2score.txt.\n\n"
                "Asegúrate de haber seleccionado correctamente la carpeta 'fightcade'.\n"
                "La ruta debe terminar en: \\emulator\\fbneo\\fightcade\\"
            )
            return

        # Guardar directorio si pasa todas las validaciones
        self.directory_var.set(selected_dir)
        self.entry_dir.delete(0, tk.END)
        self.entry_dir.insert(0, selected_dir)

        # Desactivar edición manual del directorio
        self.entry_dir.config(state="readonly")

        # Intentar guardar directorio en disco
        try:
            with open(FC_DIRECTORY_FILE, "w") as f:
                f.write(selected_dir)
        except Exception as e:
            # Mostrar error y revertir estado del entry_dir
            print("Error al guardar directorio:", e)
            self.entry_dir.config(state="normal")
            messagebox.showerror(
                "Error",
                "No se pudo guardar el directorio seleccionado.\n"
                "Puedes continuar usando la aplicación, pero esta carpeta no se recordará después de cerrarla."
            )

        try:
            score1, score2 = self.read_scores_from_files()
            if score1 is not None and score2 is not None:
                self.score1.set(score1)
                self.score2.set(score2)
                self.update_score_display()
        except Exception as e:
            print("No se pudieron cargar los puntajes iniciales", e)

    def toggle_mode_text(self):
        current = self.mode_button["text"]
        if current == "Modo FightCade":
            # Cambiar a Modo Challonge
            self.mode_button.config(text="Modo Challonge")
            self.entry_dir.config(state="disabled")
            self.button_browse.config(state="disabled")
        else:
            # Cambiar a Modo FightCade
            self.mode_button.config(text="Modo FightCade")
            self.button_browse.config(state="normal")

            # Recuperar directorio desde archivo si existe
            if not self.directory_var.get() and os.path.exists(FC_DIRECTORY_FILE):
                try:
                    with open(FC_DIRECTORY_FILE, "r") as f:
                        saved_dir = f.read().strip()
                        if os.path.isdir(saved_dir):
                            self.directory_var.set(saved_dir)
                            self.entry_dir.delete(0, tk.END)
                            self.entry_dir.insert(0, saved_dir)
                            self.entry_dir.config(state="disabled")
                        else:
                            self.entry_dir.config(state="normal")
                except Exception as e:
                    print("Error al cargar directorio guardado:", e)
                    self.entry_dir.config(state="normal")
            else:
                # Si ya hay directorio, mantenerlo en "readonly"
                if self.directory_var.get():
                    self.entry_dir.config(state="readonly")
                else:
                    self.entry_dir.config(state="normal")
            
    def read_scores_from_files(self):
        if self.mode_button["text"] != "Modo FightCade":
            return None, None

        selected_dir = self.directory_var.get()
        if not selected_dir:
            return None, None

        p1_path = os.path.join(selected_dir, "p1score.txt")
        p2_path = os.path.join(selected_dir, "p2score.txt")

        if not (os.path.exists(p1_path) and os.path.exists(p2_path)):
            return None, None

        try:
            with open(p1_path, "r") as f:
                score1 = int(f.read().strip())
            with open(p2_path, "r") as f:
                score2 = int(f.read().strip())
            return score1, score2
        except Exception as e:
            print("Error al leer puntajes.", e)
            return None, None
            
    def check_score_auto_update(self):
        if not self.loaded_match or not self.auto_update_enabled or self.mode_button["text"] != "Modo FightCade":
            self.auto_update_id = self.root.after(1000, self.check_score_auto_update)
            return

        score1, score2 = self.read_scores_from_files()

        if score1 is None or score2 is None:
            self.root.after(1000, self.check_score_auto_update)
            return

        # Actualizar solo si hay cambio real
        if self.score1.get() != score1 or self.score2.get() != score2:
            self.score1.set(score1)
            self.score2.set(score2)
            self.update_score_display()
            self.check_auto_submit_result(score1, score2)

        # Volver a ejecutar después de 1 segundo
        self.auto_update_id = self.root.after(1000, self.check_score_auto_update)
        
    def reset_scores_files_and_ui(self):
        """Reinicia puntajes visuales y archivos p1score.txt / p2score.txt"""
        # Reiniciar puntajes en interfaz
        self.score1.set(0)
        self.score2.set(0)
        self.update_score_display()

        # Reiniciar archivos p1score.txt y p2score.txt si están en modo FightCade
        if self.mode_button["text"] == "Modo FightCade":
            selected_dir = self.directory_var.get()
            if selected_dir:
                p1_path = os.path.join(selected_dir, "p1score.txt")
                p2_path = os.path.join(selected_dir, "p2score.txt")
                try:
                    with open(p1_path, "w") as f:
                        f.write("0")
                    with open(p2_path, "w") as f:
                        f.write("0")
                except Exception as e:
                    print("No se pudieron resetear los archivos.", e)
            
    def reopen_match(self):
        """Reabre un partido finalizado desde la API de Challonge"""
        if not self.loaded_match:
            print("No hay partido cargado.")
            return

        tournament_id = self.loaded_match["tournament_id"]
        match_id = self.loaded_match["match_id"]

        try:
            # 1. Confirmación del usuario
            response = messagebox.askyesno(
                "Reabrir Partido",
                "¿Estás seguro de que deseas reabrir este partido?"
            )
            if not response:
                return

            # 2. Llamar a la API de Challonge para reabrir el partido
            challonge.matches.reopen(tournament_id, match_id)

            # 3. Actualizar UI
            self.show_notification("Partido Reabierto", duration=2000)
            self.load_selected_match()  # Recargar datos del partido
            self.draw_bracket()  # Actualizar visualización del bracket
            self.update_match_combobox()  # Refrescar combobox_match

            # Reiniciar puntajes y archivos usando el método auxiliar
            self.reset_scores_files_and_ui()

            # Recargar todos los partidos del torneo y actualizar UI
            self.load_matches()
            self.update_match_combobox()

            # 5. Habilitar edición de puntaje
            if hasattr(self, "button_submit"):
                self.button_submit.config(state="normal")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo reabrir el partido.\n{str(e)}")
    
    def update_score_display(self):
        score1 = self.score1.get()
        score2 = self.score2.get()
        # Actualiza directamente los textos del canvas con formato de dos dígitos
        self.canvas.itemconfig(self.score1_label, text=f"{score1:02d}")
        self.canvas.itemconfig(self.score2_label, text=f"{score2:02d}")
        
    def update_next_match_combobox(self):
        if not self.loaded_match:
            self.combobox_next_match["values"] = []
            self.combobox_next_match.set("")
            return

        tournament_id = self.loaded_match["tournament_id"]
        current_p1 = self.canvas.itemcget(self.player1_name, "text")
        current_p2 = self.canvas.itemcget(self.player2_name, "text")

        try:
            matches = challonge.matches.index(tournament_id)
            participants = {p["id"]: p["name"] for p in challonge.participants.index(tournament_id)}
            future_matches = []

            for match in matches:
                p1 = participants.get(match["player1_id"], "?")
                p2 = participants.get(match["player2_id"], "?")
                if p1 == "?" or p2 == "?":
                    continue
                match_text = f"{p1} vs {p2}"
                current_text = f"{current_p1} vs {current_p2}"

                # Solo agregar si NO es el partido actual y está abierto
                if match["state"] == "open" and match_text != current_text:
                    future_matches.append(match_text)

            # Eliminar duplicados y actualizar combobox
            future_matches = list(set(future_matches))
            self.combobox_next_match["values"] = future_matches
            self.combobox_next_match.set("")  # Iniciar vacío

        except Exception as e:
            print("Error al actualizar next_match:", e)
            self.combobox_next_match["values"] = []
            self.combobox_next_match.set("")
    
    def load_scores_from_files_after_delay(self, p1, p2, match, tournament_id):
        score1, score2 = self.read_scores_from_files()
        if score1 is not None and score2 is not None:
            self.score1.set(score1)
            self.score2.set(score2)
            self.update_score_display()
        else:
            self.score1.set(0)
            self.score2.set(0)
            self.canvas.itemconfig(self.score1_label, text="0")
            self.canvas.itemconfig(self.score2_label, text="0")

        # Guardar datos del partido cargado
        self.loaded_match = {
            "tournament_id": tournament_id,
            "match_id": match["id"],
            "player1": p1,
            "player2": p2,
            "old_winner_id": match.get("winner_id")
        }

        # Iniciar autolectura periódica cada segundo
        self.auto_update_id = self.root.after(1000, self.auto_update_scores)
        
    def auto_update_scores(self):
        if not self.loaded_match or not self.auto_update_enabled or self.mode_button["text"] != "Modo FightCade":
            return

        score1, score2 = self.read_scores_from_files()
        if score1 is None or score2 is None:
            self.root.after(1000, self.auto_update_scores)
            return

        if self.score1.get() != score1 or self.score2.get() != score2:
            self.score1.set(score1)
            self.score2.set(score2)
            self.update_score_display()
            self.check_auto_submit_result(score1, score2)

        self.auto_update_id = self.root.after(1000, self.auto_update_scores)
    
    def get_current_ft_value(self):
        #Obtiene el FT actual según ronda
        if not self.loaded_match:
            return None

        round_desc = self.canvas.itemcget(self.round_info_label, "text")
        is_final = "final" in round_desc.lower()

        try:
            if is_final:
                ft_value = int(self.combo_ft_final.get()[2:])  # Ej: "FT3" → 3
            else:
                ft_value = int(self.combo_ft_tournament.get()[2:])
            return ft_value
        except Exception as e:
            print("Error al leer FT.", e)
            return None
            
    def is_special_match(self, match_data):
        """Detecta si el partido actual es uno especial según tus claves personalizadas."""
        try:
            tournament_id = self.current_tournament_id
            matches = challonge.matches.index(tournament_id)
            participants = challonge.participants.index(tournament_id)
            total_players = len(participants) if participants else 8
            rounds_before_finals = int(math.log2(total_players)) if total_players > 0 else 3

            match_round = match_data["round"]

            # Asignar clave interna
            if match_round == rounds_before_finals:
                key = 1000  # WB SemiFinal
            elif match_round == rounds_before_finals + 1:
                key = 1001  # WB Final
            elif match_round == rounds_before_finals + 2:
                key = 1002  # Grand Final
            elif match_round == rounds_before_finals + 3:
                key = 1003  # Grand Final Reset
            else:
                key = match_round

            # Estos keys son considerados especiales
            special_keys = [1000, 1001, 1002, 1003]

            # Verificar si es "LB Final" basado en tu nomenclatura personalizada
            abs_rnd = abs(match_round)
            losers_rounds = set()
            for m in matches:
                if m["round"] < 0:
                    losers_rounds.add(abs(m["round"]))
            max_losers_round = max(losers_rounds) if losers_rounds else 1

            if match_round < 0 and abs_rnd == max_losers_round:
                # Es "LB Final"
                return True

            # Si es alguno de los partidos especiales definidos por key
            return key in special_keys

        except Exception as e:
            print("Error al detectar tipo de partido:", e)
            return False
            
    def get_ft_value(self):
        """Devuelve el valor numérico del FT según el tipo de partido"""
        if not self.loaded_match:
            return 3
        try:
            match_data = challonge.matches.show(self.loaded_match["tournament_id"], self.loaded_match["match_id"])

            if self.is_special_match(match_data):
                try:
                    ft_value = int(self.combo_ft_final.get()[2:])  # Ej: "FT5" → 5
                    return ft_value
                except:
                    return 5  # Valor por defecto para finales
            else:
                try:
                    ft_value = int(self.combo_ft_tournament.get()[2:])  # Ej: "FT3" → 3
                    return ft_value
                except:
                    return 3  # Valor por defecto para torneos
        except Exception as e:
            print("Error al obtener FT:", e)
            return 3
            
    def check_auto_submit_result(self, score1, score2):
        if self.mode_button["text"] != "Modo FightCade":
            return
        if not self.loaded_match:
            return

        try:
            ft_value = self.get_ft_value()

            if score1 >= ft_value or score2 >= ft_value:
                winner = "p1" if score1 > score2 else "p2"

                # Cancelar cualquier auto-check pendiente antes de enviar
                if self.auto_update_id:
                    self.root.after_cancel(self.auto_update_id)
                    self.auto_update_id = None

                # Enviar resultados automáticamente
                self.submit_result(auto=True, force_winner=winner)

                # Reiniciar puntajes visuales a "00"
                self.score1.set(0)
                self.score2.set(0)
                self.update_score_display()

                # Mostrar notificación
                self.show_notification("Elija Partido!", permanent=True)

        except Exception as e:
            print("Error en check_auto_submit_result:", e)
            
    def on_ft_change(self, event=None):
        """Detecta cambios en FT Torneo/Final y muestra mensajes según estado"""
        ft_tournament = self.combo_ft_tournament.get()
        ft_final = self.combo_ft_final.get()

        # Validar qué falta
        if not ft_tournament and not ft_final:
            self.show_notification("Asigne FT Torneo y FT Final", duration=3000, permanent=True)
        elif not ft_tournament:
            self.show_notification("Asigne FT Torneo", duration=3000, permanent=True)
        elif not ft_final:
            self.show_notification("Asigne FT Final", duration=3000, permanent=True)
        else:
            self.show_notification("Elija Torneo!", duration=3000, permanent=True)

        # Habilitar combos solo si ambos FT están llenos
        if ft_tournament and ft_final:
            self.combobox_tournament.config(state="readonly")
            self.combobox_match.config(state="readonly")
        else:
            self.combobox_tournament.config(state="disabled")
            self.combobox_match.config(state="disabled")
        
    def update_match_combobox(self):
        """Actualiza el texto del partido seleccionado en el combobox_match"""
        if not self.loaded_match:
            return

        p1 = self.canvas.itemcget(self.player1_name, "text")
        p2 = self.canvas.itemcget(self.player2_name, "text")
    
        match_text = f"{p1} vs {p2}"
        match_index = -1
    
        for i, value in enumerate(self.combobox_match["values"]):
            if value == match_text:
                match_index = i
                break

        # Actualizar el valor del combobox_match
        if match_index != -1:
            self.combobox_match.current(match_index)
        else:
            self.combobox_match.set(match_text)

        # Asegurar que el combobox_match esté habilitado si hay partido abierto
        if self.loaded_match.get("state") == "open":
            self.combobox_match.config(state="readonly")
        else:
            self.combobox_match.config(state="normal")
            
    def on_refresh_bracket(self):
        if not self.current_tournament_id:
            return

        try:
            matches = challonge.matches.index(self.current_tournament_id)
            participants = {p["id"]: p["name"] for p in challonge.participants.index(self.current_tournament_id)}

            winners_by_round = {}
            losers_by_round = {}

            for match in matches:
                rnd = match["round"]
                if rnd > 0:
                    if rnd not in winners_by_round:
                        winners_by_round[rnd] = []
                    winners_by_round[rnd].append(match)
                elif rnd < 0:
                    abs_rnd = abs(rnd)
                    if abs_rnd not in losers_by_round:
                        losers_by_round[abs_rnd] = []
                    losers_by_round[abs_rnd].append(match)

            # Redibujar partidos
            for widget in self.winners_container.winfo_children():
                widget.destroy()
            for widget in self.losers_container.winfo_children():
                widget.destroy()

            self.display_horizontal_bracket(self.winners_container, winners_by_round, participants, is_losers=False)
            self.display_horizontal_bracket(self.losers_container, losers_by_round, participants, is_losers=True)

            # Mostrar notificación de actualización
            self.show_notification("Bracket Refresh", duration=2000)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo refrescar el bracket\n{str(e)}")
            
    def on_reset_scores_click(self):
        """Reinicia ambos puntajes a 0 con confirmación"""
        if not self.loaded_match:
            messagebox.showwarning("Advertencia", "Debe cargar un partido primero para usar este botón.")
            return

        try:
            tournament_id = self.loaded_match["tournament_id"]
            match_id = self.loaded_match["match_id"]
            match_data = challonge.matches.show(tournament_id, match_id)
            match_state = match_data["state"]
        except Exception as e:
            print("Error al obtener estado del partido:", e)
            match_state = "open"

        # Si el partido está cerrado → pregunta si reiniciar de todas formas
        if match_state == "complete":
            response = messagebox.askyesno(
                "Advertencia",
                "Este partido ya está cerrado. ¿Deseas reiniciar puntajes de todas formas?"
            )
            if not response:
                return

        # Confirmación final del usuario
        response = messagebox.askyesno(
            "Confirmar reinicio",
            "¿Estás seguro que deseas reiniciar ambos puntajes a 0?"
        )
        if not response:
            return

        # Usar método auxiliar para reiniciar puntajes y archivos
        self.reset_scores_files_and_ui()
        self.auto_update_enabled = True
        
        if self.auto_update_id is not None:
            try:
                self.root.after_cancel(self.auto_update_id)
            except ValueError:
                pass
            self.auto_update_id = None

        # Mostrar notificación y refrescar UI
        self.show_notification("Score Resets OK", duration=2000)
        self.draw_bracket()

        # Actualizar estado del partido localmente a "open"
        self.loaded_match["state"] = "open"

        # Forzar actualización visual
        self.update_match_combobox()
        
    def force_combobox_up(self, event):
        try:
            event.widget.tk.eval(f"::ttk::popup {event.widget}")
        finally:
            return "break"
        
    def on_next_match_selected(self, event=None):
        selected_match = self.next_match_var.get()
        if not selected_match:
            return

        selected_dir = self.directory_var.get()
        if not selected_dir:
            messagebox.showwarning(
                "Directorio no definido",
                "No se puede guardar 'next_match.txt' sin directorio válido."
            )
            return

        next_match_path = os.path.join(selected_dir, "next_match.txt")
        try:
            with open(next_match_path, "w", encoding="utf-8") as f:
                f.write(selected_match)
        except Exception as e:
            print("Error al guardar next_match.txt:", e)
            messagebox.showerror(
                "Error",
                "No se pudo guardar el archivo next_match.txt"
            )
            
            
if __name__ == "__main__":
    window = tk.Tk()
    app = ChallongeScoreboardApp(window)
    window.mainloop()
