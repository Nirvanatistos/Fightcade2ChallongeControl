import tkinter as tk  # Importa el módulo tkinter principal para GUI
from tkinter import ttk, messagebox, Canvas, PhotoImage, filedialog  # Importa componentes específicos de tkinter
from tkinter import PhotoImage  # Importa PhotoImage directamente (duplicado pero válido)
from pathlib import Path  # Importa Path para manejo de rutas de archivos
import math  # Importa math para operaciones matemáticas
import challonge  # Importa librería challonge para integración con API
import os  # Importa os para funciones del sistema operativo
import json  # Importa json para manejo de archivos JSON

# Ruta relativa a los assets
OUTPUT_PATH = Path(__file__).parent  # Obtiene el directorio del script actual
ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"  # Define ruta base para assets
def relative_to_assets(path: str) -> Path:  # Función para convertir ruta relativa a asset
    return ASSETS_PATH / Path(path)  # Devuelve la ruta completa al asset
        
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
    
# Constantes
CREDENTIALS_FILE = "challonge_credentials.json"  # Archivo para guardar credenciales Challonge
FC_DIRECTORY_FILE = "fightcade_directory.txt"  # Archivo para guardar directorio FightCade

# Traducciones
LANGUAGES = {  # Diccionario de traducciones soportadas
    "es": {  # Traducciones en español
        "title": "FightCade2Challonge Control v1.0.1",  # Título de ventana
        "connect": "Conectar",  # Botón conectar
        "user": "Usuario:",  # Etiqueta usuario
        "api_key": "API Key:",  # Etiqueta API key
        "select_tournament": "Selecciona un Torneo:",  # Selección de torneo
        "select_match": "Selecciona un Partido:",  # Selección de partido
        "submit_result": "Subir Resultados",  # Botón subir resultados
        "no_tournament": "No tienes torneos en progreso.",  # Mensaje sin torneos
        "no_match": "Primero debes cargar un match.",  # Mensaje sin partido seleccionado
        "connection_success": "Sesión Iniciada!",  # Confirmación conexión exitosa
        "tournament_loaded": "Torneo cargado!",  # Confirmación torneo cargado
        "match_loaded": "Match cargado!",  # Confirmación partido cargado
        "result_uploaded": "Bracket actualizado.",  # Confirmación resultado subido
        "tie_error": "No puede haber empate. Debe haber un ganador.",  # Error empate
        "change_winner_title": "Cambio de Ganador",  # Título confirmación cambio ganador
        "change_winner_msg": "Estás por cambiar el ganador de '{old}' a '{new}'. Esto podría afectar la estructura del torneo. ¿Deseas continuar?",  # Mensaje confirmación cambio ganador
        "incomplete_match": "Match incompleto. Falta un participante.",  # Error partido incompleto
        "credentials": "Ingresa tu nombre de usuario y tu API Key.",  # Instrucción credenciales
        "invalid_creds": "Credenciales inválidas o sin conexión a internet.",  # Error credenciales
        "error_updating": "No se pudo actualizar el Match.",  # Error actualización match
        "no_tournament_selected": "No hay torneo seleccionado."  # Error sin torneo seleccionado
    }
}
texts = LANGUAGES["es"]  # Selecciona el idioma español como predeterminado
class ChallongeScoreboardApp:  # Clase principal de la aplicación
    def __init__(self, root):  # Constructor de la clase
        
        self.root = root  # Guarda referencia a la ventana principal
        self.root.title("FightCade2Challonge Control v1.0.1")  # Establece título de ventana
        self.root.geometry("1366x768")  # Establece tamaño de ventana
        self.root.configure(bg="#FFFFFF")  # Establece color de fondo blanco
        self.root.resizable(False, False)  # Deshabilita redimensionamiento
        try:  # Intenta establecer ícono de ventana
            self.root.iconbitmap(resource_path("assets/frame0/ico.ico"))  # Carga ícono desde archivo
        except Exception as e:  # Captura excepción si falla
            print("No se pudo cargar el ícono.", e)  # Muestra mensaje de error
        
        def center_window(self, width=1366, height=768):  # Función para centrar ventana
            # Establecer tamaño de la ventana
            self.root.geometry(f"{width}x{height}")  # Aplica tamaño especificado
            # Obtener dimensiones de la pantalla
            screen_width = self.root.winfo_screenwidth()  # Obtiene ancho de pantalla
            screen_height = self.root.winfo_screenheight()  # Obtiene alto de pantalla
            # Calcular posición X e Y para centrar la ventana
            x = (screen_width // 2) - (width // 2)  # Calcula coordenada X central
            y = (screen_height // 2) - (height // 2)  # Calcula coordenada Y central
            # Aplicar posición centrada
            self.root.geometry(f"+{x}+{y}")  # Aplica posición centrada a la ventana
        
        # --- Variables Configuración y credenciales ---
        self.user_var = tk.StringVar()  # Variable para almacenar usuario
        self.api_key_var = tk.StringVar()  # Variable para almacenar clave API
        self.ft_tournament_var = tk.StringVar()  # Variable para FT Torneo
        self.ft_final_var = tk.StringVar()  # Variable para FT Final
        self.tournament_var = tk.StringVar()  # Variable para selección de torneo
        self.match_var = tk.StringVar()  # Variable para selección de partido
        self.directory_var = tk.StringVar()  # Variable para directorio FightCade
        # Control de autolectura de archivos
        self.auto_update_enabled = True  # Indica si está activa la autolectura
        self.auto_update_id = None  # ID para programar actualizaciones automáticas
        self._auto_check_id = None  # ID para verificación periódica de cambios
        
        # --- Variables UI y Widgets ---
        self.mode_button = tk.Button(  # Botón para cambiar entre modo FightCade y Challonge
            self.root,
            text="Modo FightCade",
            font=("Arial", 8),
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            command=self.toggle_mode_text
        )
        self.mode_button.place(x=1133.0, y=98.0, width=140.0, height=20.0)  # Posiciona botón
        self.entry_dir = tk.Entry(  # Campo de texto para directorio FightCade
            self.root,
            textvariable=self.directory_var,
            font=("Arial", 8),
        )
        
        # --- Estado del partido actual ---
        self.loaded_match = None  # Almacena datos del partido actualmente cargado
        self.original_match_data = {}  # Datos originales del partido cargado
        self.current_tournament_id = None  # ID del torneo actualmente seleccionado
        self.matches_data = []  # Lista de partidos del torneo actual
        self.tournaments_list = []  # Lista de torneos disponibles
        
        # --- Variables Control de modo (FightCade) ---
        self.mode_var = tk.StringVar(value="manual")  # Modo actual (manual/automático)
        self.manual_order_confirmed = False  # Indica si se confirmó orden manual
        self.auto_update_paused = False  # Indica si se pausó la autoactualización
        
        # --- Variables Puntajes y notificaciones ---
        self.score1 = tk.IntVar()  # Variable para puntaje jugador 1
        self.score2 = tk.IntVar()  # Variable para puntaje jugador 2
        self.after_id = None  # ID para programar acciones posteriores
        self.auto_update_id = None  # ID para programar actualizaciones automáticas
        
        # --- Variables Set Default Botones gráficos ---
        self.button_submit = None  # Referencia al botón de subir resultados
        self.button_reopen = None  # Referencia al botón de reabrir partido
        
        # --- Variable para next_match ---
        self.next_match_var = tk.StringVar()  # Variable para siguiente partido
        
        # Cargar directorio de FightCade desde archivo
        if os.path.exists(FC_DIRECTORY_FILE):  # Si existe archivo de directorio guardado
            with open(FC_DIRECTORY_FILE, "r") as f:  # Abre archivo en modo lectura
                dir_path = f.read().strip()  # Lee y limpia espacios del directorio
            if os.path.isdir(dir_path):  # Si es un directorio válido
                self.directory_var.set(dir_path)  # Establece valor en variable
                self.entry_dir.delete(0, tk.END)  # Limpia campo de texto
                self.entry_dir.insert(0, dir_path)  # Inserta directorio en campo
        
        # Cargar credenciales guardadas
        self.load_saved_credentials()  # Llama método para cargar credenciales
        
        # Crear widgets
        self.create_widgets()  # Crea todos los elementos visuales de la interfaz
        
        # Conectar automáticamente si ya hay credenciales
        if self.user_var.get() and self.api_key_var.get():  # Si hay usuario y clave guardados
            self.connect_to_challonge()  # Conecta automáticamente a Challonge
        
        # Boton Subir a challonge deshabilitado
        if hasattr(self, "button_submit"):  # Si existe el botón de subir resultados
            self.button_submit.config(state="disabled")  # Lo inicializa deshabilitado

    def create_widgets(self):
        # Canvas principal
        self.canvas = Canvas(  # Crea el lienzo principal donde se colocarán los elementos gráficos
            self.root,  # Ventana principal de la aplicación
            bg="#FFFFFF",  # Color de fondo blanco
            height=768,  # Altura del lienzo en píxeles
            width=1366,  # Ancho del lienzo en píxeles
            bd=0,  # Borde del lienzo (0 para no mostrarlo)
            highlightthickness=0,  # Sin resaltado alrededor del lienzo
            relief="ridge"  # Estilo del borde (no visible aquí por bd=0)
        )
        self.canvas.place(x=0, y=0)  # Posiciona el lienzo en la esquina superior izquierda
        
        # Imagen fondo (ui_background.png)
        try:  # Intenta cargar la imagen de fondo
            self.image_image_1 = PhotoImage(file=relative_to_assets("ui_background.png"))  # Carga la imagen
            self.image_1 = self.canvas.create_image(683.0, 384.0, image=self.image_image_1)  # Coloca la imagen centrada
        except Exception as e:  # Si hay error al cargar la imagen
            print("Error al cargar ui_background.png.", e)  # Muestra mensaje de error
        
        # Notificaciones
        self.notification_label = tk.Label(  # Etiqueta para mostrar mensajes emergentes
            self.root,  # Ventana principal
            text="",  # Texto inicial vacío
            bg="#24000c",  # Fondo oscuro
            fg="#FFFFFF",  # Texto en color blanco
            wraplength=319,  # Longitud máxima antes de saltar línea
            font=("Arial Black", 12, "bold"),  # Fuente del texto
            anchor="center"  # Alineación del texto al centro
        )
        self.notification_label.place(x=550.0, y=10.0, width=319.0, height=30.0)  # Posición y tamaño de la notificación
        
        # Combobox Seleccionar Torneo
        self.combobox_tournament = ttk.Combobox(  # Campo desplegable para seleccionar torneo
            self.root,  # Ventana principal
            textvariable=self.tournament_var,  # Variable asociada para almacenar valor seleccionado
            state="readonly",  # Solo permite selección, no edición
            font=("Arial", 8)  # Fuente del texto
        )
        self.combobox_tournament.place(x=119.0, y=34.0, width=209.0, height=20.0)  # Posición y tamaño del combobox
        self.combobox_tournament.bind("<<ComboboxSelected>>", lambda e: self.load_matches())  # Acción al seleccionar un torneo
        
        # Combobox Seleccionar Match
        self.combobox_match = ttk.Combobox(  # Campo desplegable para seleccionar partido
            self.root,  # Ventana principal
            textvariable=self.match_var,  # Variable asociada para almacenar valor seleccionado
            state="readonly",  # Solo permite selección, no edición
            font=("Arial", 8)  # Fuente del texto
        )
        self.combobox_match.place(x=119.0, y=66.0, width=209.0, height=20.0)  # Posición y tamaño del combobox
        self.combobox_match.bind("<<ComboboxSelected>>", lambda e: (self.load_selected_match(e)))  # Acción al seleccionar partido
        
        # Combobox Next Match
        self.combobox_next_match = ttk.Combobox(  # Campo desplegable para siguiente partido
            self.root,  # Ventana principal
            textvariable=self.next_match_var,  # Variable asociada para almacenar valor seleccionado
            state="readonly",  # Solo permite selección, no edición
            font=("Arial", 8),  # Fuente del texto
            values=[]  # Lista vacía inicialmente
        )
        self.combobox_next_match.place(x=1153.0, y=140.0, width=199.0, height=20.0)  # Posición y tamaño del combobox
        self.combobox_next_match.set("")  # Iniciar vacío
        
        # Vincular evento de selección
        self.combobox_next_match.bind("<<ComboboxSelected>>", self.on_next_match_selected)  # Acción al seleccionar siguiente partido
        
        # Entry Usuario
        self.entry_user = tk.Entry(  # Campo de entrada para nombre de usuario
            self.root,  # Ventana principal
            textvariable=self.user_var,  # Variable asociada para almacenar el valor
            font=("Arial Black", 8),  # Fuente del texto
            show=""  # Muestra el texto normalmente (no como contraseña)
        )
        self.entry_user.place(x=1153.0, y=48.0, width=140.0, height=20.0)  # Posición y tamaño del campo
        
        # Entry API Key
        self.entry_apikey = tk.Entry(  # Campo de entrada para clave API
            self.root,  # Ventana principal
            textvariable=self.api_key_var,  # Variable asociada para almacenar el valor
            font=("Arial Black", 8),  # Fuente del texto
            show="*"  # Oculta el texto introducido (para seguridad)
        )
        self.entry_apikey.place(x=1153.0, y=78.0, width=140.0, height=20.0)  # Posición y tamaño del campo
        
        # Botón conectar (login.png)
        try:  # Intenta cargar la imagen del botón
            self.button_connect_image = PhotoImage(file=relative_to_assets("login.png"))  # Carga la imagen del botón
            self.button_connect = tk.Button(  # Crea el botón de conexión
                image=self.button_connect_image,  # Imagen del botón
                borderwidth=0,  # Sin borde
                highlightthickness=0,  # Sin resaltado
                command=self.connect_to_challonge,  # Acción al hacer clic
                relief="flat"  # Estilo plano del botón
            )
            self.button_connect.place(x=1303.0, y=50.0, width=45.0, height=45.0)  # Posición y tamaño del botón
        except Exception as e:  # Si hay error al cargar la imagen
            print("Error al cargar login.png.", e)  # Muestra mensaje de error
        
        # Etiqueta "Usuario:"
        self.canvas.create_text(  # Crea texto en el lienzo
            1098.0,  # Coordenada X
            50.0,  # Coordenada Y
            anchor="nw",  # Anclaje al noroeste (esquina superior izquierda)
            text="Usuario:",  # Texto a mostrar
            fill="#FFFFFF",  # Color del texto
            font=("Arial Black", 8, "bold")  # Fuente del texto
        )
        
        # Etiqueta "APIKEY:"
        self.canvas.create_text(  # Crea texto en el lienzo
            1098.0,  # Coordenada X
            80.0,  # Coordenada Y
            anchor="nw",  # Anclaje al noroeste
            text="APIKEY:",  # Texto a mostrar
            fill="#FFFFFF",  # Color del texto
            font=("Arial Black", 8, "bold")  # Fuente del texto
        )
        
        # Etiqueta "Next Match:"
        self.canvas.create_text(  # Crea texto en el lienzo
            1062.0,  # Coordenada X
            142.0,  # Coordenada Y
            anchor="nw",  # Anclaje al noroeste
            text="NEXT MATCH:",  # Texto a mostrar
            fill="#FFFFFF",  # Color del texto
            font=("Arial Black", 8, "bold")  # Fuente del texto
        )
        
        # Botón Examinar (examinar.png)
        try:  # Intenta cargar la imagen del botón
            self.examine_button_image = PhotoImage(file=relative_to_assets("examinar.png"))  # Carga la imagen del botón
            self.button_browse = tk.Button(  # Crea el botón para buscar directorio
                image=self.examine_button_image,  # Imagen del botón
                borderwidth=0,  # Sin borde
                highlightthickness=0,  # Sin resaltado
                command=self.browse_directory,  # Acción al hacer clic
                relief="flat"  # Estilo plano del botón
            )
            self.button_browse.place(x=309.0, y=125.0, width=20.0, height=20.0)  # Posición y tamaño del botón
        except Exception as e:  # Si hay error al cargar la imagen
            print("Error al crear examinar.png", e)  # Muestra mensaje de error
        
        # Campo Directorio
        self.entry_dir = tk.Entry(  # Campo de texto para mostrar ruta del directorio
            self.root,  # Ventana principal
            textvariable=self.directory_var,  # Variable asociada para almacenar valor
            font=("Arial", 8),  # Fuente del texto
            bg="#FFFFFF",  # Fondo blanco
            fg="#000716"  # Color del texto
        )
        self.entry_dir.place(x=119.0, y=125.0, width=181.0, height=20.0)  # Posición y tamaño del campo
        self.entry_dir.config(state="disabled")  # Deshabilitado por defecto
        
        # Jugadores (Nick Player1 y Nick Player2 - texto por defecto)
        self.player1_name = self.canvas.create_text(  # Nombre del jugador 1 en pantalla
            450.0,  # Coordenada X
            85.0,  # Coordenada Y
            anchor="center",  # Centrado horizontalmente
            text="Nick Player1",  # Texto por defecto
            fill="#FFFFFF",  # Color del texto
            font=("Arial Black", 15, "bold"),  # Fuente del texto
            justify="center",  # Justificado al centro
            width=150  # Ancho máximo del texto
        )
        self.player2_name = self.canvas.create_text(  # Nombre del jugador 2 en pantalla
            930.0,  # Coordenada X
            85.0,  # Coordenada Y
            anchor="center",  # Centrado horizontalmente
            text="Nick Player2",  # Texto por defecto
            fill="#FFFFFF",  # Color del texto
            font=("Arial Black", 15, "bold"),  # Fuente del texto
            justify="center",  # Justificado al centro
            width=150  # Ancho máximo del texto
        )
        
        # Puntajes (0 por defecto)
        self.score1 = tk.IntVar(value=0)  # Variable para puntaje del jugador 1
        self.score2 = tk.IntVar(value=0)  # Variable para puntaje del jugador 2
        
        # Etiqueta para mostrar ronda ("Round 1", "Final", etc.)
        self.round_info_label = self.canvas.create_text(  # Muestra información de la ronda actual
            1500.0,  # Coordenada X
            75.0,  # Coordenada Y
            anchor="nw",  # Anclaje al noroeste
            text="Round Info",  # Texto por defecto
            fill="#FFFFFF",  # Color del texto
            font=("Arial", 10, "bold"),  # Fuente del texto
            justify="center"  # Justificado al centro
        )
        self.score1_label = self.canvas.create_text(  # Puntaje del jugador 1
            592.0,  # Coordenada X
            40.0,  # Coordenada Y
            anchor="nw",  # Anclaje al noroeste
            text="0",  # Valor inicial
            fill="#FFFFFF",  # Color del texto
            font=("Arial Black", 48, "bold"),  # Fuente del texto
            justify="center",  # Justificado al centro
            width=100  # Ancho máximo del texto
        )
        self.score2_label = self.canvas.create_text(  # Puntaje del jugador 2
            738.0,  # Coordenada X
            40.0,  # Coordenada Y
            anchor="nw",  # Anclaje al noroeste
            text="0",  # Valor inicial
            fill="#FFFFFF",  # Color del texto
            font=("Arial Black", 48, "bold"),  # Fuente del texto
            justify="center",  # Justificado al centro
            width=100  # Ancho máximo del texto
        )
        self.vs_label = self.canvas.create_text(  # Texto que muestra "V/S"
            683.0,  # Coordenada X
            67.0,  # Coordenada Y
            anchor="nw",  # Anclaje al noroeste
            text="V/S",  # Texto a mostrar
            fill="#FFFFFF",  # Color del texto
            font=("Arial Black", 20, "bold"),  # Fuente del texto
            justify="center",  # Justificado al centro
            width=70  # Ancho máximo del texto
        )
        
        # Botones de +1/-1
        try:  # Intenta crear el botón de +1 para jugador 1
            self.button_add1 = tk.Button(  # Botón para aumentar puntaje jugador 1
                self.root,  # Ventana principal
                text="+1",  # Texto del botón
                command=self.add_point_player1,  # Acción al hacer clic
                font=("Arial", 10, "bold"),  # Fuente del texto
                bg="#00FF15",  # Fondo verde claro
                fg="#000716"  # Color del texto
            )
            self.button_add1.place(x=380.0, y=15.0, width=25.0, height=25.0)  # Posición y tamaño del botón
        except Exception as e:  # En caso de error
            print("Error al cargar botón +1 (player1).", e)  # Muestra mensaje de error
        try:  # Intenta crear el botón de -1 para jugador 1
            self.button_minus1 = tk.Button(  # Botón para disminuir puntaje jugador 1
                self.root,  # Ventana principal
                text="-1",  # Texto del botón
                command=self.minus_point_player1,  # Acción al hacer clic
                font=("Arial", 10, "bold"),  # Fuente del texto
                bg="#cf0000",  # Fondo rojo oscuro
                fg="#000716"  # Color del texto
            )
            self.button_minus1.place(x=350.0, y=15.0, width=25.0, height=25.0)  # Posición y tamaño del botón
        except Exception as e:  # En caso de error
            print("Error al cargar botón -1 (player1).", e)  # Muestra mensaje de error
        try:  # Intenta crear el botón de +1 para jugador 2
            self.button_add2 = tk.Button(  # Botón para aumentar puntaje jugador 2
                self.root,  # Ventana principal
                text="+1",  # Texto del botón
                command=self.add_point_player2,  # Acción al hacer clic
                font=("Arial", 10, "bold"),  # Fuente del texto
                bg="#00FF15",  # Fondo verde claro
                fg="#000716"  # Color del texto
            )
            self.button_add2.place(x=1023.0, y=15.0, width=25.0, height=25.0)  # Posición y tamaño del botón
        except Exception as e:  # En caso de error
            print("Error al cargar botón +1 (player2)", e)  # Muestra mensaje de error
        try:  # Intenta crear el botón de -1 para jugador 2
            self.button_minus2 = tk.Button(  # Botón para disminuir puntaje jugador 2
                self.root,  # Ventana principal
                text="-1",  # Texto del botón
                command=self.minus_point_player2,  # Acción al hacer clic
                font=("Arial", 10, "bold"),  # Fuente del texto
                bg="#cf0000",  # Fondo rojo oscuro
                fg="#000716"  # Color del texto
            )
            self.button_minus2.place(x=993.0, y=15.0, width=25.0, height=25.0)  # Posición y tamaño del botón
        except Exception as e:  # En caso de error
            print("Error al cargar botón -1 (player2).", e)  # Muestra mensaje de error
        
        # Botón Subir Resultados (upload_results.png)
        try:  # Intenta cargar la imagen del botón
            self.submit_results_image = PhotoImage(file=relative_to_assets("upload_results.png"))  # Carga la imagen
            self.button_submit = tk.Button(  # Botón para subir resultados
                image=self.submit_results_image,  # Imagen del botón
                borderwidth=0,  # Sin borde
                highlightthickness=0,  # Sin resaltado
                command=self.submit_result,  # Acción al hacer clic
                relief="flat"  # Estilo plano
            )
            self.button_submit.image = self.submit_results_image  # Evita que sea eliminada por el recolector de memoria
            self.button_submit.place(x=563.0, y=135.0, width=300.0, height=30.0)  # Posición y tamaño del botón
            self.button_submit.config(state="disabled")  # ← Esta línea es clave
        except Exception as e:  # En caso de error
            print("Error al cargar upload_results.png.", e)  # Muestra mensaje de error
        
        # Botón Re-Abrir Match (reopen_match.png)
        try:  # Intenta cargar la imagen del botón
            self.reopen_match_image = PhotoImage(file=relative_to_assets("reopen_match.png"))  # Carga la imagen
            self.button_reopen = tk.Button(  # Botón para reabrir partido
                image=self.reopen_match_image,  # Imagen del botón
                borderwidth=0,  # Sin borde
                highlightthickness=0,  # Sin resaltado
                command=self.reopen_match,  # Acción al hacer clic
                relief="flat"  # Estilo plano
            )
            self.button_reopen.image = self.reopen_match_image  # ← Mantén la referencia
            self.button_reopen.place(x=879.0, y=10.0, width=30.0, height=30.0)  # Posición y tamaño del botón
            self.button_reopen.config(state="disabled")  # Deshabilitado inicialmente
            if hasattr(self, "button_reopen"):  # Si el botón existe
                self.button_reopen.config(state="disabled")  # Lo mantiene deshabilitado
        except Exception as e:  # En caso de error
            print("Error al cargar reopen_match.png.", e)  # Muestra mensaje de error
        
        # Combobox FT Torneo
        self.combo_ft_tournament = ttk.Combobox(  # Campo desplegable para FT Torneo
            self.root,  # Ventana principal
            textvariable=self.ft_tournament_var,  # Variable asociada
            values=["FT1", "FT2", "FT3", "FT4", "FT5", "FT6", "FT7", "FT8", "FT9", "FT10"],  # Opciones disponibles
            state="readonly",  # Solo lectura
            font=("Arial", 8)  # Fuente del texto
        )
        self.combo_ft_tournament.place(x=119.0, y=96.0, width=50.0, height=20.0)  # Posición y tamaño
        
        # Combobox FT Final
        self.combo_ft_final = ttk.Combobox(  # Campo desplegable para FT Final
            self.root,  # Ventana principal
            textvariable=self.ft_final_var,  # Variable asociada
            values=["FT1", "FT2", "FT3", "FT4", "FT5", "FT6", "FT7", "FT8", "FT9", "FT10"],  # Opciones disponibles
            state="readonly",  # Solo lectura
            font=("Arial", 8)  # Fuente del texto
        )
        self.combo_ft_final.place(x=278.0, y=96.0, width=50.0, height=20.0)  # Posición y tamaño
        self.combo_ft_tournament.bind("<<ComboboxSelected>>", self.on_ft_change)  # Acción al seleccionar
        self.combo_ft_final.bind("<<ComboboxSelected>>", self.on_ft_change)  # Acción al seleccionar
        
        # Winners Bracket
        self.winners_frame = tk.Frame(self.root, bg="#FFFFFF")  # Marco para bracket ganadores
        self.winners_frame.place(x=10.0, y=201.0, width=1346.0, height=200.0)  # Posición y tamaño
        self.winners_canvas = Canvas(self.winners_frame, bg="#FFFFFF", highlightthickness=0)  # Lienzo para scroll
        self.winners_scroll_x = tk.Scrollbar(self.winners_frame, orient="horizontal", command=self.winners_canvas.xview)  # Scroll horizontal
        self.winners_scroll_y = tk.Scrollbar(self.winners_frame, orient="vertical", command=self.winners_canvas.yview)  # Scroll vertical
        self.winners_container = tk.Frame(self.winners_canvas, bg="#FFFFFF", height=260)  # Contenedor interno
        self.winners_container.pack_propagate(False)  # Impide redimensionamiento automático
        self.winners_canvas.configure(  # Configura el lienzo
            xscrollcommand=self.winners_scroll_x.set,  # Asocia scroll horizontal
            yscrollcommand=self.winners_scroll_y.set  # Asocia scroll vertical
        )
        self.winners_canvas.create_window((0, 0), window=self.winners_container, anchor="nw", width=3000, tags="winners_window")  # Crea ventana interna
        self.winners_canvas.pack(side="left", fill="both", expand=True)  # Empaqueta el lienzo
        self.winners_scroll_x.place(x=0, y=185, width=1346, height=15)  # Posición del scroll horizontal
        self.winners_scroll_y.place(x=1326, y=0, width=15, height=180)  # Posición del scroll vertical
        def on_configure_winners(e):  # Función para ajustar scroll región
            self.winners_canvas.configure(scrollregion=self.winners_canvas.bbox("all"))  # Ajusta región de scroll
        self.winners_container.bind("<Configure>", on_configure_winners)  # Ejecuta función al cambiar tamaño
        self.winners_canvas.bind("<Configure>", lambda e: self.winners_canvas.configure(scrollregion=self.winners_canvas.bbox("all")))  # También ajusta región
        
        # Losers Bracket
        self.losers_frame = tk.Frame(self.root, bg="#FFFFFF")  # Marco para bracket perdedores
        self.losers_frame.place(x=10.0, y=446.0, width=1346.0, height=222.0)  # Posición y tamaño
        self.losers_canvas = Canvas(self.losers_frame, bg="#FFFFFF", highlightthickness=0)  # Lienzo para scroll
        self.losers_scroll_x = tk.Scrollbar(self.losers_frame, orient="horizontal", command=self.losers_canvas.xview)  # Scroll horizontal
        self.losers_scroll_y = tk.Scrollbar(self.losers_frame, orient="vertical", command=self.losers_canvas.yview)  # Scroll vertical
        self.losers_container = tk.Frame(self.losers_canvas, bg="#FFFFFF", height=260)  # Contenedor interno
        self.losers_container.pack_propagate(False)  # Impide redimensionamiento automático
        self.losers_canvas.configure(  # Configura el lienzo
            xscrollcommand=self.losers_scroll_x.set,  # Asocia scroll horizontal
            yscrollcommand=self.losers_scroll_y.set  # Asocia scroll vertical
        )
        self.losers_canvas.create_window((0, 0), window=self.losers_container, anchor="nw", width=3000, tags="losers_window")  # Crea ventana interna
        self.losers_canvas.pack(side="left", fill="both", expand=True)  # Empaqueta el lienzo
        self.losers_scroll_x.place(x=0, y=207, width=1346, height=15)  # Posición del scroll horizontal
        self.losers_scroll_y.place(x=1326, y=0, width=15, height=202)  # Posición del scroll vertical
        def on_configure_losers(e):  # Función para ajustar scroll región
            self.losers_canvas.configure(scrollregion=self.losers_canvas.bbox("all"))  # Ajusta región de scroll
        self.losers_container.bind("<Configure>", on_configure_losers)  # Ejecuta función al cambiar tamaño
        self.losers_canvas.bind("<Configure>", lambda e: self.losers_canvas.configure(scrollregion=self.losers_canvas.bbox("all")))  # También ajusta región
        def on_mousewheel_winners(event):  # Función de scroll para Winners
            self.winners_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")  # Desplazamiento vertical
        def on_shift_mousewheel_winners(event):  # Función de scroll horizontal para Winners
            self.winners_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")  # Desplazamiento horizontal
        def on_mousewheel_losers(event):  # Función de scroll para Losers
            self.losers_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")  # Desplazamiento vertical
        def on_shift_mousewheel_losers(event):  # Función de scroll horizontal para Losers
            self.losers_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")  # Desplazamiento horizontal
        
        # Asignar eventos de scroll con rueda del mouse
        self.winners_canvas.bind("<MouseWheel>", on_mousewheel_winners)  # Scroll vertical
        self.winners_canvas.bind("<Shift-MouseWheel>", on_shift_mousewheel_winners)  # Scroll horizontal
        self.losers_canvas.bind("<MouseWheel>", on_mousewheel_losers)  # Scroll vertical
        self.losers_canvas.bind("<Shift-MouseWheel>", on_shift_mousewheel_losers)  # Scroll horizontal
        
        # Textos selección de torneo, match y directorio FC2
        self.canvas.create_text(  # Crea texto en el lienzo
            22.0,  # Coordenada X
            36.0,  # Coordenada Y
            anchor="nw",  # Anclaje al noroeste
            text="Selec. Torneo:",  # Texto a mostrar
            fill="#FFFFFF",  # Color del texto
            font=("Arial Black", 8, "bold")  # Fuente del texto
        )
        self.canvas.create_text(  # Crea texto en el lienzo
            27.0,  # Coordenada X
            68.0,  # Coordenada Y
            anchor="nw",  # Anclaje al noroeste
            text="Selec. Match:",  # Texto a mostrar
            fill="#FFFFFF",  # Color del texto
            font=("Arial Black", 8, "bold")  # Fuente del texto
        )
        self.canvas.create_text(  # Crea texto en el lienzo
            60.0,  # Coordenada X
            127.0,  # Coordenada Y
            anchor="nw",  # Anclaje al noroeste
            text="FC2 Dir:",  # Texto a mostrar
            fill="#FFFFFF",  # Color del texto
            font=("Arial Black", 8, "bold")  # Fuente del texto
        )
        self.canvas.create_text(  # Crea texto en el lienzo
            45.0,  # Coordenada X
            98.0,  # Coordenada Y
            anchor="nw",  # Anclaje al noroeste
            text="FT Torneo:",  # Texto a mostrar
            fill="#FFFFFF",  # Color del texto
            font=("Arial Black", 8, "bold")  # Fuente del texto
        )
        self.canvas.create_text(  # Crea texto en el lienzo
            218.0,  # Coordenada X
            98.0,  # Coordenada Y
            anchor="nw",  # Anclaje al noroeste
            text="FT Final:",  # Texto a mostrar
            fill="#FFFFFF",  # Color del texto
            font=("Arial Black", 8, "bold")  # Fuente del texto
        )
        self.update_score_display()  # Actualiza visualización de puntajes

    def load_saved_credentials(self):
        if os.path.exists(CREDENTIALS_FILE):  # Verifica si existe el archivo de credenciales guardadas
            with open(CREDENTIALS_FILE, "r") as f:  # Abre el archivo en modo lectura
                data = json.load(f)  # Carga los datos JSON desde el archivo
                self.user_var.set(data.get("user", ""))  # Establece el valor del usuario desde el archivo
                self.api_key_var.set(data.get("api_key", ""))  # Establece la API Key desde el archivo

    def save_credentials(self):
        with open(CREDENTIALS_FILE, "w") as f:  # Abre el archivo en modo escritura (sobrescribirá contenido)
            json.dump({  # Guarda las credenciales actuales en formato JSON
                "user": self.user_var.get(),  # Obtiene el valor actual del campo de usuario
                "api_key": self.api_key_var.get()  # Obtiene el valor actual del campo de API Key
            }, f)  # Escribe los datos en el archivo

    def connect_to_challonge(self):
        user = self.user_var.get().strip()  # Obtiene y limpia espacios al inicio/fin del nombre de usuario
        api_key = self.api_key_var.get().strip()  # Obtiene y limpia espacios al inicio/fin de la API Key

        if not user or not api_key:  # Si alguno está vacío o None
            messagebox.showerror("Error", texts["credentials"])  # Muestra mensaje de error
            return  # Sale del método si no hay credenciales

        try:
            challonge.set_credentials(user, api_key)  # Configura las credenciales para Challonge API

            # Cargar lista completa de torneos
            tournaments = challonge.tournaments.index()  # Obtiene todos los torneos disponibles
            double_elimination_tournaments = []  # Lista para almacenar solo torneos de doble eliminación

            for t in tournaments:  # Itera sobre todos los torneos obtenidos
                if t["state"] in ["in_progress", "underway"]:  # Filtra por estado activo
                    full_tournament = challonge.tournaments.show(t["id"])  # Obtiene detalles completos del torneo
                    tournament_type = full_tournament.get("tournament_type", "").strip().lower()  # Obtiene tipo y lo pasa a minúsculas
                    if tournament_type == "double elimination":  # Comprueba si es de doble eliminación
                        double_elimination_tournaments.append(t)  # Añade a la lista de torneos válidos

            if not double_elimination_tournaments:  # Si no hay torneos válidos
                messagebox.showinfo("Sin torneos de doble eliminación.", texts["no_tournament"])  # Muestra mensaje informativo
                return  # Sale del método si no hay torneos

            self.save_credentials()  # Guarda las credenciales localmente
            self.tournaments_list = double_elimination_tournaments  # Asigna lista de torneos a variable de instancia
            self.combobox_tournament["values"] = [t["name"] for t in double_elimination_tournaments]  # Llena combobox con nombres de torneos
            self.combobox_tournament.config(state="readonly")  # Habilita el combobox como solo lectura
            self.combobox_tournament.set("")  # Limpia selección inicial

            # Deshabilitar partido hasta que haya torneo elegido
            self.combobox_match.config(state="disabled")  # Deshabilita el combobox de partidos
            self.combobox_match.set("")  # Limpia cualquier selección previa
            self.notification_label.config(text="")  # Limpia cualquier notificación existente

            # Mostrar mensaje en notificación
            self.show_notification("FC2Challonge Control v1.0", duration=3000, permanent=True)  # Muestra mensaje de bienvenida durante 3 segundos

            # Forzar revisión de FT después de conectar
            self.root.after(2000, self.on_ft_change)  # Programa una acción para verificar FT tras 2 segundos

            if hasattr(self, "combobox_match"):  # Si el combobox_match existe
                self.combobox_match.config(state="disabled")  # Lo mantiene deshabilitado

        except Exception as e:  # Captura cualquier excepción durante la conexión
            print("Error al conectar con Challonge.", str(e))  # Muestra mensaje de error en consola
            messagebox.showerror("Error", f"{texts['invalid_creds']}\n{str(e)}")  # Muestra mensaje de error en GUI

    def show_notification(self, message, duration=2000, permanent=False):
        #Muestra una notificación en pantalla y maneja los after_ids de forma segura
        # Limpiar notificación anterior si existe
        if hasattr(self, "_notification_after_id") and self._notification_after_id is not None:  # Si ya hay un temporizador activo
            try:
                self.root.after_cancel(self._notification_after_id)  # Cancela la acción programada
            except:
                pass  # Ignora errores al cancelar

        # Actualizar texto de notificación
        self.notification_label.config(text=message)  # Establece el nuevo mensaje en la etiqueta

        # Si no es permanente, programar limpieza después de X segundos
        if not permanent:  # Si no debe mantenerse siempre visible
            self._notification_after_id = self.root.after(duration, lambda: self.notification_label.config(text=""))  # Programa limpieza
        else:
            self._notification_after_id = None  # No programar limpieza si es permanente

    def load_matches(self, event=None):
        ft_tournament = self.combo_ft_tournament.get()  # Obtiene el valor seleccionado en FT Torneo
        ft_final = self.combo_ft_final.get()  # Obtiene el valor seleccionado en FT Final

        if not ft_tournament or not ft_final:  # Si alguno está vacío
            messagebox.showwarning(  # Muestra advertencia
                "Configuración incompleta.",
                "Por favor selecciona valores en ambos campos 'FT Torneo' y 'FT Final' antes de cargar un Match."
            )
            return  # Sale del método si no están ambos seleccionados

        tournament_index = self.combobox_tournament.current()  # Obtiene índice del torneo seleccionado
        if tournament_index == -1:  # Si no hay selección válida
            return  # Sale del método si no hay torneo seleccionado

        tournament = self.tournaments_list[tournament_index]  # Obtiene datos del torneo seleccionado
        tournament_id = tournament["id"]  # Extrae el ID del torneo
        self.current_tournament_id = tournament_id  # Almacena el ID actualmente seleccionado

        try:
            matches = challonge.matches.index(tournament_id)  # Obtiene todos los partidos del torneo
            participants = {p["id"]: p["name"] for p in challonge.participants.index(tournament_id)}  # Diccionario de participantes

            self.matches_data = []  # Reinicia lista de datos de partidos
            match_list = []  # Lista temporal para mostrar en interfaz

            for match in matches:  # Itera sobre todos los partidos del torneo
                p1_name = participants.get(match["player1_id"], "") or match.get("player1_placeholder_text", "?")  # Nombre jugador 1
                p2_name = participants.get(match["player2_id"], "") or match.get("player2_placeholder_text", "?")  # Nombre jugador 2

                # Verificar que ambos jugadores estén definidos y el partido no esté cerrado
                if (p1_name not in ["?", "?"] and   # Si jugador 1 tiene nombre válido
                    p2_name not in ["?", "?"] and   # Si jugador 2 tiene nombre válido
                    match["state"] == "open"):       # Y el partido aún está abierto

                    display_text = f"{p1_name} vs {p2_name}"  # Crea texto para mostrar en UI
                    match_list.append(display_text)  # Añade texto a lista de visualización
                    match["p1_name"] = p1_name  # Añade nombre jugador 1 al objeto match
                    match["p2_name"] = p2_name  # Añade nombre jugador 2 al objeto match
                    self.matches_data.append(match)  # Añade partido completo a datos internos

            # Actualizar combobox_match
            self.combobox_match["values"] = match_list  # Asigna lista de partidos al combo
            if match_list:  # Si hay partidos disponibles
                self.combobox_match.config(state="readonly")  # Habilita el combo
                self.combobox_match.set("")  # Limpia selección inicial
                self.notification_label.config(text="Elija Partido!", fg="#FFFFFF")  # Pide seleccionar partido
            else:  # Si no hay partidos disponibles
                self.combobox_match.config(state="disabled")  # Deshabilita el combo
                self.combobox_match.set("")  # Limpia cualquier selección
                self.notification_label.config(text="No hay Matches disponibles.")  # Notifica ausencia de partidos

            self.draw_bracket()  # Dibuja el bracket en pantalla

        except Exception as e:  # En caso de error
            messagebox.showerror("Error", f"No se pudieron cargar los matches.\n{str(e)}")  # Muestra mensaje de error
        
    def draw_bracket(self):
        for widget in self.winners_container.winfo_children():  # Limpia todos los widgets dentro de winners_container
            widget.destroy()  # Elimina cada widget hijo para redibujar
        for widget in self.losers_container.winfo_children():  # Limpia todos los widgets dentro de losers_container
            widget.destroy()  # Elimina cada widget hijo para redibujar
        if not self.current_tournament_id:  # Si no hay torneo actualmente seleccionado
            return  # Sale del método si no hay torneo
        try:
            matches = challonge.matches.index(self.current_tournament_id)  # Obtiene la lista de partidos del torneo actual
            participants = {p["id"]: p["name"] for p in challonge.participants.index(self.current_tournament_id)}  # Crea diccionario de participantes
            if not participants:  # Si no hay participantes cargados
                raise ValueError("No se encontraron participantes para este torneo.")  # Lanza error si no hay participantes
            winners_by_round = {}  # Diccionario para agrupar partidos por ronda en Winners Bracket
            losers_by_round = {}  # Diccionario para agrupar partidos por ronda en Losers Bracket
            total_players = len(participants) if participants else 8  # Calcula cantidad de jugadores o usa 8 como predeterminado
            rounds_before_finals = int(math.log2(total_players)) if total_players > 0 else 3  # Calcula rondas antes de semifinales
            # Separar partidos en Winners Bracket
            for match in matches:  # Itera sobre cada partido obtenido
                rnd = match["round"]  # Obtiene la ronda del partido
                if rnd > 0:  # Si es una ronda positiva (Winners Bracket)
                    if rnd == rounds_before_finals:  # Si es semifinales
                        key = 1000  # Clave especial para semifinales
                    elif rnd == rounds_before_finals + 1:  # Si es final
                        key = 1001  # Clave especial para final
                    elif rnd == rounds_before_finals + 2:  # Si es gran final
                        key = 1002  # Clave especial para gran final
                    else:  # Para cualquier otra ronda normal
                        key = rnd  # Usa número de ronda directamente
                    if key not in winners_by_round:  # Si no existe la clave aún
                        winners_by_round[key] = []  # Inicializa lista vacía
                    winners_by_round[key].append(match)  # Añade partido al grupo correspondiente
                elif rnd < 0:  # Si es una ronda negativa (Losers Bracket)
                    abs_rnd = abs(rnd)  # Toma valor absoluto de la ronda
                    if abs_rnd not in losers_by_round:  # Si no existe la clave aún
                        losers_by_round[abs_rnd] = []  # Inicializa lista vacía
                    losers_by_round[abs_rnd].append(match)  # Añade partido al grupo correspondiente
            # Dibujar partidos en orden lógico
            self.display_horizontal_bracket(self.winners_container, winners_by_round, participants, is_losers=False)  # Dibuja partidos en Winners Bracket
            self.display_horizontal_bracket(self.losers_container, losers_by_round, participants, is_losers=True)  # Dibuja partidos en Losers Bracket
        except Exception as e:  # Captura cualquier excepción durante el proceso
            messagebox.showerror("Error", f"No se pudo dibujar el bracket.\n{str(e)}")  # Muestra mensaje de error

    def display_horizontal_bracket(self, container, rounds_dict, participants, is_losers=False):
        # Ordenar claves con "Rondas normales primero", luego "Semifinales", "Final", etc.
        sorted_rounds = sorted(rounds_dict.keys())  # Ordena las claves numéricamente
        special_keys = [1000, 1001, 1002]  # Claves especiales para partidos finales
        for key in special_keys:  # Procesa cada clave especial
            if key in sorted_rounds:  # Si ya está en la lista
                sorted_rounds.remove(key)  # La elimina temporalmente
                sorted_rounds.append(key)  # Y la añade al final para mostrarla al final
        for key in sorted_rounds:  # Itera sobre cada ronda procesada
            matches_in_round = rounds_dict[key]  # Obtiene los partidos de esta ronda
            # Generar título de ronda
            if key in [1000, 1001, 1002]:  # Si es una ronda especial
                title = {  # Asigna nombre según tipo de ronda
                    1000: "Semifinales",
                    1001: "Final",
                    1002: "Grand Final"
                }.get(key, "Desconocido")  # Valor por defecto en caso de error
            else:  # Para rondas normales
                title = self.get_round_description(key, len(participants)) if not is_losers else self.get_round_description(-key, len(participants))  # Obtiene descripción según sea Winners o Losers
            frame = tk.Frame(container, bg="#f5f5f5")  # Crea marco para esta ronda
            frame.pack(side="left", fill="y", padx=5, pady=5)  # Lo posiciona horizontalmente
            # Título del round ENCIMA de los partidos
            tk.Label(frame, text=title, font=("Arial", 10, "bold"), bg="#f5f5f5").pack(anchor="n", pady=(0, 5))  # Etiqueta de título
            inner = tk.Frame(frame, bg="#ffffff")  # Marco interno para partidos
            inner.pack(fill="y")  # Lo empaqueta para ocupar espacio
            for match in matches_in_round:  # Itera sobre partidos de la ronda actual
                p1 = participants.get(match["player1_id"], "") or match.get("player1_placeholder_text", "?")  # Nombre jugador 1 o placeholder
                p2 = participants.get(match["player2_id"], "") or match.get("player2_placeholder_text", "?")  # Nombre jugador 2 o placeholder
                scores_csv = match.get("scores_csv", "")  # Obtiene puntaje guardado si existe
                # Estilizar partido según estado
                if match["state"] == "complete" and scores_csv:  # Si partido terminado y tiene resultados
                    match_str = f"{p1} ({scores_csv}) {p2}"  # Texto con resultado
                    label = tk.Label(inner, text=match_str, font=("Arial black", 10), bg="#f5f5f5", fg="#808080")  # Estilo gris claro
                elif p1 == "?" or p2 == "?":  # Si algún jugador es desconocido
                    match_str = f"{p1} vs {p2}"  # Texto genérico
                    label = tk.Label(inner, text=match_str, font=("Arial black", 10), bg="#f5f5f5", fg="#aaaaaa")  # Estilo gris claro
                else:  # Partido válido y completo
                    match_str = f"{p1} vs {p2}"  # Texto normal
                    label = tk.Label(inner, text=match_str, font=("Arial black", 10), bg="#f5f5f5", fg="#2ecc71")  # Verde para partido activo
                label.pack(pady=1)  # Coloca etiqueta en pantalla
                label.bind("<Button-1>", lambda e, m=match: self.on_click_match(m, participants, label, is_losers))  # Vincula evento click

    # Actualizar scroll region después de dibujar todo
    def update_scroll_region(self, container=None):
        canvas = container.master  # Obtiene lienzo padre del contenedor
        canvas.configure(scrollregion=canvas.bbox("all"))  # Ajusta región desplazable a todo el contenido
        container.update_idletasks()  # Asegura que el contenedor esté actualizado
        self.root.after(100, self.update_scroll_region)  # Programa próxima actualización cada 100ms

    def get_round_description(self, round_num, total_participants):
        # Para partidos del Losers Bracket
        if round_num < 0:  # Ronda negativa → Losers Bracket
            abs_rnd = abs(round_num)  # Toma valor absoluto
            try:
                # Obtenemos todas las rondas negativas (del Losers)
                losers_rounds = set()  # Conjunto para evitar duplicados
                for match in challonge.matches.index(self.current_tournament_id):  # Recorre todos los partidos
                    if match["round"] < 0:  # Solo rondas del Losers
                        losers_rounds.add(abs(match["round"]))  # Añade ronda al conjunto
                # Si esta ronda es la última del Losers → mostrar "Losers Final"
                if losers_rounds and abs_rnd == max(losers_rounds):  # Comprueba si es la última
                    return "Losers Final"  # Devuelve texto especial
                else:  # Otra ronda del Losers
                    return f"Loser Round {abs_rnd}"  # Devuelve texto general
            except Exception as e:  # En caso de error
                print("Error al obtener rondas del Losers:", e)  # Muestra mensaje en consola
                return f"Loser Round {abs_rnd}"  # Devuelve valor por defecto
        # Para partidos del Winners Bracket
        try:
            # Cargar participantes desde API para calcular rondas antes de semifinales
            participants = challonge.participants.index(self.current_tournament_id)  # Obtiene lista real de jugadores
            total_players = len(participants)  # Cuenta cuántos jugadores hay
        except Exception as e:  # En caso de error
            # Usar total_participants como respaldo
            total_players = total_participants or 8  # Fallback a 8 jugadores
        # Calcular cuántas rondas hay antes de semifinales
        rounds_before_finals = int(math.log2(total_players)) if total_players > 0 else 3  # Número de rondas hasta semifinales
        # Devolver descripción según posición en ronda
        if round_num == rounds_before_finals:  # Semifinales
            return "Semifinales"  # Devuelve texto
        elif round_num == rounds_before_finals + 1:  # Final
            return "Final"  # Devuelve texto
        elif round_num == rounds_before_finals + 2:  # Gran final
            return "Grand Final"  # Devuelve texto
        else:  # Otra ronda normal
            return f"Ronda {round_num}"  # Devuelve texto general

    def on_click_match(self, match, participants, label, is_losers=False):
        p1_id = match["player1_id"]  # ID del jugador 1
        p2_id = match["player2_id"]  # ID del jugador 2
        try:
            tournament_id = self.current_tournament_id  # Obtiene ID del torneo actual
            p1 = challonge.participants.show(tournament_id, p1_id)  # Obtiene datos del jugador 1
            p2 = challonge.participants.show(tournament_id, p2_id)  # Obtiene datos del jugador 2
        except Exception as e:  # En caso de error al cargar jugadores
            print("Error al cargar jugadores desde Challonge:", e)  # Muestra mensaje en consola
            return  # Sale del método
        if p1["name"] == "?" or p2["name"] == "?":  # Si falta nombre de algún jugador
            messagebox.showinfo("Partido incompleto", texts["incomplete_match"])  # Muestra advertencia
            return  # Sale del método
        # Obtener estado del partido desde Challonge
        try:
            match_data = challonge.matches.show(tournament_id, match["id"])  # Obtiene detalles del partido
            match_state = match_data["state"]  # Extrae estado del partido
        except Exception as e:  # En caso de error
            print("Error al obtener estado del partido:", e)  # Muestra mensaje en consola
            match_state = "open"  # Asume partido abierto como valor seguro
        # Si partido cerrado → pregunta si continuar sin reiniciar
        if match_state == "complete":  # Si partido ya está cerrado
            response = messagebox.askyesno(  # Pregunta confirmación
                "Advertencia",
                "Este partido ya está finalizado.\nModificarlo podría alterar demasiado el bracket.\n¿Deseas continuar?"
            )
            if not response:  # Si usuario cancela
                return  # Sale del método
        # Guardar datos del partido cargado
        self.loaded_match = {  # Almacena datos del partido actual
            "tournament_id": self.current_tournament_id,  # ID del torneo
            "match_id": match["id"],  # ID del partido
            "player1_id": p1_id,  # ID del jugador 1
            "player2_id": p2_id,  # ID del jugador 2
            "player1": p1,  # Datos del jugador 1
            "player2": p2,  # Datos del jugador 2
            "state": match_state,  # Estado actual del partido
            "old_winner_id": match.get("winner_id")  # ID del ganador anterior
        }
        # Actualizar nombres en pantalla
        self.canvas.itemconfig(self.player1_name, text=p1["name"])  # Cambia texto del jugador 1
        self.canvas.itemconfig(self.player2_name, text=p2["name"])  # Cambia texto del jugador 2
        # Cargar puntaje desde Challonge si está cerrado
        if match_state == "complete" and match_data.get("scores_csv"):  # Si partido cerrado y tiene puntaje
            scores = match_data["scores_csv"].split("-")  # Divide puntajes por "-"
            self.score1.set(int(scores[0]))  # Asigna puntaje jugador 1
            self.score2.set(int(scores[1]))  # Asigna puntaje jugador 2
            self.update_score_display()  # Actualiza visualización del puntaje
        else:  # Si partido está abierto
            if self.mode_button["text"] == "Modo FightCade":  # Si está en modo FightCade
                score1, score2 = self.read_scores_from_files()  # Lee puntajes desde archivos
                if score1 is not None and score2 is not None:  # Si se pudieron leer
                    self.score1.set(score1)  # Asigna puntaje 1
                    self.score2.set(score2)  # Asigna puntaje 2
                    self.update_score_display()  # Actualiza visualización
                else:  # Si hubo error leyendo archivos
                    self.score1.set(0)  # Reinicia puntaje 1
                    self.score2.set(0)  # Reinicia puntaje 2
                    self.update_score_display()  # Actualiza visualización
            else:  # Si no está en modo FightCade
                self.score1.set(0)  # Reinicia puntaje 1
                self.score2.set(0)  # Reinicia puntaje 2
                self.update_score_display()  # Actualiza visualización
        # Resaltar partido seleccionado
        container = self.winners_container if not is_losers else self.losers_container  # Selecciona contenedor adecuado
        for child in container.winfo_children():  # Itera sobre hijos del contenedor
            for w in child.winfo_children():  # Itera sobre elementos internos
                if isinstance(w, tk.Label):  # Si es una etiqueta
                    w.config(bg="#f5f5f5")  # Restablece color fondo
        label.config(bg="#f1c40f")  # Marca partido seleccionado con color amarillo
        # Mostrar notificación de partido en curso
        self.show_notification("Match en curso...", permanent=True)  # Muestra mensaje permanente
        # Habilitar/deshabilitar botones según estado
        if match_state == "open":  # Si partido abierto
            if hasattr(self, "button_submit"):  # Si existe botón submit
                self.button_submit.config(state="normal")  # Habilítalo
            if hasattr(self, "button_reopen"):  # Si existe botón reopen
                self.button_reopen.config(state="disabled")  # Deshabilítalo
        else:  # Si partido cerrado
            if hasattr(self, "button_submit"):  # Si existe botón submit
                self.button_submit.config(state="disabled")  # Deshabilítalo
            if hasattr(self, "button_reopen"):  # Si existe botón reopen
                self.button_reopen.config(state="normal")  # Habilítalo
        self.update_next_match_combobox()  # Actualiza combobox de próximo partido
        self.update_match_combobox()  # Actualiza combobox de partidos
        # Vaciar archivo next_match.txt si tiene contenido
        selected_dir = self.directory_var.get()  # Obtiene directorio actual
        if selected_dir:  # Si hay directorio definido
            next_match_path = os.path.join(selected_dir, "next_match.txt")  # Ruta al archivo
            try:
                with open(next_match_path, "w") as f:  # Abre archivo en modo escritura
                    f.write("")  # Escribe cadena vacía
            except Exception as e:  # En caso de error
                print("No se pudo limpiar next_match.txt", e)  # Muestra mensaje en consola
        # Reiniciar modo automático para próximo partido
        self.auto_update_enabled = True  # Activa modo automático
        if hasattr(self, "button_submit"):  # Si existe botón submit
            self.button_submit.config(state="disabled")  # Deshabilítalo inicialmente
        # Iniciar autolectura periódica cada segundo
        if self._auto_check_id:  # Si ya hay un temporizador activo
            self.root.after_cancel(self._auto_check_id)  # Cancela el anterior
        self._auto_check_id = self.root.after(1000, self.check_score_auto_update)  # Programa nueva revisión
        
    def add_point_player1(self):
        if not self.auto_update_enabled:  # Si la autolectura ya está desactivada (modo manual)
            current = self.score1.get()  # Obtiene el valor actual del puntaje del jugador 1
            self.score1.set(current + 1)  # Incrementa en 1 el puntaje
            self.update_score_display()  # Actualiza la visualización del puntaje en pantalla
            score1 = self.score1.get()  # Vuelve a obtener el nuevo valor del puntaje
            score2 = self.score2.get()  # Obtiene el puntaje del jugador 2 para comparación
            self.check_auto_submit_result(score1, score2)  # Verifica si se debe enviar automáticamente
            return  # Sale del método tras incrementar

        # Si la autolectura está activa (modo automático), pregunta antes de cambiar manualmente
        response = messagebox.askyesno(  # Muestra advertencia al usuario
            "Advertencia",  # Título del mensaje
            "Modificar los puntajes manualmente desactivará la lectura automática de FightCade.\n"  # Mensaje informativo
            "¿Deseas continuar?"  # Pregunta confirmación
        )
        if not response:  # Si el usuario selecciona "No"
            return  # Sale del método sin hacer cambios

        # Desactivar autolectura y habilitar botón de submit
        self.auto_update_enabled = False  # Desactiva la autolectura
        if hasattr(self, "button_submit"):  # Si el botón de submit existe
            self.button_submit.config(state="normal")  # Lo habilita para uso

        current = self.score1.get()  # Obtiene el valor actual del puntaje
        self.score1.set(current + 1)  # Incrementa en 1 el puntaje
        self.update_score_display()  # Actualiza la visualización del puntaje en pantalla
        score1 = self.score1.get()  # Vuelve a obtener el nuevo valor del puntaje
        score2 = self.score2.get()  # Obtiene el puntaje del jugador 2 para comparación
        self.check_auto_submit_result(score1, score2)  # Verifica si se debe enviar automáticamente


    def minus_point_player1(self):
        if not self.auto_update_enabled:  # Si la autolectura ya está desactivada (modo manual)
            current = self.score1.get()  # Obtiene el valor actual del puntaje
            if current > 0:  # Solo permite decrementar si es mayor a 0
                self.score1.set(current - 1)  # Decrementa en 1 el puntaje
                self.update_score_display()  # Actualiza la visualización del puntaje en pantalla
                score1 = self.score1.get()  # Vuelve a obtener el nuevo valor del puntaje
                score2 = self.score2.get()  # Obtiene el puntaje del jugador 2 para comparación
                self.check_auto_submit_result(score1, score2)  # Verifica si se debe enviar automáticamente
            return  # Sale del método tras decrementar

        # Si la autolectura está activa (modo automático), pregunta antes de cambiar manualmente
        response = messagebox.askyesno(  # Muestra advertencia al usuario
            "Advertencia",  # Título del mensaje
            "Modificar los puntajes manualmente desactivará la lectura automática de FightCade.\n"  # Mensaje informativo
            "¿Deseas continuar?"  # Pregunta confirmación
        )
        if not response:  # Si el usuario selecciona "No"
            return  # Sale del método sin hacer cambios

        # Desactivar autolectura y habilitar botón de submit
        self.auto_update_enabled = False  # Desactiva la autolectura
        if hasattr(self, "button_submit"):  # Si el botón de submit existe
            self.button_submit.config(state="normal")  # Lo habilita para uso

        current = self.score1.get()  # Obtiene el valor actual del puntaje
        if current > 0:  # Solo permite decrementar si es mayor a 0
            self.score1.set(current - 1)  # Decrementa en 1 el puntaje
            self.update_score_display()  # Actualiza la visualización del puntaje en pantalla
            score1 = self.score1.get()  # Vuelve a obtener el nuevo valor del puntaje
            score2 = self.score2.get()  # Obtiene el puntaje del jugador 2 para comparación
            self.check_auto_submit_result(score1, score2)  # Verifica si se debe enviar automáticamente


    def add_point_player2(self):
        if not self.auto_update_enabled:  # Si la autolectura ya está desactivada (modo manual)
            current = self.score2.get()  # Obtiene el valor actual del puntaje del jugador 2
            self.score2.set(current + 1)  # Incrementa en 1 el puntaje
            self.update_score_display()  # Actualiza la visualización del puntaje en pantalla
            score1 = self.score1.get()  # Obtiene el puntaje del jugador 1 para comparación
            score2 = self.score2.get()  # Vuelve a obtener el nuevo valor del puntaje
            self.check_auto_submit_result(score1, score2)  # Verifica si se debe enviar automáticamente
            return  # Sale del método tras incrementar

        # Si la autolectura está activa (modo automático), pregunta antes de cambiar manualmente
        response = messagebox.askyesno(  # Muestra advertencia al usuario
            "Advertencia",  # Título del mensaje
            "Modificar los puntajes manualmente desactivará la lectura automática de FightCade.\n"  # Mensaje informativo
            "¿Deseas continuar?"  # Pregunta confirmación
        )
        if not response:  # Si el usuario selecciona "No"
            return  # Sale del método sin hacer cambios

        # Desactivar autolectura y habilitar botón de submit
        self.auto_update_enabled = False  # Desactiva la autolectura
        if hasattr(self, "button_submit"):  # Si el botón de submit existe
            self.button_submit.config(state="normal")  # Lo habilita para uso

        current = self.score2.get()  # Obtiene el valor actual del puntaje
        self.score2.set(current + 1)  # Incrementa en 1 el puntaje
        self.update_score_display()  # Actualiza la visualización del puntaje en pantalla
        score1 = self.score1.get()  # Obtiene el puntaje del jugador 1 para comparación
        score2 = self.score2.get()  # Vuelve a obtener el nuevo valor del puntaje
        self.check_auto_submit_result(score1, score2)  # Verifica si se debe enviar automáticamente


    def minus_point_player2(self):
        if not self.auto_update_enabled:  # Si la autolectura ya está desactivada (modo manual)
            current = self.score2.get()  # Obtiene el valor actual del puntaje
            if current > 0:  # Solo permite decrementar si es mayor a 0
                self.score2.set(current - 1)  # Decrementa en 1 el puntaje
                self.update_score_display()  # Actualiza la visualización del puntaje en pantalla
                score1 = self.score1.get()  # Obtiene el puntaje del jugador 1 para comparación
                score2 = self.score2.get()  # Vuelve a obtener el nuevo valor del puntaje
                self.check_auto_submit_result(score1, score2)  # Verifica si se debe enviar automáticamente
            return  # Sale del método tras decrementar

        # Si la autolectura está activa (modo automático), pregunta antes de cambiar manualmente
        response = messagebox.askyesno(  # Muestra advertencia al usuario
            "Advertencia",  # Título del mensaje
            "Modificar los puntajes manualmente desactivará la lectura automática de FightCade.\n"  # Mensaje informativo
            "¿Deseas continuar?"  # Pregunta confirmación
        )
        if not response:  # Si el usuario selecciona "No"
            return  # Sale del método sin hacer cambios

        # Desactivar autolectura y habilitar botón de submit
        self.auto_update_enabled = False  # Desactiva la autolectura
        if hasattr(self, "button_submit"):  # Si el botón de submit existe
            self.button_submit.config(state="normal")  # Lo habilita para uso

        current = self.score2.get()  # Obtiene el valor actual del puntaje
        if current > 0:  # Solo permite decrementar si es mayor a 0
            self.score2.set(current - 1)  # Decrementa en 1 el puntaje
            self.update_score_display()  # Actualiza la visualización del puntaje en pantalla
            score1 = self.score1.get()  # Obtiene el puntaje del jugador 1 para comparación
            score2 = self.score2.get()  # Vuelve a obtener el nuevo valor del puntaje
            self.check_auto_submit_result(score1, score2)  # Verifica si se debe enviar automáticamente
            
    def toggle_manual_mode_warning(self):
        if not self.auto_update_enabled:  # Si ya está en modo manual (autolectura desactivada)
            return  # Sale del método

        response = messagebox.askyesno(  # Muestra advertencia al usuario
            "Advertencia",  # Título del mensaje
            "Modificar los puntajes manualmente desactivará la lectura automática de FightCade.\n"  # Mensaje informativo
            "Deberás usar 'Upload Results' para enviar los resultados."  # Segunda parte del mensaje
        )
        if response:  # Si el usuario selecciona "Sí"
            self.auto_update_enabled = True  # Activa el modo manual (sí, aunque suene raro, es así en este contexto)
            if hasattr(self, "button_submit"):  # Si el botón de submit existe
                self.button_submit.config(state="normal")  # Lo habilita para uso
        else:  # Si el usuario selecciona "No"
            # Restaurar valores anteriores
            score1, score2 = self.read_scores_from_files()  # Lee puntajes desde archivos
            if score1 is not None and score2 is not None:  # Si se pudieron leer correctamente
                self.score1.set(score1)  # Restablece el puntaje del jugador 1
                self.score2.set(score2)  # Restablece el puntaje del jugador 2
                self.update_score_display()  # Actualiza visualización del puntaje en pantalla


    def submit_result(self, auto=False, force_winner=None):
        if not self.loaded_match:  # Si no hay partido cargado
            messagebox.showwarning("Advertencia", texts["no_match"])  # Muestra mensaje de error
            return  # Sale del método

        tournament_id = self.loaded_match["tournament_id"]  # Obtiene ID del torneo actual
        match_id = self.loaded_match["match_id"]  # Obtiene ID del partido actual
        p1 = self.loaded_match["player1"]  # Obtiene datos del jugador 1
        p2 = self.loaded_match["player2"]  # Obtiene datos del jugador 2

        score1 = self.score1.get()  # Obtiene puntaje actual del jugador 1
        score2 = self.score2.get()  # Obtiene puntaje actual del jugador 2

        if auto and force_winner:  # Si es llamada automática y con ganador forzado
            winner = p1["id"] if force_winner == "p1" else p2["id"]  # Asigna ganador según parámetro
        else:
            if score1 == score2:  # Si hay empate
                messagebox.showerror("Error", texts["tie_error"])  # Muestra mensaje de error
                return  # Sale del método
            winner = p1["id"] if score1 > score2 else p2["id"]  # Determina ganador por puntaje

        try:
            challonge.matches.update(  # Intenta actualizar partido en Challonge
                tournament_id,  # ID del torneo
                match_id,  # ID del partido
                scores_csv=f"{score1}-{score2}",  # Formato CSV de puntajes
                winner_id=winner,  # ID del ganador
                state="complete"  # Cierra el partido tras actualizar
            )

            # Resetear puntajes en pantalla
            self.score1.set(0)  # Reinicia puntaje del jugador 1
            self.score2.set(0)  # Reinicia puntaje del jugador 2
            self.canvas.itemconfig(self.score1_label, text="0")  # Limpia visualización del puntaje 1
            self.canvas.itemconfig(self.score2_label, text="0")  # Limpia visualización del puntaje 2

            # Resetear archivos p1score.txt y p2score.txt si es necesario
            selected_dir = self.directory_var.get()  # Obtiene directorio actual
            if selected_dir:  # Si hay directorio definido
                p1_path = os.path.join(selected_dir, "p1score.txt")  # Ruta al archivo de puntaje jugador 1
                p2_path = os.path.join(selected_dir, "p2score.txt")  # Ruta al archivo de puntaje jugador 2
                try:
                    with open(p1_path, "w") as f:  # Abre archivo de p1 en modo escritura
                        f.write("0")  # Escribe valor 0
                    with open(p2_path, "w") as f:  # Abre archivo de p2 en modo escritura
                        f.write("0")  # Escribe valor 0
                except Exception as e:  # En caso de error al escribir
                    print("No se pudieron resetear los archivos.", e)  # Muestra mensaje de error

            # Mostrar notificación y refrescar bracket
            self.show_notification(texts["result_uploaded"], duration=2000)  # Muestra mensaje de éxito
            self.notification_label.config(text="")  # Limpia texto de notificación
            self.draw_bracket()  # Vuelve a dibujar el bracket

            # ← Actualizar partidos
            self.load_matches()  # Recarga lista de partidos del torneo
            self.update_match_combobox()  # Actualiza combobox de partidos
            self.draw_bracket()  # Dibuja nuevamente el bracket

            # Reiniciar la interfaz para seleccionar un nuevo partido
            self.show_notification("Elija Partido!", duration=3000)  # Pide elegir un partido

            # Reiniciar nombres visuales a valores por defecto
            self.canvas.itemconfig(self.player1_name, text="Nick Player1")  # Resetea nombre jugador 1
            self.canvas.itemconfig(self.player2_name, text="Nick Player2")  # Resetea nombre jugador 2

            # Reiniciar puntajes visuales a "00"
            self.score1.set(0)  # Reinicia puntaje jugador 1
            self.score2.set(0)  # Reinicia puntaje jugador 2
            self.update_score_display()  # Actualiza visualización

            # Limpiar next_match (interfaz y archivo)
            self.combobox_next_match.set("")  # Limpia selección en combobox
            self.combobox_next_match["values"] = []  # Vacía lista de valores

            # Vaciar archivo next_match.txt
            if selected_dir:  # Si hay directorio definido
                next_match_path = os.path.join(selected_dir, "next_match.txt")  # Ruta al archivo
                try:
                    with open(next_match_path, "w") as f:  # Abre archivo en modo escritura
                        f.write("")  # Escribe cadena vacía
                except Exception as e:  # En caso de error
                    print("No se pudo limpiar next_match.txt", e)  # Muestra mensaje de error

            # Limpiar selección del combobox_match
            self.combobox_match.set("")  # Limpia selección del partido

            # Deshabilitar botones tras subir resultado
            if hasattr(self, "button_submit"):  # Si existe el botón de submit
                self.button_submit.config(state="disabled")  # Lo deshabilita

            # Reiniciar modo automático para próximo partido
            self.auto_update_enabled = True  # Reactiva autolectura para siguiente partido

        except Exception as e:  # Captura cualquier excepción durante actualización
            messagebox.showerror("Error", f"{texts['error_updating']}\n{str(e)}")  # Muestra mensaje de error

    def load_selected_match(self, event=None):
        match_index = self.combobox_match.current()  # Obtiene índice del partido seleccionado en combobox
        if match_index == -1:  # Si no hay selección válida
            return  # Sale del método
        match = self.matches_data[match_index]  # Obtiene datos del partido desde lista interna
        tournament_index = self.combobox_tournament.current()  # Obtiene índice del torneo seleccionado
        if tournament_index == -1:  # Si no hay selección válida
            return  # Sale del método
        tournament = self.tournaments_list[tournament_index]  # Obtiene datos del torneo seleccionado
        tournament_id = tournament["id"]  # Extrae ID del torneo
        self.current_tournament_id = tournament_id  # Almacena ID actualmente seleccionado

        try:
            p1 = challonge.participants.show(tournament_id, match["player1_id"])  # Obtiene datos jugador 1
            p2 = challonge.participants.show(tournament_id, match["player2_id"])  # Obtiene datos jugador 2
            # Cargar estado del partido desde Challonge
            match_data = challonge.matches.show(tournament_id, match["id"])  # Consulta estado actual del partido
            match_state = match_data["state"]  # Guarda estado del partido (abierto/cerrado)
            # Actualizar nombres en pantalla
            self.canvas.itemconfig(self.player1_name, text=p1["name"])  # Cambia texto del jugador 1
            self.canvas.itemconfig(self.player2_name, text=p2["name"])  # Cambia texto del jugador 2
            # Reiniciar archivos p1score.txt y p2score.txt a "0"
            selected_dir = self.directory_var.get()  # Obtiene directorio actual
            if selected_dir:  # Si hay directorio definido
                p1_path = os.path.join(selected_dir, "p1score.txt")  # Ruta al archivo de puntaje jugador 1
                p2_path = os.path.join(selected_dir, "p2score.txt")  # Ruta al archivo de puntaje jugador 2
                try:
                    with open(p1_path, "w") as f:  # Abre archivo de p1 en modo escritura
                        f.write("0")  # Escribe valor "0" para reiniciar
                    with open(p2_path, "w") as f:  # Abre archivo de p2 en modo escritura
                        f.write("0")  # Escribe valor "0" para reiniciar
                    self.score1.set(0)  # Reinicia variable interna de puntaje jugador 1
                    self.score2.set(0)  # Reinicia variable interna de puntaje jugador 2
                    self.update_score_display()  # Actualiza visualización del puntaje
                except Exception as e:  # En caso de error al escribir archivos
                    print("No se pudieron resetear los archivos.", e)  # Muestra mensaje de error

            # Guardar datos del partido cargado
            self.loaded_match = {  # Almacena datos del partido actual
                "tournament_id": tournament_id,  # ID del torneo
                "match_id": match["id"],  # ID del partido
                "player1": p1,  # Datos del jugador 1
                "player2": p2,  # Datos del jugador 2
                "old_winner_id": match.get("winner_id"),  # ID del ganador anterior
                "state": match_state  # Estado actual del partido
            }

            # Mostrar notificación y habilitar botones
            if match_state == "open":  # Si partido está abierto
                self.show_notification("Match en curso...", permanent=True)  # Muestra notificación permanente
                if hasattr(self, "button_submit"):  # Si existe botón de subir resultados
                    self.button_submit.config(state="normal")  # Lo habilita
                if hasattr(self, "button_reopen"):  # Si existe botón de reabrir
                    self.button_reopen.config(state="disabled")  # Lo deshabilita
            else:  # Si partido está cerrado
                self.show_notification("", permanent=True)  # Limpia notificación
                if hasattr(self, "button_submit"):  # Si existe botón de subir resultados
                    self.button_submit.config(state="disabled")  # Lo deshabilita
                if hasattr(self, "button_reopen"):  # Si existe botón de reabrir
                    self.button_reopen.config(state="normal")  # Lo habilita

            self.update_next_match_combobox()  # Actualiza combobox de próximo partido
            self.update_match_combobox()  # Actualiza combobox de partidos

            # Vaciar archivo next_match.txt si tiene contenido
            if selected_dir:  # Si hay directorio definido
                next_match_path = os.path.join(selected_dir, "next_match.txt")  # Ruta al archivo
                try:
                    with open(next_match_path, "w") as f:  # Abre archivo en modo escritura
                        f.write("")  # Escribe cadena vacía
                except Exception as e:  # En caso de error
                    print("No se pudo limpiar next_match.txt", e)  # Muestra mensaje de error

            # Reiniciar modo automático para próximo partido
            self.auto_update_enabled = True  # Activa autolectura nuevamente
            if hasattr(self, "button_submit"):  # Si existe botón de submit
                self.button_submit.config(state="disabled")  # Lo deshabilita inicialmente

            # Iniciar autolectura periódica cada segundo
            if self._auto_check_id:  # Si ya hay temporizador activo
                self.root.after_cancel(self._auto_check_id)  # Cancela el previo
            self._auto_check_id = self.root.after(1000, self.check_score_auto_update)  # Programa nueva revisión

        except Exception as e:  # Captura cualquier excepción durante proceso
            messagebox.showerror("Error", f"No se pudo cargar el match.\n{str(e)}")  # Muestra mensaje de error


    def is_valid_fightcade_root(self, path):
        """Verifica que el directorio tenga la estructura correcta: \emulator\fbneo\fightcade\ """
        path_parts = os.path.normpath(path).split(os.sep)  # Divide ruta en partes usando separador del sistema

        # Verificar estructura de carpetas
        if len(path_parts) < 3:  # Si la ruta es demasiado corta
            return False  # No cumple con la estructura mínima

        if path_parts[-1].lower() != "fightcade":  # Última carpeta debe ser "fightcade"
            return False  # No coincide
        if path_parts[-2].lower() != "fbneo":  # Penúltima carpeta debe ser "fbneo"
            return False  # No coincide
        if path_parts[-3].lower() != "emulator":  # Antepenúltima carpeta debe ser "emulator"
            return False  # No coincide

        # Verificar que existan los archivos de puntaje
        p1_path = os.path.join(path, "p1score.txt")  # Ruta al archivo de puntaje jugador 1
        p2_path = os.path.join(path, "p2score.txt")  # Ruta al archivo de puntaje jugador 2
        if not (os.path.exists(p1_path) and os.path.exists(p2_path)):  # Comprueba existencia de ambos
            return False  # Archivos faltantes

        return True  # Todas las verificaciones pasaron


    def browse_directory(self):
        selected_dir = filedialog.askdirectory()  # Abre diálogo para elegir directorio
        if not selected_dir:  # Si usuario cancela o no selecciona nada
            return  # Sale del método

        p1_path = os.path.join(selected_dir, "p1score.txt")  # Ruta al archivo de p1
        p2_path = os.path.join(selected_dir, "p2score.txt")  # Ruta al archivo de p2

        # Verificar estructura del directorio
        if not self.is_valid_fightcade_root(selected_dir):  # Si no tiene estructura válida
            messagebox.showwarning(  # Muestra advertencia
                "Directorio incorrecto",  # Título del mensaje
                "Debe seleccionar el directorio raíz de FightCade:\n"  # Mensaje informativo
                "Ejemplo: \\emulator\\fbneo\\fightcade\\"  # Ejemplo de ruta correcta
            )
            return  # Sale del método si no pasa validación

        # Verificar que existan los archivos p1score.txt y p2score.txt
        if not (os.path.exists(p1_path) and os.path.exists(p2_path)):  # Si falta alguno de los archivos
            messagebox.showwarning(  # Muestra advertencia
                "Archivos faltantes",  # Título del mensaje
                "No se encontraron los archivos p1score.txt y/o p2score.txt.\n\n"  # Indica archivos faltantes
                "Asegúrate de haber seleccionado correctamente la carpeta 'fightcade'.\n"  # Ayuda
                "La ruta debe terminar en: \\emulator\\fbneo\\fightcade\\"  # Ejemplo válido
            )
            return  # Sale del método si faltan archivos

        # Guardar directorio si pasa todas las validaciones
        self.directory_var.set(selected_dir)  # Establece directorio seleccionado
        self.entry_dir.delete(0, tk.END)  # Limpia campo de texto
        self.entry_dir.insert(0, selected_dir)  # Inserta nuevo directorio en campo

        # Desactivar edición manual del directorio
        self.entry_dir.config(state="readonly")  # Hace campo solo lectura

        # Intentar guardar directorio en disco
        try:
            with open(FC_DIRECTORY_FILE, "w") as f:  # Abre archivo local en modo escritura
                f.write(selected_dir)  # Escribe directorio seleccionado
        except Exception as e:  # En caso de error al guardar
            print("Error al guardar directorio:", e)  # Muestra mensaje en consola
            self.entry_dir.config(state="normal")  # Permite edición manual
            messagebox.showerror(  # Muestra mensaje de error
                "Error",  # Título del mensaje
                "No se pudo guardar el directorio seleccionado.\n"  # Información del error
                "Puedes continuar usando la aplicación, pero esta carpeta no se recordará después de cerrarla."  # Consejo
            )

        try:
            score1, score2 = self.read_scores_from_files()  # Lee puntajes desde archivos
            if score1 is not None and score2 is not None:  # Si se pudieron leer
                self.score1.set(score1)  # Asigna puntaje jugador 1
                self.score2.set(score2)  # Asigna puntaje jugador 2
                self.update_score_display()  # Actualiza visualización del puntaje
        except Exception as e:  # En caso de error al leer
            print("No se pudieron cargar los puntajes iniciales", e)  # Muestra mensaje en consola

    def toggle_mode_text(self):
        current = self.mode_button["text"]  # Obtiene texto actual del botón
        if current == "Modo FightCade":  # Si está en modo FightCade
            # Cambiar a Modo Challonge
            self.mode_button.config(text="Modo Challonge")  # Actualiza texto del botón
            self.entry_dir.config(state="disabled")  # Deshabilita campo de directorio
            self.button_browse.config(state="disabled")  # Deshabilita botón de búsqueda
        else:  # Si está en modo Challonge
            # Cambiar a Modo FightCade
            self.mode_button.config(text="Modo FightCade")  # Actualiza texto del botón
            self.button_browse.config(state="normal")  # Habilita botón de búsqueda

            # Recuperar directorio desde archivo si existe
            if not self.directory_var.get() and os.path.exists(FC_DIRECTORY_FILE):  # Si no hay directorio actual y existe uno guardado
                try:
                    with open(FC_DIRECTORY_FILE, "r") as f:  # Abre archivo en modo lectura
                        saved_dir = f.read().strip()  # Lee y limpia espacios
                    if os.path.isdir(saved_dir):  # Si es un directorio válido
                        self.directory_var.set(saved_dir)  # Establece directorio seleccionado
                        self.entry_dir.delete(0, tk.END)  # Limpia campo de texto
                        self.entry_dir.insert(0, saved_dir)  # Inserta directorio en campo
                        self.entry_dir.config(state="disabled")  # Deshabilita edición manual
                    else:
                        self.entry_dir.config(state="normal")  # Habilita edición si ruta inválida
                except Exception as e:  # En caso de error al leer archivo
                    print("Error al cargar directorio guardado:", e)  # Muestra mensaje en consola
                    self.entry_dir.config(state="normal")  # Permite edición manual
            else:
                # Si ya hay directorio, mantenerlo en "readonly"
                if self.directory_var.get():  # Si ya hay un directorio definido
                    self.entry_dir.config(state="readonly")  # Lo mantiene solo lectura
                else:
                    self.entry_dir.config(state="normal")  # Habilita edición manual


    def read_scores_from_files(self):
        if self.mode_button["text"] != "Modo FightCade":  # Si no está en modo FightCade
            return None, None  # No lee puntajes

        selected_dir = self.directory_var.get()  # Obtiene directorio actual
        if not selected_dir:  # Si no hay directorio definido
            return None, None  # No lee puntajes

        p1_path = os.path.join(selected_dir, "p1score.txt")  # Ruta al archivo de p1
        p2_path = os.path.join(selected_dir, "p2score.txt")  # Ruta al archivo de p2

        if not (os.path.exists(p1_path) and os.path.exists(p2_path)):  # Si falta alguno
            return None, None  # No lee puntajes

        try:
            with open(p1_path, "r") as f:  # Abre archivo de p1 en modo lectura
                score1 = int(f.read().strip())  # Lee y convierte a entero
            with open(p2_path, "r") as f:  # Abre archivo de p2 en modo lectura
                score2 = int(f.read().strip())  # Lee y convierte a entero
            return score1, score2  # Devuelve ambos puntajes leídos
        except Exception as e:  # En caso de error al leer archivos
            print("Error al leer puntajes.", e)  # Muestra mensaje de error
            return None, None  # Devuelve valores nulos


    def check_score_auto_update(self):
        if not self.loaded_match or not self.auto_update_enabled or self.mode_button["text"] != "Modo FightCade":  # Si no hay partido o autolectura desactivada o no está en modo FightCade
            self.auto_update_id = self.root.after(1000, self.check_score_auto_update)  # Programa nueva revisión
            return  # Sale del método

        score1, score2 = self.read_scores_from_files()  # Lee puntajes desde archivos

        if score1 is None or score2 is None:  # Si no se pudieron leer
            self.root.after(1000, self.check_score_auto_update)  # Programa nueva revisión
            return  # Sale del método

        # Actualizar solo si hay cambio real
        if self.score1.get() != score1 or self.score2.get() != score2:  # Solo si hay diferencia
            self.score1.set(score1)  # Actualiza variable interna de p1
            self.score2.set(score2)  # Actualiza variable interna de p2
            self.update_score_display()  # Refresca visualización en pantalla
            self.check_auto_submit_result(score1, score2)  # Verifica si debe enviar automáticamente

        # Volver a ejecutar después de 1 segundo
        self.auto_update_id = self.root.after(1000, self.check_score_auto_update)  # Programa próxima revisión


    def reset_scores_files_and_ui(self):
        """Reinicia puntajes visuales y archivos p1score.txt / p2score.txt"""
        # Reiniciar puntajes en interfaz
        self.score1.set(0)  # Reinicia variable interna de p1
        self.score2.set(0)  # Reinicia variable interna de p2
        self.update_score_display()  # Actualiza visualización en pantalla

        # Reiniciar archivos p1score.txt y p2score.txt si están en modo FightCade
        if self.mode_button["text"] == "Modo FightCade":  # Solo si está en modo FightCade
            selected_dir = self.directory_var.get()  # Obtiene directorio actual
            if selected_dir:  # Si hay directorio definido
                p1_path = os.path.join(selected_dir, "p1score.txt")  # Ruta al archivo de p1
                p2_path = os.path.join(selected_dir, "p2score.txt")  # Ruta al archivo de p2
                try:
                    with open(p1_path, "w") as f:  # Abre archivo de p1 en modo escritura
                        f.write("0")  # Escribe valor 0
                    with open(p2_path, "w") as f:  # Abre archivo de p2 en modo escritura
                        f.write("0")  # Escribe valor 0
                except Exception as e:  # En caso de error al escribir
                    print("No se pudieron resetear los archivos.", e)  # Muestra mensaje de error


    def reopen_match(self):
        """Reabre un partido finalizado desde la API de Challonge"""
        if not self.loaded_match:  # Si no hay partido cargado
            print("No hay partido cargado.")  # Muestra mensaje en consola
            return  # Sale del método

        tournament_id = self.loaded_match["tournament_id"]  # Obtiene ID del torneo
        match_id = self.loaded_match["match_id"]  # Obtiene ID del partido

        try:
            # 1. Confirmación del usuario
            response = messagebox.askyesno(  # Pregunta confirmación antes de reabrir
                "Reabrir Partido",  # Título del mensaje
                "¿Estás seguro de que deseas reabrir este partido?"  # Mensaje de confirmación
            )
            if not response:  # Si responde que no
                return  # Sale del método

            # 2. Llamar a la API de Challonge para reabrir el partido
            challonge.matches.reopen(tournament_id, match_id)  # Ejecuta acción en API

            # 3. Actualizar UI
            self.show_notification("Partido Reabierto", duration=2000)  # Muestra notificación temporal
            self.load_selected_match()  # Recarga datos del partido
            self.draw_bracket()  # Dibuja nuevamente el bracket
            self.update_match_combobox()  # Refresca combobox de partidos

            # Reiniciar puntajes y archivos usando el método auxiliar
            self.reset_scores_files_and_ui()  # Llama método que reinicia puntajes

            # Recargar todos los partidos del torneo y actualizar UI
            self.load_matches()  # ← Esto es clave para refrescar datos
            self.update_match_combobox()  # Actualiza lista de partidos

            # 5. Habilitar edición de puntaje
            if hasattr(self, "button_submit"):  # Si existe botón de submit
                self.button_submit.config(state="normal")  # Lo habilita

        except Exception as e:  # Captura cualquier excepción durante proceso
            messagebox.showerror("Error", f"No se pudo reabrir el partido.\n{str(e)}")  # Muestra mensaje de error


    def update_score_display(self):
        score1 = self.score1.get()  # Obtiene puntaje jugador 1
        score2 = self.score2.get()  # Obtiene puntaje jugador 2
        # Actualiza directamente los textos del canvas con formato de dos dígitos
        self.canvas.itemconfig(self.score1_label, text=f"{score1:02d}")  # Formato de 2 dígitos para p1
        self.canvas.itemconfig(self.score2_label, text=f"{score2:02d}")  # Formato de 2 dígitos para p2


    def update_next_match_combobox(self):
        if not self.loaded_match:  # Si no hay partido cargado
            self.combobox_next_match["values"] = []  # Vacía lista de próximo partido
            self.combobox_next_match.set("")  # Limpia selección
            return  # Sale del método

        tournament_id = self.loaded_match["tournament_id"]  # Obtiene ID del torneo actual
        current_p1 = self.canvas.itemcget(self.player1_name, "text")  # Obtiene nombre actual de p1
        current_p2 = self.canvas.itemcget(self.player2_name, "text")  # Obtiene nombre actual de p2

        try:
            matches = challonge.matches.index(tournament_id)  # Obtiene todos los partidos del torneo
            participants = {p["id"]: p["name"] for p in challonge.participants.index(tournament_id)}  # Crea diccionario de jugadores
            future_matches = []  # Lista temporal para partidos futuros

            for match in matches:  # Itera sobre todos los partidos del torneo
                p1 = participants.get(match["player1_id"], "?")  # Obtiene nombre de p1 o ?
                p2 = participants.get(match["player2_id"], "?")  # Obtiene nombre de p2 o ?
                if p1 == "?" or p2 == "?":  # Si algún jugador no está definido
                    continue  # Salta partido incompleto
                match_text = f"{p1} vs {p2}"  # Crea texto para mostrar
                current_text = f"{current_p1} vs {current_p2}"  # Crea texto del partido actual

                # Solo agregar si NO es el partido actual y está abierto
                if match["state"] == "open" and match_text != current_text:  # Filtra partidos abiertos
                    future_matches.append(match_text)  # Añade partido a lista futura

            # Eliminar duplicados y actualizar combobox
            future_matches = list(set(future_matches))  # Elimina partidos repetidos
            self.combobox_next_match["values"] = future_matches  # Asigna lista de próximos partidos
            self.combobox_next_match.set("")  # Limpia selección inicial

        except Exception as e:  # En caso de error durante proceso
            print("Error al actualizar next_match:", e)  # Muestra mensaje de error
            self.combobox_next_match["values"] = []  # Vacía lista de partidos
            self.combobox_next_match.set("")  # Limpia selección
    
    def load_scores_from_files_after_delay(self, p1, p2, match, tournament_id):
        score1, score2 = self.read_scores_from_files()  # Lee puntajes desde archivos
        if score1 is not None and score2 is not None:  # Si se pudieron leer correctamente
            self.score1.set(score1)  # Asigna puntaje jugador 1
            self.score2.set(score2)  # Asigna puntaje jugador 2
            self.update_score_display()  # Actualiza visualización en pantalla
        else:  # Si hubo error leyendo archivos
            self.score1.set(0)  # Reinicia variable interna de p1
            self.score2.set(0)  # Reinicia variable interna de p2
            self.canvas.itemconfig(self.score1_label, text="0")  # Limpia visualización de p1
            self.canvas.itemconfig(self.score2_label, text="0")  # Limpia visualización de p2

        # Guardar datos del partido cargado
        self.loaded_match = {  # Almacena información del partido actual
            "tournament_id": tournament_id,  # ID del torneo
            "match_id": match["id"],  # ID del partido
            "player1": p1,  # Datos del jugador 1
            "player2": p2,  # Datos del jugador 2
            "old_winner_id": match.get("winner_id")  # ID del ganador anterior (si existe)
        }

        # Iniciar autolectura periódica cada segundo
        self.auto_update_id = self.root.after(1000, self.auto_update_scores)  # Programa revisión automática


    def auto_update_scores(self):
        if not self.loaded_match or not self.auto_update_enabled or self.mode_button["text"] != "Modo FightCade":  # Si no hay partido o modo incorrecto
            return  # Sale del método

        score1, score2 = self.read_scores_from_files()  # Lee puntajes desde archivos

        if score1 is None or score2 is None:  # Si no se pudieron leer
            print("No se pudieron leer los puntajes.")  # Muestra mensaje en consola
            self.root.after(1000, self.auto_update_scores)  # Programa nueva revisión
            return  # Sale del método

        # Obtener el FT correcto (Torneo o Final)
        ft_value = self.get_ft_value()  # Obtiene valor FT según tipo de partido

        # Actualizar solo si hay cambio real
        if self.score1.get() != score1 or self.score2.get() != score2:  # Solo si hay diferencia
            self.score1.set(score1)  # Actualiza puntaje jugador 1
            self.score2.set(score2)  # Actualiza puntaje jugador 2
            self.update_score_display()  # Refresca visualización en pantalla
            self.check_auto_submit_result(score1, score2)  # Verifica si debe enviar automáticamente

        # Si se alcanzó el FT, subir resultado automáticamente
        if score1 >= ft_value or score2 >= ft_value:  # Si algún jugador llegó al límite FT
            winner = "p1" if score1 > score2 else "p2"  # Determina ganador por puntaje
            self.submit_result(auto=True, force_winner=winner)  # Envía resultados automáticamente

        # Volver a ejecutar después de 1 segundo
        self.auto_update_id = self.root.after(1000, self.auto_update_scores)  # Programa próxima revisión


    def get_current_ft_value(self):
        # Obtiene el FT actual según ronda
        if not self.loaded_match:  # Si no hay partido cargado
            return None  # Devuelve valor nulo

        round_desc = self.canvas.itemcget(self.round_info_label, "text")  # Obtiene descripción de ronda actual
        is_final = "final" in round_desc.lower()  # Comprueba si es final

        try:
            if is_final:  # Si es partida final
                ft_value = int(self.combo_ft_final.get()[2:])  # Ej: "FT3" → 3
            else:  # Si no es final
                ft_value = int(self.combo_ft_tournament.get()[2:])  # Toma valor FT Torneo
            return ft_value  # Devuelve valor numérico
        except Exception as e:  # En caso de error
            print("Error al leer FT.", e)  # Muestra mensaje en consola
            return None  # Devuelve valor nulo


    def is_special_match(self, match_data):
        """Detecta si el partido actual es uno especial (final de winners, losers o grand final)"""
        try:
            tournament_id = self.current_tournament_id  # Obtiene ID del torneo actual
            matches = challonge.matches.index(tournament_id)  # Obtiene todos los partidos

            # Obtener todos los partidos del Losers Bracket (round < 0)
            losers_matches = [m for m in matches if m["round"] < 0]  # Filtra partidos con ronda negativa
            # Obtener todos los partidos del Winners Bracket (round > 0)
            winners_matches = [m for m in matches if m["round"] > 0]  # Filtra partidos con ronda positiva

            # Último partido del Winners Bracket
            last_winners_match = max(winners_matches, key=lambda m: m["round"], default=None)  # Busca mayor ronda

            # Último partido del Losers Bracket
            last_losers_match = max(losers_matches, key=lambda m: abs(m["round"]), default=None)  # Por valor absoluto

            # Si es final de Winners Bracket
            if last_winners_match and match_data["id"] == last_winners_match["id"]:  # Compara IDs
                return "winners_final"  # Es final de Winners

            # Si es final de Losers Bracket
            elif last_losers_match and match_data["id"] == last_losers_match["id"]:  # Compara IDs
                return "losers_final"  # Es final de Losers

            # Si tiene group_id → probablemente sea Grand Final
            elif match_data.get("group_id") is not None:  # Si existe grupo asociado
                return "grand_final"  # Es gran final

            else:
                return "normal"  # No es partido especial
        except Exception as e:  # En caso de error durante detección
            print("Error al detectar tipo de partido:", e)  # Muestra mensaje en consola
            return "normal"  # Devuelve tipo normal por defecto


    def get_ft_value(self):
        """Devuelve el valor numérico del FT según el tipo de partido"""
        if not self.loaded_match:  # Si no hay partido cargado
            return 3  # Valor predeterminado

        try:
            match_data = challonge.matches.show(self.loaded_match["tournament_id"], self.loaded_match["match_id"])  # Obtiene detalles del partido
            match_type = self.is_special_match(match_data)  # Detecta si es partido especial

            # Usar FT Final para partidos especiales
            if match_type in ["winners_final", "losers_final", "grand_final"]:  # Para partidos finales
                try:
                    ft_value = int(self.combo_ft_final.get()[2:])  # Ej: "FT5" → 5
                    return ft_value  # Devuelve valor FT Final
                except:
                    return 5  # Valor por defecto para finales

            # Para partidos normales, usar FT Torneo
            else:
                try:
                    ft_value = int(self.combo_ft_tournament.get()[2:])  # Ej: "FT3" → 3
                    return ft_value  # Devuelve valor FT Torneo
                except:
                    return 3  # Valor por defecto para torneos
        except Exception as e:  # En caso de error
            print("Error al obtener FT:", e)  # Muestra mensaje en consola
            return 3  # Valor predeterminado


    def check_auto_submit_result(self, score1, score2):
        if self.mode_button["text"] != "Modo FightCade":  # Si no está en modo FightCade
            return  # Sale del método

        # Obtener datos del partido actual
        match_data = challonge.matches.show(self.loaded_match["tournament_id"], self.loaded_match["match_id"])  # Consulta partido actual

        # Detectar si es un partido especial
        match_type = self.is_special_match(match_data)  # Clasifica tipo de partido

        # Seleccionar el FT adecuado según tipo de partido
        if match_type in ["losers_final", "winners_final", "grand_final"]:  # Si es partido especial
            try:
                ft_value = int(self.combo_ft_final.get()[2:])  # Ej: "FT3" → 3
            except:
                ft_value = 3  # Valor por defecto
        else:  # Si es partido normal
            try:
                ft_value = int(self.combo_ft_tournament.get()[2:])  # Toma FT Torneo
            except:
                ft_value = 3  # Valor por defecto

        # Verificar si se alcanzó el FT
        if score1 >= ft_value or score2 >= ft_value:  # Si algún jugador llegó al límite FT
            winner = "p1" if score1 > score2 else "p2"  # Determina ganador
            self.submit_result(auto=True, force_winner=winner)  # Envía resultados automáticamente

            # Reiniciar puntajes visuales a "00"
            self.score1.set(0)  # Reinicia puntaje jugador 1
            self.score2.set(0)  # Reinicia puntaje jugador 2
            self.update_score_display()  # Actualiza visualización en pantalla

            # Mostrar notificación
            self.show_notification("Elija Partido!", permanent=True)  # Pide seleccionar nuevo partido
            
    def on_ft_change(self, event=None):
        """Detecta cambios en FT Torneo/Final y muestra mensajes según estado"""
        ft_tournament = self.combo_ft_tournament.get()  # Obtiene valor actual de FT Torneo
        ft_final = self.combo_ft_final.get()  # Obtiene valor actual de FT Final

        # Validar qué falta
        if not ft_tournament and not ft_final:  # Si ambos están vacíos
            self.show_notification("Asigne FT Torneo y FT Final", duration=3000, permanent=True)  # Muestra mensaje informativo
        elif not ft_tournament:  # Si solo falta FT Torneo
            self.show_notification("Asigne FT Torneo", duration=3000, permanent=True)  # Pide asignar FT Torneo
        elif not ft_final:  # Si solo falta FT Final
            self.show_notification("Asigne FT Final", duration=3000, permanent=True)  # Pide asignar FT Final
        else:  # Si ambos tienen valores
            self.show_notification("Elija Torneo!", duration=3000, permanent=True)  # Indica que debe elegir torneo

        # Habilitar combos solo si ambos FT están llenos
        if ft_tournament and ft_final:  # Si ambos FT tienen valores
            self.combobox_tournament.config(state="readonly")  # Habilita combobox de torneos
            self.combobox_match.config(state="readonly")  # Habilita combobox de partidos
        else:  # Si alguno o ambos están vacíos
            self.combobox_tournament.config(state="disabled")  # Deshabilita combobox de torneos
            self.combobox_match.config(state="disabled")  # Deshabilita combobox de partidos


    def update_match_combobox(self):
        """Actualiza el texto del partido seleccionado en el combobox_match"""
        if not self.loaded_match:  # Si no hay partido cargado
            return  # Sale del método

        p1 = self.canvas.itemcget(self.player1_name, "text")  # Obtiene nombre jugador 1 desde canvas
        p2 = self.canvas.itemcget(self.player2_name, "text")  # Obtiene nombre jugador 2 desde canvas

        match_text = f"{p1} vs {p2}"  # Crea texto para mostrar
        match_index = -1  # Inicializa índice como no encontrado

        for i, value in enumerate(self.combobox_match["values"]):  # Recorre lista de partidos
            if value == match_text:  # Si encuentra coincidencia exacta
                match_index = i  # Guarda posición encontrada
                break  # Sale del bucle

        # Actualizar el valor del combobox_match
        if match_index != -1:  # Si se encontró el partido
            self.combobox_match.current(match_index)  # Establece selección por índice
        else:  # Si no se encontró
            self.combobox_match.set(match_text)  # Establece texto manualmente

        # Asegurar que el combobox_match esté habilitado si hay partido abierto
        if self.loaded_match.get("state") == "open":  # Si partido está abierto
            self.combobox_match.config(state="readonly")  # Solo lectura
        else:  # Si partido está cerrado
            self.combobox_match.config(state="normal")  # Edición permitida


    def on_refresh_bracket(self):
        if not self.current_tournament_id:  # Si no hay torneo actual
            return  # Sale del método

        try:
            matches = challonge.matches.index(self.current_tournament_id)  # Obtiene partidos del torneo
            participants = {p["id"]: p["name"] for p in challonge.participants.index(self.current_tournament_id)}  # Diccionario de jugadores

            winners_by_round = {}  # Diccionario para agrupar partidos por ronda (Winners)
            losers_by_round = {}  # Diccionario para agrupar partidos por ronda (Losers)

            for match in matches:  # Itera sobre todos los partidos del torneo
                rnd = match["round"]  # Obtiene número de ronda
                if rnd > 0:  # Winners Bracket
                    if rnd not in winners_by_round:  # Si es nueva ronda
                        winners_by_round[rnd] = []  # Crea lista vacía
                    winners_by_round[rnd].append(match)  # Añade partido a la ronda correspondiente
                elif rnd < 0:  # Losers Bracket
                    abs_rnd = abs(rnd)  # Toma valor absoluto
                    if abs_rnd not in losers_by_round:  # Si es nueva ronda
                        losers_by_round[abs_rnd] = []  # Crea lista vacía
                    losers_by_round[abs_rnd].append(match)  # Añade partido a la ronda

            # Redibujar partidos
            for widget in self.winners_container.winfo_children():  # Limpia widgets anteriores
                widget.destroy()  # Elimina cada widget hijo
            for widget in self.losers_container.winfo_children():  # Lo mismo para Losers
                widget.destroy()  # Elimina cada widget hijo

            self.display_horizontal_bracket(self.winners_container, winners_by_round, participants, is_losers=False)  # Dibuja bracket ganadores
            self.display_horizontal_bracket(self.losers_container, losers_by_round, participants, is_losers=True)  # Dibuja bracket perdedores

            # Mostrar notificación de actualización
            self.show_notification("Bracket Refresh", duration=2000)  # Notifica refresco del bracket

        except Exception as e:  # Captura cualquier excepción durante proceso
            messagebox.showerror("Error", f"No se pudo refrescar el bracket\n{str(e)}")  # Muestra mensaje de error


    def on_reset_scores_click(self):
        """Reinicia ambos puntajes a 0 con confirmación"""
        if not self.loaded_match:  # Si no hay partido cargado
            messagebox.showwarning("Advertencia", "Debe cargar un partido primero para usar este botón.")  # Muestra advertencia
            return  # Sale del método

        # Asegúrate de que el partido tenga estado actualizado desde API
        try:
            tournament_id = self.loaded_match["tournament_id"]  # Obtiene ID del torneo
            match_id = self.loaded_match["match_id"]  # Obtiene ID del partido
            match_data = challonge.matches.show(tournament_id, match_id)  # Consulta datos actuales
            match_state = match_data["state"]  # Extrae estado del partido
        except Exception as e:  # En caso de error al consultar
            print("Error al obtener estado del partido:", e)  # Muestra mensaje en consola
            match_state = "open"  # Por defecto, asume partido abierto

        # Si el partido está cerrado → pregunta si reiniciar de todas formas
        if match_state == "complete":  # Si partido ya está cerrado
            response = messagebox.askyesno(  # Pregunta confirmación
                "Advertencia",
                "Este partido ya está cerrado. ¿Deseas reiniciar puntajes de todas formas?"
            )
            if not response:  # Si usuario cancela
                return  # Sale del método

        # Confirmación final del usuario
        response = messagebox.askyesno(  # Pregunta confirmación definitiva
            "Confirmar reinicio",
            "¿Estás seguro que deseas reiniciar ambos puntajes a 0?"
        )
        if not response:  # Si usuario cancela
            return  # Sale del método

        # Usar método auxiliar para reiniciar puntajes y archivos
        self.reset_scores_files_and_ui()  # Llama al método que resetea archivos y UI

        # ← Nuevo: reactivar autolectura después del reseteo
        self.auto_update_enabled = True  # Activa nuevamente la autolectura
        if self.auto_update_id is not None:  # Si había un temporizador activo
            try:
                self.root.after_cancel(self.auto_update_id)  # Cancela la acción programada
            except ValueError:  # Si el ID es inválido
                pass  # Ignora el error
            self.auto_update_id = None  # Limpia referencia al temporizador

        # Mostrar notificación y refrescar UI
        self.show_notification("Score Resets OK", duration=2000)  # Muestra mensaje de éxito
        self.draw_bracket()  # Vuelve a dibujar el bracket

        # Actualizar estado del partido localmente a "open"
        self.loaded_match["state"] = "open"  # Marca partido como abierto

        # Forzar actualización visual
        self.update_match_combobox()  # Refresca visualización del partido seleccionado


    def force_combobox_up(self, event):
        try:
            event.widget.tk.eval(f"::ttk::popup {event.widget}")  # Simula apertura del desplegable
        finally:
            return "break"  # Detiene propagación del evento


    def on_next_match_selected(self, event=None):
        selected_match = self.next_match_var.get()  # Obtiene partido seleccionado
        if not selected_match:  # Si no hay selección válida
            return  # Sale del método

        selected_dir = self.directory_var.get()  # Obtiene directorio actual
        if not selected_dir:  # Si no hay directorio definido
            messagebox.showwarning(  # Muestra advertencia
                "Directorio no definido",  # Título del mensaje
                "No se puede guardar 'next_match.txt' sin directorio válido."  # Mensaje informativo
            )
            return  # Sale del método

        next_match_path = os.path.join(selected_dir, "next_match.txt")  # Ruta al archivo next_match.txt
        try:
            with open(next_match_path, "w", encoding="utf-8") as f:  # Abre archivo en modo escritura
                f.write(selected_match)  # Escribe nombre del próximo partido
        except Exception as e:  # En caso de error al escribir
            print("Error al guardar next_match.txt:", e)  # Muestra mensaje en consola
            messagebox.showerror(  # Muestra mensaje de error
                "Error",  # Título del mensaje
                "No se pudo guardar el archivo next_match.txt"  # Contenido del mensaje
            )
            
            
if __name__ == "__main__":
    window = tk.Tk()
    app = ChallongeScoreboardApp(window)
    window.mainloop()
