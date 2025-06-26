
# 🎮 Fightcade2Challonge Control v1.0

- 🛠️ **Controla tus torneos de Challonge desde Fightcade 2**  
 Automatiza resultados con `p1score.txt` y `p2score.txt` (datos de FightCade 2).
 Se vincula automáticamente con Challonge.
 Ideal para streamers y organizadores de Fighting Tournaments.

---
## 💻 Windows Installer Download:
https://nirvanaruns.itch.io/fightcade2challonge-control-v1

---
## 📦 Requisitos del Programa

- 💻 Windows
- 🐍 Python 3.6+
- 📁 Carpeta de FightCade con los archivos:
  - `p1score.txt`
  - `p2score.txt`
- 🔑 API Key de Challonge.
- 📦 Librerías usadas:
  - `challonge`
  - `tkinter`

---
## Clona este repositorio:
git clone https://github.com/Nirvanatistos/Fightcade2Challonge.git

cd Fightcade2Challonge

---
## Instala las dependencias necesarias:
pip install -r requirements.txt

---
## 🔑 ¿Cómo Obtener tu API Key de Challonge?.

Para usar este programa necesitas una **API Key de Challonge**.

### Pasos:
1. Inicia sesión en [Challonge](https://challonge.com) .
2. Ve a → https://challonge.com/settings/developer
3. Baja hasta encontrar la sección **"Developer API Key"**.
4. Haz clic en **"Generate"** si aún no tienes una clave.
5. Cópiala y guárdala en un lugar seguro.

Tu API Key es algo como: `abcdefghijk1234567890`

🔐 No la compartas públicamente.

👉 Puedes regenerarla desde la misma página si crees que fue comprometida.

---

## ✅ Características Principales.

- 🔁 **Modo Automático de FightCade**: Lee los archivos de puntaje y envía automáticamente los resultados a Challonge.
- 🏆 Compara contra "FT" (First To X) → cierra el match automáticamente cuando se alcanza el FT seleccionado.
- 📄 Guardado inteligente del directorio de FightCade → no vuelvas a seleccionarlo cada vez.
- 🖥️ GUI clara y simple → hecha con `tkinter`
- 📂 Se integra perfectamente con:
  - `p1score.txt`
  - `p2score.txt`
  - `"Save overlay data to files"` en Fightcade 2

---

## ⚙️ ¿Cómo funciona el Modo Fightcade?.

1. Abre un torneo de doble eliminación en Challonge.
2. Selecciona cuántas victorias se necesitan para ganar (`FT`) ( Requerido: "FT Torneo" y "FT Final" para Losers Finals, Winners Finals, Grand Final y Grand Final Reset).
3. Selecciona el torneo.
4. Selecciona el match a través de la sección de brackets o desde la listao desplegable "Selec. Match".
5. Elige la carpeta donde están `p1score.txt` y `p2score.txt`. Recuerda tener activada la opción "Save overlay data to files" ubicada en el menú "Video" -> "Fightcade" (para activar esta opción abre cualquier juego de Fightcade en modo "Test Game").
6. Al alcanzar el valor FT, el resultado se subirá automáticamente a Challonge.

---

🎮Links de interés:

Discord: https://discord.gg/7tfRJQbv8M
Software desarrollado por [OSG]~Nirvana - 2025

---
