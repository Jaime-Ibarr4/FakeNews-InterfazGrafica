import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import string
import urllib.parse

# ── Importar lógica del prototipo ──────────────────────────────────────────
try:
    from newspaper import Article, ArticleException
    NEWSPAPER_OK = True
except ImportError:
    NEWSPAPER_OK = False

# ==========================================
# ONTOLOGÍA Y DATOS (igual que prototipo.py)
# ==========================================
ONTOLOGIA = {
    "fuente_oficial":    {"credibilidad": "alta",  "peso": 0},
    "fuente_desconocida":{"credibilidad": "media", "peso": 1},
    "fuente_dudosa":     {"credibilidad": "baja",  "peso": 2},
}

RED_SEMANTICA_SENSACIONALISMO = [
    'mutilaciones','ejecución','ejecutado','decapitado',
    'violencia','hallazgo','cadáver','cuerpos','desaparecen',
    'increíble','urgente','atención','difundir','ocultan',
    'nunca visto','impactante','exclusiva','revelación',
    'gasolinazo','desabasto','quiebra',
]

LUGARES_LOCALES_CHIAPAS = [
    'jiquipilas','tuxtla','chiapas','san cristóbal',
    'tapachula','comitán','ocosingo','palenque',
    'tonalá','arriaga','villaflores','cintalapa',
    'suchiapa','berriozábal','chiapa de corzo',
]

FUENTES_OFICIALES = [
    'diariodechiapas.com','eluniversal.com.mx','gob.mx',
    'fiscalia.gob.mx','bbc.com','elpais.com','reforma.com',
    'animalpolitico.com','proceso.com.mx','excelsior.com.mx',
    'milenio.com','jornada.com.mx','cronica.com.mx', 'nmas.com.mx'
]
FUENTES_DUDOSAS = [
    'facebook.com','whatsapp.com','twitter.com','x.com',
    'costanews.com','codigorojo.com','tiktok.com','instagram.com',
    'youtube.com','t.me','telegram.org',
]

# ==========================================
# LÓGICA DE CLASIFICACIÓN
# ==========================================
def limpiar_texto(texto):
    texto = texto.lower()
    texto = texto.translate(str.maketrans('', '', string.punctuation))
    return texto

def tokenizar(texto):
    return texto.split()

def extraer_dominio(url):
    try:
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc
        return domain.replace('www.', '')
    except Exception:
        return 'desconocida'

def heuristica_sensacionalismo(titulo, cuerpo):
    peso = 0
    titulo_limpio = limpiar_texto(titulo)
    tokens_titulo = set(tokenizar(titulo_limpio))
    for palabra in RED_SEMANTICA_SENSACIONALISMO:
        if palabra in tokens_titulo:
            peso = 1
            break
    mayusculas = sum(1 for c in titulo if c.isupper())
    if len(titulo) > 0 and (mayusculas / len(titulo)) > 0.3:
        peso = 1
    return peso

def heuristica_verificabilidad(fuente):
    fuente_limpia = fuente.lower().strip()
    if any(f in fuente_limpia for f in FUENTES_DUDOSAS):
        return ONTOLOGIA["fuente_dudosa"]["peso"]
    elif any(f in fuente_limpia for f in FUENTES_OFICIALES):
        return ONTOLOGIA["fuente_oficial"]["peso"]
    else:
        return ONTOLOGIA["fuente_desconocida"]["peso"]

def heuristica_contexto_local(titulo, cuerpo):
    texto_unido = limpiar_texto(titulo + " " + cuerpo)
    menciona = any(lugar in texto_unido for lugar in LUGARES_LOCALES_CHIAPAS)
    return 1 if menciona else 0

def heuristica_consistencia(desmentido):
    return 2 if desmentido.strip().lower() in ('si', 'sí', 's') else 0

def clasificar(peso_total):
    if peso_total >= 4:
        return ("PROBABLEMENTE FALSA", "#FF4B4B", "🚨",
                "R1 + R2 activadas: Múltiples alertas graves detectadas.")
    elif peso_total >= 2:
        return ("NECESITA VERIFICACIÓN", "#FFA500", "⚠️",
                "R1 activada: Múltiples indicadores de sospecha.")
    elif peso_total == 1:
        return ("LIGERA SOSPECHA", "#FFD700", "🟡",
                "Indicadores leves detectados.")
    else:
        return ("PROBABLEMENTE VERDADERA", "#00C853", "✅",
                "R3 activada: Fuente confiable, sin indicadores de alerta.")


# ==========================================
# PALETA DE COLORES
# ==========================================
BG_DARK    = "#0D1117"
BG_CARD    = "#161B22"
BG_INPUT   = "#21262D"
ACCENT     = "#58A6FF"
ACCENT2    = "#3FB950"
TEXT_MAIN  = "#E6EDF3"
TEXT_SUB   = "#8B949E"
BORDER     = "#30363D"
FONT_MAIN  = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_SMALL = ("Segoe UI", 9)


# ==========================================
# APLICACIÓN
# ==========================================
class FakeNewsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Clasificador de Fake News · UNACH IA 7°M")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)
        self.minsize(780, 620)

        # Centrar ventana
        self.update_idletasks()
        w, h = 900, 700
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        # ── Encabezado ──────────────────────────────────────────────
        header = tk.Frame(self, bg="#0D1B2A", pady=18)
        header.pack(fill="x")

        tk.Label(header, text="🔍  Clasificador de Fake News",
                 font=FONT_TITLE, fg=ACCENT, bg="#0D1B2A").pack()
        tk.Label(header,
                 text="Sistema Inteligente Heurístico · Universidad Autónoma de Chiapas — IA 7°M",
                 font=FONT_SMALL, fg=TEXT_SUB, bg="#0D1B2A").pack(pady=(2,0))

        # ── Cuerpo principal (dos columnas) ─────────────────────────
        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=20, pady=14)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        left  = tk.Frame(body, bg=BG_DARK)
        right = tk.Frame(body, bg=BG_DARK)
        left.grid (row=0, column=0, sticky="nsew", padx=(0,8))
        right.grid(row=0, column=1, sticky="nsew", padx=(8,0))

        self._build_left(left)
        self._build_right(right)

    # ------------------------------------------------------------------
    def _build_left(self, parent):
        """Panel de entrada."""
        self._card(parent, "📋  Datos de Análisis").pack(fill="x")

        card = self._card(parent)
        card.pack(fill="both", expand=True, pady=(8,0))

        # URL
        self._label(card, "🔗  URL de la noticia")
        self.entry_url = self._entry(card)

        # Título manual
        self._label(card, "📰  Título  (si el scraping falla)")
        self.entry_titulo = self._entry(card)

        # Cuerpo manual
        self._label(card, "📄  Cuerpo del texto  (opcional)")
        self.txt_cuerpo = tk.Text(card, height=5, bg=BG_INPUT, fg=TEXT_MAIN,
                                  insertbackground=ACCENT, relief="flat",
                                  font=FONT_MAIN, wrap="word",
                                  highlightthickness=1,
                                  highlightbackground=BORDER,
                                  highlightcolor=ACCENT)
        self.txt_cuerpo.pack(fill="x", pady=(0,10))

        # Desmentido
        self._label(card, "⚖️  ¿Ha sido desmentida oficialmente?")
        self.desmentido_var = tk.StringVar(value="no")
        row_des = tk.Frame(card, bg=BG_CARD)
        row_des.pack(fill="x", pady=(0,12))
        for texto, valor in [("No", "no"), ("Sí", "si")]:
            rb = tk.Radiobutton(row_des, text=texto, variable=self.desmentido_var,
                                value=valor, bg=BG_CARD, fg=TEXT_MAIN,
                                activebackground=BG_CARD, activeforeground=ACCENT,
                                selectcolor=BG_INPUT, font=FONT_MAIN)
            rb.pack(side="left", padx=(0,16))

        # Botón analizar
        self.btn = tk.Button(card, text="  Analizar Noticia  →",
                             command=self._iniciar_analisis,
                             bg=ACCENT, fg="#0D1117", font=("Segoe UI", 11, "bold"),
                             relief="flat", cursor="hand2", pady=10,
                             activebackground="#79C0FF", activeforeground="#0D1117")
        self.btn.pack(fill="x", pady=(4,0))

        # Barra de progreso
        self.progress = ttk.Progressbar(card, mode="indeterminate")
        self.progress.pack(fill="x", pady=(8,0))
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TProgressbar", troughcolor=BG_INPUT,
                        background=ACCENT, thickness=4)

    # ------------------------------------------------------------------
    def _build_right(self, parent):
        """Panel de resultados."""
        self._card(parent, "📊  Resultados").pack(fill="x")

        # Tarjeta de veredicto
        self.verdict_frame = tk.Frame(parent, bg=BG_CARD,
                                      highlightthickness=1,
                                      highlightbackground=BORDER)
        self.verdict_frame.pack(fill="x", pady=(8,0))

        self.lbl_icon    = tk.Label(self.verdict_frame, text="—", font=("Segoe UI",36),
                                    bg=BG_CARD, fg=TEXT_SUB)
        self.lbl_icon.pack(pady=(14,4))

        self.lbl_verdict = tk.Label(self.verdict_frame,
                                    text="Esperando análisis...",
                                    font=("Segoe UI",13,"bold"),
                                    bg=BG_CARD, fg=TEXT_SUB, wraplength=340)
        self.lbl_verdict.pack(pady=(0,4))

        self.lbl_regla   = tk.Label(self.verdict_frame, text="",
                                    font=FONT_SMALL, fg=TEXT_SUB,
                                    bg=BG_CARD, wraplength=340)
        self.lbl_regla.pack(pady=(0,14))

        # Tabla heurística
        table_card = self._card(parent, "🧪  Tabla Heurística")
        table_card.pack(fill="x", pady=(8,0))
        self._build_table(table_card)

        # Log de proceso
        log_card = self._card(parent, "📝  Log del Proceso")
        log_card.pack(fill="both", expand=True, pady=(8,0))

        self.log = scrolledtext.ScrolledText(
            log_card, height=7, bg=BG_INPUT, fg="#58A6FF",
            insertbackground=ACCENT, relief="flat", font=("Consolas",9),
            wrap="word", state="disabled",
            highlightthickness=0)
        self.log.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    def _build_table(self, parent):
        cols = ["Heurística", "Indicador", "Peso"]
        headers_frame = tk.Frame(parent, bg=BG_INPUT)
        headers_frame.pack(fill="x")
        widths = [160, 180, 60]
        for i, (col, w) in enumerate(zip(cols, widths)):
            tk.Label(headers_frame, text=col, font=FONT_BOLD,
                     fg=ACCENT, bg=BG_INPUT, width=w//8,
                     anchor="w", padx=8, pady=4).grid(row=0, column=i, sticky="w")

        self.table_rows = []
        rows_data = [
            ("Verificabilidad",   "Fuente analizada"),
            ("Estilo Lingüístico","Sensacionalismo"),
            ("Contexto Local",    "Lugar s/respaldo"),
            ("Consistencia",      "Desmentido oficial"),
        ]
        self.table_frame = tk.Frame(parent, bg=BG_CARD)
        self.table_frame.pack(fill="x")

        for i, (heur, ind) in enumerate(rows_data):
            bg = BG_CARD if i % 2 == 0 else BG_INPUT
            row_f = tk.Frame(self.table_frame, bg=bg)
            row_f.pack(fill="x")
            lh = tk.Label(row_f, text=heur, font=FONT_MAIN, fg=TEXT_MAIN,
                          bg=bg, anchor="w", padx=8, pady=3, width=20)
            li = tk.Label(row_f, text=ind,  font=FONT_MAIN, fg=TEXT_SUB,
                          bg=bg, anchor="w", padx=8, pady=3, width=22)
            lp = tk.Label(row_f, text="—",  font=FONT_BOLD, fg=ACCENT,
                          bg=bg, anchor="center", padx=8, pady=3, width=7)
            lh.grid(row=0, column=0, sticky="w")
            li.grid(row=0, column=1, sticky="w")
            lp.grid(row=0, column=2, sticky="w")
            self.table_rows.append(lp)

        # Fila total
        total_f = tk.Frame(parent, bg="#0D1B2A")
        total_f.pack(fill="x")
        tk.Label(total_f, text="TOTAL DE SOSPECHA", font=FONT_BOLD,
                 fg=TEXT_MAIN, bg="#0D1B2A", anchor="w",
                 padx=8, pady=5, width=20).grid(row=0, column=0, sticky="w")
        tk.Label(total_f, text="", bg="#0D1B2A", width=22).grid(row=0,column=1)
        self.lbl_total = tk.Label(total_f, text="—", font=("Segoe UI",10,"bold"),
                                  fg=ACCENT, bg="#0D1B2A", anchor="center",
                                  padx=8, pady=5, width=7)
        self.lbl_total.grid(row=0, column=2, sticky="w")

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------
    def _card(self, parent, title=None):
        frame = tk.Frame(parent, bg=BG_CARD,
                         highlightthickness=1, highlightbackground=BORDER,
                         padx=12, pady=10)
        if title:
            tk.Label(frame, text=title, font=FONT_BOLD,
                     fg=ACCENT, bg=BG_CARD).pack(anchor="w", pady=(0,4))
        return frame

    def _label(self, parent, text):
        tk.Label(parent, text=text, font=FONT_SMALL,
                 fg=TEXT_SUB, bg=BG_CARD, anchor="w").pack(fill="x", pady=(6,2))

    def _entry(self, parent):
        e = tk.Entry(parent, bg=BG_INPUT, fg=TEXT_MAIN,
                     insertbackground=ACCENT, relief="flat",
                     font=FONT_MAIN, highlightthickness=1,
                     highlightbackground=BORDER, highlightcolor=ACCENT)
        e.pack(fill="x", ipady=5, pady=(0,4))
        return e

    def _log(self, msg):
        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    # ------------------------------------------------------------------
    # ANÁLISIS
    # ------------------------------------------------------------------
    def _iniciar_analisis(self):
        url = self.entry_url.get().strip()
        if not url:
            messagebox.showwarning("Campo vacío", "Por favor ingresa una URL.")
            return

        self.btn.configure(state="disabled", text="Analizando...")
        self.progress.start(12)
        self._clear_log()

        thread = threading.Thread(target=self._analizar, args=(url,), daemon=True)
        thread.start()

    def _analizar(self, url):
        self._log(f"[→] URL: {url}")
        titulo = self.entry_titulo.get().strip()
        cuerpo = self.txt_cuerpo.get("1.0", "end").strip()
        fuente = extraer_dominio(url)
        self._log(f"[→] Dominio detectado: {fuente}")

        # Scraping automático
        if NEWSPAPER_OK and not titulo:
            self._log("[→] Intentando scraping automático...")
            try:
                art = Article(url, language='es')
                art.download()
                art.parse()
                if art.title:
                    titulo = art.title
                    self._log(f"[✓] Título obtenido: {titulo[:60]}...")
                if art.text:
                    cuerpo = art.text
                    self._log(f"[✓] Cuerpo extraído ({len(cuerpo)} caracteres).")
            except Exception as e:
                self._log(f"[!] Scraping falló: {e}")
        elif not NEWSPAPER_OK:
            self._log("[!] newspaper3k no disponible. Usando texto manual.")

        if not titulo:
            titulo = url  # fallback mínimo
            self._log("[!] Sin título disponible, usando URL como referencia.")

        desmentido = self.desmentido_var.get()
        self._log(f"[→] ¿Desmentido oficial? {desmentido}")

        # Heurísticas
        self._log("\n[→] Aplicando heurísticas...")
        p_verif = heuristica_verificabilidad(fuente)
        p_sens  = heuristica_sensacionalismo(titulo, cuerpo)
        p_ctx   = heuristica_contexto_local(titulo, cuerpo)
        p_cons  = heuristica_consistencia(desmentido)
        total   = p_verif + p_sens + p_ctx + p_cons

        self._log(f"    Verificabilidad : +{p_verif}")
        self._log(f"    Sensacionalismo : +{p_sens}")
        self._log(f"    Contexto local  : +{p_ctx}")
        self._log(f"    Consistencia    : +{p_cons}")
        self._log(f"    ─────────────────────")
        self._log(f"    TOTAL           : +{total}")

        veredicto, color, icono, regla = clasificar(total)
        self._log(f"\n[✓] Clasificación: {veredicto}")

        # Actualizar UI en hilo principal
        self.after(0, self._actualizar_ui,
                   p_verif, p_sens, p_ctx, p_cons, total,
                   veredicto, color, icono, regla)

    def _actualizar_ui(self, p_verif, p_sens, p_ctx, p_cons,
                       total, veredicto, color, icono, regla):
        # Tabla
        pesos = [p_verif, p_sens, p_ctx, p_cons]
        for lbl, p in zip(self.table_rows, pesos):
            lbl.configure(text=f"+{p}",
                          fg="#FF4B4B" if p > 0 else ACCENT2)
        self.lbl_total.configure(text=f"+{total}", fg=color)

        # Veredicto
        self.lbl_icon.configure(text=icono, fg=color)
        self.lbl_verdict.configure(text=veredicto, fg=color)
        self.lbl_regla.configure(text=regla, fg=TEXT_SUB)

        # Restaurar botón
        self.progress.stop()
        self.btn.configure(state="normal", text="  Analizar Noticia  →")


# ==========================================
# PUNTO DE ENTRADA
# ==========================================
if __name__ == "__main__":
    app = FakeNewsApp()
    app.mainloop()
