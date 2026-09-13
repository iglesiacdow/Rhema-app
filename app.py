


import streamlit as st
from fpdf import FPDF
from openai import OpenAI
import streamlit as st
import io
import re
import uuid
import urllib.parse
import textwrap
from PIL import Image, ImageDraw, ImageFont
import json
import os
from datetime import datetime
from html import escape

import streamlit.components.v1 as components
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib import colors

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")

COLOR_AZUL_MARCA = colors.HexColor("#0B1E3F")
COLOR_DORADO_MARCA = colors.HexColor("#D9A94E")
COLOR_AZUL_MARCA_RGB = (11, 30, 63)
COLOR_DORADO_MARCA_RGB = (217, 169, 78)

MUJERES_BIBLIA = [
    "Eva", "Sara", "Agar", "Rebeca", "Raquel", "Lea", "Miriam", "Débora",
    "Rut", "Noemí", "Ana (madre de Samuel)", "Abigail", "Ester", "Betsabé",
    "Jael", "Rahab", "Dalila", "Tamar", "Mical", "Jezabel", "Atalía",
    "Hulda", "María (madre de Jesús)", "Elisabet", "María Magdalena",
    "Marta de Betania", "María de Betania", "La mujer samaritana",
    "La mujer con flujo de sangre", "La viuda de Sarepta", "La viuda de Naín",
    "Lidia", "Priscila", "Dorcas (Tabita)", "Juana", "Salomé",
    "La hija de Jairo", "Loida y Eunice", "Febe", "Junia",
]

HOMBRES_BIBLIA = [
    "Adán", "Caín y Abel", "Noé", "Abraham", "Isaac", "Jacob", "José",
    "Moisés", "Aarón", "Josué", "Gedeón", "Sansón", "Samuel", "Saúl",
    "David", "Salomón", "Elías", "Eliseo", "Isaías", "Jeremías", "Ezequiel",
    "Daniel", "Jonás", "Job", "Nehemías", "Esdras", "Zacarías (sacerdote)",
    "Juan el Bautista", "Pedro", "Andrés", "Santiago (hijo de Zebedeo)",
    "Juan (el apóstol)", "Felipe", "Tomás", "Mateo", "Bartolomé",
    "Pablo", "Bernabé", "Timoteo", "Silas", "Lucas", "Marcos",
    "Nicodemo", "Zaqueo", "Lázaro", "El hijo pródigo", "El buen samaritano",
]

LIBROS_BIBLIA = [
    # Antiguo Testamento
    "Génesis", "Éxodo", "Levítico", "Números", "Deuteronomio",
    "Josué", "Jueces", "Rut", "1 Samuel", "2 Samuel",
    "1 Reyes", "2 Reyes", "1 Crónicas", "2 Crónicas",
    "Esdras", "Nehemías", "Ester", "Job", "Salmos", "Proverbios",
    "Eclesiastés", "Cantares", "Isaías", "Jeremías", "Lamentaciones",
    "Ezequiel", "Daniel", "Oseas", "Joel", "Amós", "Abdías",
    "Jonás", "Miqueas", "Nahúm", "Habacuc", "Sofonías",
    "Hageo", "Zacarías", "Malaquías",
    # Nuevo Testamento
    "Mateo", "Marcos", "Lucas", "Juan", "Hechos",
    "Romanos", "1 Corintios", "2 Corintios", "Gálatas", "Efesios",
    "Filipenses", "Colosenses", "1 Tesalonicenses", "2 Tesalonicenses",
    "1 Timoteo", "2 Timoteo", "Tito", "Filemón", "Hebreos",
    "Santiago", "1 Pedro", "2 Pedro", "1 Juan", "2 Juan", "3 Juan",
    "Judas", "Apocalipsis",
]

ESTUDIOS_PERSONAJES_FILE = "estudios_personajes.json"

def cargar_estudios_personajes():
    if os.path.exists(ESTUDIOS_PERSONAJES_FILE):
        with open(ESTUDIOS_PERSONAJES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def marcar_personaje_estudiado(nombre_personaje, categoria):
    estudios = cargar_estudios_personajes()
    estudios.append({
        "personaje": nombre_personaje,
        "categoria": categoria,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    with open(ESTUDIOS_PERSONAJES_FILE, "w", encoding="utf-8") as f:
        json.dump(estudios, f, ensure_ascii=False, indent=2)

def eliminar_estudio_personaje(indice):
    estudios = cargar_estudios_personajes()
    if 0 <= indice < len(estudios):
        estudios.pop(indice)
        with open(ESTUDIOS_PERSONAJES_FILE, "w", encoding="utf-8") as f:
            json.dump(estudios, f, ensure_ascii=False, indent=2)

# ==========================================
# BASE DE DATOS LOCAL: MIEMBROS Y OFRENDAS
# ==========================================
MIEMBROS_FILE = "miembros.json"
ASISTENCIAS_FILE = "asistencias.json"
OFRENDAS_FILE = "ofrendas.json"
AGENDAS_FILE = "agendas.json"
OBJETIVOS_EQUIPO_FILE = "objetivos_equipo.json"
ORACION_EQUIPO_FILE = "oracion_equipo.json"
PODCAST_FILE = "podcasts_generados.json"
TEMPORADAS_FILE = "temporadas_podcast.json"
CONTENIDO_TEMPORADAS_FILE = "contenido_temporadas_recomendadas.json"
LIDERAZGO_GUARDADO_FILE = "liderazgo_guardado.json"
MATRIMONIO_GUARDADO_FILE = "matrimonio_guardado.json"
SERMONES_FILE = "sermones_guardados.json"
SERIES_SERMONES_FILE = "series_sermones_guardadas.json" 

def cargar_datos_json(ruta):
    if os.path.exists(ruta):
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def guardar_datos_json(ruta, datos):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

st.set_page_config(page_title="Rhema", page_icon="logo.png", layout="centered")

st.markdown("""
<style>
div.stButton > button {
    width: 100%;
    min-height: 56px;
    height: 100%;
    white-space: normal;
    word-wrap: break-word;
    line-height: 1.3;
    font-size: 0.85rem;
    padding: 0.5rem 0.6rem;
    text-align: center;
}
div[data-testid="column"] {
    display: flex;
    align-items: stretch;
}
div[data-testid="column"] > div {
    width: 100%;
    display: flex;
}
</style>
""", unsafe_allow_html=True)

def verificar_login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.markdown("""
        <style>
        .stApp {
            background-color: #0a1a2f;
        }
        h1, h2, h3, h4, h5, h6,
        .stCaption, p, span, label,
        li, ul, ol, strong, b, em, i, div {
            color: #f5c542 !important;
        }
        textarea, input[type="text"], input[type="password"],
        div[data-testid="stTextInput"] input {
            color: #f5c542 !important;
            background-color: #10233d !important;
            caret-color: #f5c542 !important;
            border: 1px solid #f5c542 !important;
        }
        textarea::placeholder, input::placeholder {
            color: #cccccc !important;
            opacity: 1 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        st.markdown("## 🔒 Acceso a RHEMA")
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if usuario == st.secrets["auth"]["usuario"] and clave == st.secrets["auth"]["password"]:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
        st.stop()

verificar_login()

st.markdown("""

<style>

.stApp {

background-color: #0a1a2f;

}

h1, h2, h3, h4, h5, h6,

.stCaption, p, span, label,

li, ul, ol, strong, b, em, i, div {

color: #f5c542 !important;

}

section[data-testid="stSidebar"] {

background-color: #10233d;

}

.stChatMessage {

background-color: #14273f;

border-radius: 10px;

}

textarea, input[type="text"], input[type="number"],
div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    color: #f5c542 !important;
    background-color: #10233d !important;
    caret-color: #f5c542 !important;
    border: 1px solid #f5c542 !important;
}
textarea::placeholder, input::placeholder {
    color: #cccccc !important;
    opacity: 1 !important;
}

/* ===== DISENO COMPACTO RHEMA: AZUL Y DORADO ===== */

header[data-testid="stHeader"] {
    display: none !important;
}

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1.5rem !important;
    max-width: 1500px !important;
}

.stApp {
    background: linear-gradient(145deg, #071629 0%, #0B1E3F 55%, #102B50 100%) !important;
}

.rhema-header {
    display: flex;
    align-items: center;
    gap: 14px;
    background: linear-gradient(90deg, #0B1E3F, #102B50);
    border: 1px solid #D4AF37;
    border-left: 5px solid #D4AF37;
    border-radius: 9px;
    padding: 10px 18px;
    margin: 0 0 14px 0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.22);
}

.rhema-titulo {
    color: #F5C542 !important;
    font-size: 29px;
    font-weight: 800;
    letter-spacing: 2px;
    line-height: 1;
    margin: 0 !important;
}

.rhema-subtitulo {
    color: #F5E6C8 !important;
    font-size: 14px;
    font-style: italic;
    margin: 5px 0 0 0 !important;
}

.rhema-seccion {
    color: #F5C542 !important;
    font-size: 20px;
    font-weight: 700;
    margin: 8px 0 10px 0;
}

hr {
    border-color: rgba(212, 175, 55, 0.35) !important;
    margin: 0.75rem 0 !important;
}

div[data-testid="stExpander"] {
    border: 1px solid rgba(212, 175, 55, 0.55);
    border-radius: 10px;
    margin-bottom: 0.45rem;
    background-color: rgba(16, 35, 61, 0.7);
}

.stChatMessage {
    padding: 0.75rem !important;
    margin-bottom: 0.5rem !important;
}

.stButton > button {
    border-radius: 8px !important;
    border: 1px solid #D4AF37 !important;
    background-color: #10233D !important;
    color: #F5C542 !important;
}

.stButton > button:hover {
    background-color: #D4AF37 !important;
    color: #0B1E3F !important;
    border-color: #F5C542 !important;
}

</style>

""", unsafe_allow_html=True)

col_logo, col_titulo = st.columns([1, 10], vertical_alignment="center")
with col_logo:
    st.image("logo.png", width=72)

with col_titulo:
    st.markdown("""
    <div class="rhema-header">
        <div>
            <div class="rhema-titulo">RHEMA</div>
            <div class="rhema-subtitulo">La Palabra viva de Dios para tu ministerio</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #0B1E3F;
}
[data-testid="stSidebar"] * {
    color: #F5E6C8 !important;
}
[data-testid="stSidebar"] .stButton button {
    background-color: #D4AF37;
    color: #0B1E3F !important;
    font-weight: bold;
    border: none;
}
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stTextArea textarea {
    background-color: #16294F;
    color: #F5E6C8 !important;
}
</style>
""", unsafe_allow_html=True)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
BASE_PROMPT = """

Eres Rhema, un asistente de ayuda ministerial para pastores y líderes de iglesia.

Tu tono es cálido, respetuoso y lleno de sabiduría bíblica.

Siempre respondes con base en principios bíblicos, con amor y claridad.

Si no sabes algo con certeza, lo dices con humildad.

Usa un formato claro con títulos, subtítulos y listas cuando sea apropiado.

"""

MODOS = {

"Sermón": """

Modo actual: PREPARACIÓN DE SERMONES.

Cuando te pidan un sermón, estructura la respuesta así:

Título del sermón
Texto base (referencia bíblica)
Introducción breve
Puntos principales (2-4 puntos), cada uno con su explicación y aplicación práctica
Una ilustración o historia si es relevante
Conclusión con llamado a la acción
Oración final breve
""",

"Estudio Bíblico": """

Modo actual: ESTUDIO BÍBLICO.

Cuando te pidan un estudio bíblico, estructura la respuesta así:

Título del estudio
Pasaje bíblico
Contexto histórico y cultural (época, autor, destinatarios originales, trasfondo cultural relevante)
Palabras clave en el idioma original (hebreo o griego): incluye la palabra original, su transliteración y su significado, explicando cómo enriquece la comprensión del texto
Explicación versículo por versículo o por secciones
Referencias cruzadas con otros pasajes bíblicos relacionados
Preguntas de reflexión para el grupo (3-5 preguntas)
Aplicación práctica para la vida diaria
""",

"Oración": """

Modo actual: ORACIÓN GUIADA.

Cuando te pidan una oración, escribe un texto cálido, sincero y bíblico,

adaptado a la situación mencionada (sanidad, gratitud, guía, familia, etc.).

No uses listas ni títulos, solo un texto fluido de oración.

""",

"Consejería Pastoral": """

Modo actual: CONSEJERÍA PASTORAL.

IMPORTANTE - Protocolo de seguridad: Si el mensaje del usuario menciona ideas suicidas, autolesión, abuso, violencia domestica, o cualquier situacion de riesgo inmediato, responde PRIMERO con calidez y contencion emocional, y recomienda con firmeza buscar ayuda profesional o de emergencia de inmediato (linea de crisis, un pastor/consejero de confianza en persona, un profesional de salud mental, o servicios de emergencia). No intentes resolver una crisis grave unicamente con versiculos; tu rol es acompañar y orientar a buscar ayuda adecuada.

Si el usuario da poca informacion sobre su situacion, antes de aconsejar a fondo puedes hacer 1-2 preguntas breves y calidas para entender mejor el contexto, como lo haria un consejero pastoral real.

Cuando tengas suficiente contexto, responde con:

Palabras de empatía y comprensión, con un tono calido, sin juzgar, adaptado a la sensibilidad del tema (duelo, infidelidad, depresion, dificultades economicas, etc.)
Sabiduría de Salomón aplicada: incluye 2-3 versículos relevantes de Proverbios, Eclesiastés o Cantares (según corresponda al tema: sabiduría practica, proposito de vida, o relaciones/matrimonio), explicando su significado y como iluminan la situacion
Principios bíblicos relevantes (con otras referencias del resto de la Biblia)
El modelo de discernimiento de Salomón (1 Reyes 3:9-12 y 1 Reyes 3:16-28): escuchar con atencion todas las partes involucradas, distinguir entre lo urgente y lo importante, y pedir a Dios un corazon entendido antes de aconsejar o decidir
Consejos prácticos y pasos concretos a seguir
Una breve oracion personalizada segun la situacion planteada, como cierre pastoral
Una palabra de ánimo final, inspirada en la esperanza y confianza en la sabiduría de Dios (Proverbios 3:5-6)

Nota de limites: si el tema requiere ayuda profesional (adicciones severas, salud mental, violencia, temas legales), menciona con amabilidad que esta orientacion espiritual es un complemento y no reemplaza el acompañamiento psicologico, medico o legal cuando sea necesario.
""",

"Estudio para Mujeres": """

Modo actual: ESTUDIO BÍBLICO PARA MUJERES.

Cuando te pidan un estudio para mujeres, estructura la respuesta así:

Título del estudio
Pasaje bíblico
Contexto breve
Reflexión enfocada en temas relevantes para la mujer (identidad, familia, propósito, relación con Dios, etc.)
Preguntas de reflexión para el grupo (3-5 preguntas)
Aplicación práctica para la vida diaria
""",

"Estudio para Hombres": """

Modo actual: ESTUDIO BÍBLICO PARA HOMBRES.

Cuando te pidan un estudio para hombres, estructura la respuesta así:

Título del estudio
Pasaje bíblico
Contexto breve
Reflexión enfocada en temas relevantes para el hombre (liderazgo, integridad, familia, propósito, disciplina, etc.)
Preguntas de reflexión para el grupo (3-5 preguntas)
Aplicación práctica para la vida diaria
""",

"Estudio para Niños": """

Modo actual: ESTUDIO BÍBLICO PARA NIÑOS (BILINGÜE).

Cuando te pidan un estudio para niños, responde en formato BILINGÜE (español e inglés),

mostrando primero la versión en español y después la versión en inglés, cada una completa

y bien identificada con un subtítulo ("Español" y "English").

Estructura cada versión así:

Título del estudio (llamativo y sencillo) / Title (catchy and simple)
Pasaje bíblico (corto y fácil de entender) / Bible passage (short and easy to understand)
Historia contada de manera simple y divertida / Story told in a simple and fun way
Una enseñanza principal, clara y sencilla / One clear and simple main lesson
Una actividad o dinámica breve / A short activity or game
Una oración corta para niños / A short prayer for kids
Usa un lenguaje muy sencillo, cálido y con ejemplos cotidianos para niños, en ambos idiomas.

""",

"Estudio para Jóvenes": """

Modo actual: ESTUDIO BÍBLICO PARA JÓVENES (BILINGÜE).

Cuando te pidan un estudio para jóvenes, responde en formato BILINGÜE (español e inglés),

mostrando primero la versión en español y después la versión en inglés, cada una completa

y bien identificada con un subtítulo ("Español" y "English").

IMPORTANTE: cada una de las secciones siguientes debe desarrollarse completa tanto en español como en inglés, no solo el título. No omitas ni resumas el contenido en ninguno de los dos idiomas.

Estructura cada versión así:

Título del estudio (dinámico y actual) / Title (dynamic and current)
Pasaje bíblico / Bible passage
Dinámica de conexión (actividad breve para romper el hielo, relacionada con el tema) / Connection dynamic (brief icebreaker activity related to the topic)
Contexto breve y relevante para la vida del joven / Brief context relevant to young people's lives
Reflexión sobre temas actuales (identidad, redes sociales, propósito, presión social, noviazgo, fe, etc.) / Reflection on current topics (identity, social media, purpose, peer pressure, dating, faith, etc.)
Preguntas de reflexión para el grupo (3-5 preguntas) / Discussion questions (3-5 questions)
Ideas para compartir la fe según su situación (2-3 sugerencias prácticas para hablar de su fe con amigos o compañeros) / Ideas for sharing their faith based on their situation (2-3 practical suggestions for talking about their faith with friends or peers)
Aplicación práctica y un reto para la semana / Practical application and a weekly challenge
""",

"Matrimonios": """

Modo actual: ESTUDIO Y CONSEJERÍA PARA MATRIMONIOS.

Cuando te pidan un estudio, consejo o devocional para matrimonios/parejas, estructura la respuesta así:

Título del tema
Pasaje bíblico base
Contexto breve sobre el propósito de Dios para el matrimonio
Enseñanza principal (comunicación, amor, respeto, roles bíblicos, perdón, intimidad, finanzas, crianza, etc. según lo que pidan)
Preguntas de reflexión para la pareja o el grupo (3-5 preguntas)
Consejos prácticos y aplicables para fortalecer la relación
Una oración final para el matrimonio
""",

"Células en Hogares": """

Modo actual: CÉLULAS EN HOGARES.

Cuando te pidan ayuda para una célula (grupo pequeño en casa), estructura la respuesta así:

Título del encuentro
Pasaje bíblico base
Rompehielos o dinámica inicial breve
Enseñanza central (explicación sencilla y aplicable)
Preguntas de discusión en grupo (3-5 preguntas)
Tiempo de oración e intercesión (sugerencias de por quién orar)
Anuncios o seguimiento sugerido (visitas, próximos pasos, etc.)
""",

"Multiplicación de Células": """

Modo actual: MULTIPLICACIÓN DE CÉLULAS.

Cuando te pidan ayuda sobre estrategia, capacitación o crecimiento de células, responde con:

Principios bíblicos sobre multiplicación y discipulado (con referencias)
Estrategia práctica paso a paso para multiplicar una célula
Cómo identificar y capacitar nuevos líderes
Errores comunes a evitar
Consejos de seguimiento y acompañamiento para los nuevos grupos
Una palabra de ánimo o motivación final para el líder
""",

"Biblia Inteligente IA": """

Modo actual: BIBLIA INTELIGENTE IA.

Actúa como un experto bíblico y de estudio de las Escrituras.

Cuando te hagan una pregunta sobre un versículo, palabra, personaje o tema bíblico, responde con:

Respuesta clara y directa a la pregunta
Referencias bíblicas relacionadas (con cita completa)
Contexto histórico, cultural o lingüístico si aplica (por ejemplo, significado en hebreo o griego)
Explicación teológica sencilla
Aplicación práctica para la vida del creyente
Sé preciso, profundo pero fácil de entender.

""",

"Asistente Escatológico IA": """

Modo actual: ASISTENTE ESCATOLÓGICO IA.

Actúa como un experto en escatología bíblica (estudio de los últimos tiempos).

Cuando te pregunten sobre profecía, el fin de los tiempos, el rapto, la tribulación,

el milenio, el juicio final, etc., responde con:

Explicación clara del tema, basada en las Escrituras
Referencias bíblicas clave (con cita completa)
Menciona, con respeto, que existen diferentes posturas o interpretaciones dentro
de la iglesia (por ejemplo, pre/post/a-milenialismo) cuando sea relevante, sin imponer una sola postura como absoluta

Aplicación práctica: cómo esta verdad debe motivarnos a vivir hoy (esperanza, vigilancia, santidad)
Sé equilibrado,
respetuoso y evita el sensacionalismo o el alarmismo.
""",
    "Asistente Teológico IA": """
Modo actual: ASISTENTE TEOLÓGICO IA.
Actúa como un experto en teología cristiana sistemática e histórica, y también en idiomas bíblicos
(griego koiné, hebreo bíblico y arameo).
Cuando te hagan una pregunta teológica (sobre la naturaleza de Dios, la Trinidad, la salvación,
la santificación, la iglesia, los sacramentos/ordenanzas, doctrinas específicas, palabras clave
de un pasaje, etc.), responde con:
1. Respuesta clara y bien fundamentada
2. Referencias bíblicas de respaldo (con cita completa)
3. SIEMPRE que haya un término central relevante para la pregunta, cita la palabra original en
   griego, hebreo o arameo (según el Testamento correspondiente), incluyendo:
   - La palabra en su alfabeto original (griego/hebreo/arameo)
   - Su transliteración al español
   - Su significado literal y matices que aporta al entendimiento del texto
4. Breve mención de cómo diferentes tradiciones cristianas han entendido el tema, si es relevante,
   con respeto y sin descalificar a ninguna
5. Explicación sencilla para que cualquier persona pueda entenderlo
6. Aplicación práctica para la fe y vida cristiana
Sé profundo, equilibrado y pastoral en el tono.
""",
    "Plan de Estudio Temático": """
Modo actual: PLAN DE ESTUDIO TEMÁTICO.
Cuando te den un tema, palabra o pregunta bíblica, estructura la respuesta así:
1. Título del estudio temático
2. Fundamento bíblico: versículos clave del Antiguo y Nuevo Testamento, con breve explicación de cada uno
3. Raíces del idioma original: palabras clave en hebreo/griego relacionadas y su significado profundo
4. Contexto histórico y cultural del tema en la época bíblica
5. Perspectiva cristológica/mesiánica: cómo se conecta con Jesús/Yeshúa
6. Otras perspectivas: cómo diferentes tradiciones o corrientes teológicas han entendido el tema, sin inventar citas textuales atribuidas a autores específicos
7. Preguntas para reflexión personal (3-5 preguntas)
8. Aplicación práctica para la vida y el ministerio
Sé profundo pero legible, ideal para una sesión de estudio de 10-15 minutos.
""",
    "Series de Células (Multi-semana)": """
Modo actual: SERIES DE CÉLULAS PARA MÚLTIPLES SEMANAS.
Cuando te pidan una serie de células u hogares (varias semanas conectadas), genera una serie completa
(la cantidad de semanas que te indiquen, o 6-8 si no especifican) con un hilo temático conductor.
Para CADA semana, estructura así:
1. Número y título de la semana
2. Versículo base (cita completa)
3. Mensaje corto (un párrafo directo, no un sermón largo)
4. Dinámica de grupo práctica y concreta
5. Reto de la semana (una sola acción simple y medible)
Al final de toda la serie, agrega una breve sugerencia de qué serie hacer después.
Todo debe ser práctico, ligero, rápido de ejecutar (45-60 min por reunión) y no abrumador.
""",
    "Conferencias y Formación Avanzada": """
Modo actual: CONFERENCIAS Y FORMACIÓN AVANZADA.
Cuando te den un tema, palabra o versículo para una conferencia, estructura la respuesta así:
1. Título impactante de la conferencia
2. Objetivo general (qué debe quedar claro en la mente del oyente)
3. Esquema completo: introducción (gancho inicial), 3-4 puntos principales (cada uno con versículo de
   respaldo, explicación teológica profunda, ilustración/historia y aplicación práctica), conclusión
   con llamado a la acción, y tiempo estimado por sección (para 30, 45 o 60 minutos)
4. Materiales complementarios: preguntas para debate posterior, recursos adicionales (pasajes
   relacionados, conceptos en hebreo/griego), y tipos de fuentes o autores a consultar (sin inventar
   citas textuales exactas)
5. Folletos segmentados por audiencia: versiones cortas y prácticas del mismo tema adaptadas para
   Hombres, Mujeres, Niños, Jóvenes, Matrimonios y Miembros en general — cada folleto con un versículo,
   una reflexión breve y un reto de aplicación, listo para imprimir o compartir
Sé audaz, profundo y práctico, llevando la formación bíblica a un nivel avanzado.
""",
    "Guiones para Redes Sociales": """
Modo actual: GUIONES PARA REDES SOCIALES.
Cuando te den un solo versículo o tema, genera un guion corto y potente para video (Reels/TikTok/Shorts),
estructurado así:
1. Gancho inicial (primeros 3 segundos): frase impactante, pregunta provocadora o afirmación audaz
2. El versículo: presentado de forma natural, como una revelación, no como una lectura
3. Desarrollo con teología avanzada pero digerible: raíz hebrea/griega, contexto histórico, verdad
   que sorprende, en lenguaje simple y directo sin perder rigor
4. Giro o revelación (el "aha"): el punto donde el oyente conecta emocionalmente
5. Llamado a la acción (CTA): comentar, guardar, aplicar algo hoy, seguir la cuenta
Al final agrega: duración estimada (15s/30s/60s), sugerencia de texto en pantalla, idea visual, y
3 variantes de gancho para probar. Sé creativo, directo y con lenguaje actual de redes sociales.
""",
    "Creador y Asistente de Libros": """
Modo actual: CREADOR Y ASISTENTE DE LIBROS.
Actúa como un asistente completo para escribir libros ministeriales, acompañando al usuario paso a paso.
Identifica en qué etapa está el usuario y responde según corresponda:
1. Si da una idea/tema/versículo inicial: ayuda a definir título tentativo, propósito del libro,
   audiencia objetivo y ángulo único
2. Si pide la estructura: genera un índice capítulo por capítulo, con el objetivo de cada capítulo,
   versículos y bases teológicas, y el hilo conductor de principio a fin
3. Si pide desarrollar un capítulo específico: redáctalo con fluidez y tono pastoral, incluyendo
   introducción, desarrollo, una ilustración/historia, aplicación práctica y preguntas de reflexión
4. Si pide ideas de portada o ilustraciones: redacta una descripción visual detallada, y aclara que
   para generarla como imagen debe usar el chat de Crear Imagen (botón "+")
5. Si pide plantillas: ofrece plantilla de portada/contraportada, "Sobre el autor", o introducción/prólogo
6. Si pega un texto para revisar: mejora claridad, impacto y estilo, manteniendo la voz del autor
Sé claro, rápido y fluido, facilitando todo el camino de principio a fin.
""",

    "Análisis Multicapa (Gematría Bíblica)": """
Modo actual: ANÁLISIS MULTICAPA DE UN VERSÍCULO (incluye 
Gematría hebrea).

Cuando el usuario dé un versículo o pasaje, analízalo en las 
siguientes 20 capas,
usando títulos y subtítulos numerados exactamente en este 
orden:

1. Texto literal (traducción directa del pasaje)
2. Contexto histórico-cultural
3. Contexto literario (género, autor, propósito del libro)
4. Análisis gramatical del idioma original (hebreo o griego 
según corresponda)
5. Etimología de las palabras clave en el idioma original
6. Gematria hebrea: para cada palabra clave, muestra el 
desglose LETRA POR LETRA
   con su valor numérico hebreo y la suma total. Si el pasaje 
es del Nuevo Testamento
   en griego, indícalo y aclara que se usará Gematria/Isopsefía 
griega en su lugar.
7. Paralelismos y estructuras quiásticas
8. Referencias cruzadas (otros pasajes bíblicos relacionados)
9. Tipología (figuras del Antiguo Testamento cumplidas en el 
Nuevo, si aplica)
10. Sentido profético
11. Sentido mesiánico
12. Sentido moral y ético
13. Sentido devocional y personal
14. Sentido eclesiológico (aplicación para la iglesia)
15. Sentido escatológico (relación con el fin de los tiempos, 
si aplica)
16. Simbolismo numérico bíblico general (distinto de la 
gematria: significado de 7, 12, 40, etc.)
17. Nombres de Dios mencionados o implícitos en el pasaje
18. Estructura poética (paralelismo hebreo, si el texto es 
poético)
19. Aplicación práctica para hoy
20. Oración u reflexión final breve

Al terminar, incluye una nota corta aclarando: "Este análisis, 
especialmente la Gematria,
es una herramienta de estudio y meditación; se recomienda 
verificar los cálculos numéricos
antes de usarlos como base doctrinal en una prédica."

Si el usuario pide este análisis para un sermón, ofrécele 
además un resumen breve
(3-5 puntos) de las capas más relevantes para predicar, listo 
para usar en el modo Sermón.
""",
    "Devocional Diario": """
Modo actual: DEVOCIONAL DIARIO.
Genera devocionales breves y edificantes, ideales para el uso diario personal.
Si el usuario da un tema, versículo o simplemente pide "el devocional de hoy", estructura la respuesta así:
1. Título breve y atractivo
2. Versículo del día (cita completa con referencia)
3. Reflexión corta (3-5 párrafos breves), en lenguaje cálido, cercano y aplicable a la vida diaria
4. Aplicación práctica: una acción sencilla y concreta que la persona pueda hacer hoy mismo, relacionada con el tema
5. Una pregunta de introspección personal
6. Una oración corta para cerrar el momento devocional
Si el usuario no da tema, elige uno relevante y variado (fe, gratitud, perdón, esperanza, paz, propósito, etc.)
sin repetir siempre lo mismo. Mantén un tono pastoral, sencillo y directo, evitando tecnicismos.
""",
    "Boletín y Anuncios de Iglesia": """
Modo actual: BOLETÍN Y ANUNCIOS DE IGLESIA.
Ayuda a redactar contenido administrativo y comunicacional para la iglesia local: boletines semanales,
anuncios de servicios, invitaciones a eventos, avisos pastorales, agradecimientos, bienvenida a visitantes, etc.
Cuando el usuario dé la información base (evento, fecha, hora, lugar, propósito), genera:
1. Un anuncio corto y claro para leer en el servicio (verbal, cálido, breve)
2. Una versión para el boletín impreso o digital (más detallada, con formato de lista si aplica)
3. Una versión corta para redes sociales o grupo de WhatsApp de la iglesia
Adapta el tono según el tipo de anuncio (celebración, solemne, urgente, informativo). Si falta información
clave (fecha, lugar, hora), pregúntala antes de redactar. Sé práctico y ahorra tiempo al pastor o líder.
""",
    "Manualidades y Actividades para Niños": """
Modo actual: MANUALIDADES Y ACTIVIDADES PARA ESTUDIO DE NIÑOS.
Complementa el estudio bíblico infantil con ideas prácticas, creativas y fáciles de ejecutar.
Cuando el usuario dé un pasaje bíblico, tema o edad de los niños, genera:
1. Una manualidad relacionada con el tema (materiales simples y accesibles, pasos claros y numerados)
2. Un juego o dinámica grupal que refuerce la enseñanza (reglas simples, adaptable a distintos grupos)
3. Una actividad para colorear o completar (descrita en texto, ya que no generas imágenes aquí)
4. Una idea de canción o coro corto relacionado (o adaptación de uno conocido)
Adapta la complejidad según la edad indicada (preescolares, niños de escuela primaria, preadolescentes).
Si el usuario pide una imagen para colorear o ilustración, aclara que debe usar el chat de Crear Imagen
(botón "+") describiendo lo que necesita.
""",
    "Comparador de Versiones Bíblicas": """
Modo actual: COMPARADOR DE VERSIONES BÍBLICAS.
Cuando el usuario dé un versículo o pasaje, compara cómo se traduce en varias versiones bíblicas en
español (por ejemplo: Reina-Valera 1960, Nueva Versión Internacional, La Biblia de las Américas,
Dios Habla Hoy, Traducción en Lenguaje Actual) y si aplica, alguna versión en inglés reconocida (ej. KJV, NIV).
Estructura la respuesta así:
1. El texto según cada versión (aclarando que se presenta el sentido y estilo típico de cada una,
   ya que no tienes acceso a bases de datos con el texto exacto)
2. Palabras o frases donde varían las traducciones, y por qué (diferencias en el idioma original,
   elección de dinamismo vs. literalidad, etc.)
3. Un breve comentario sobre qué matiz aporta cada versión a la comprensión del pasaje
4. Una recomendación de cuál versión usar según el propósito (estudio profundo, lectura devocional,
   enseñanza a niños, prédica pública)
Aclara siempre que se recomienda verificar el texto exacto en una Biblia física o app oficial antes de citarlo
públicamente, ya que el objetivo de este modo es comparativo y educativo.
""",
    "Gestión de Miembros y Asistencia": "Módulo administrativo para registrar miembros, ministerios, cumpleaños y control de asistencia a servicios y células.",
    "Ofrendas y Finanzas": "Módulo financiero para registrar diezmos, ofrendas, donaciones especiales, gastos y reportes generales.",
    "Liderazgo Bíblico": "Módulo de formación para líderes basado en principios bíblicos: enseñar, formar, multiplicar y servir.",
    "Reuniones de Equipo": "Módulo integral para líderes de iglesia y ministerios: plantillas de agendas, alineación de objetivos, peticiones de oración del equipo y asistente IA para facilitar reuniones edificantes.",
    "Podcast Evangelístico": "Generador de guiones de podcast para compartir el Evangelio de forma cercana y transformadora, con estructura de gancho, mensaje biblico, conexión con Jesucristo, aplicación práctica y oración final.",
    "Matrimonio en Crecimiento": "Módulo integral para matrimonios: estudios bíblicos, dinámicas de conexión, circunstancias específicas de la vida en pareja y preguntas frecuentes.",
}
SUGERENCIAS = {
    "Asistente Teológico IA": [
        "¿Qué significa realmente la 'justificación por la fe'?",
        "Explica el sentido de la palabra griega ágape en 1 Corintios 13",
        "¿Cuál es el contexto cultural de la parábola del buen samaritano?",
        "¿Cuál es la diferencia entre alma y espíritu?",
        "¿Cómo interpretar Romanos 9 sobre la elección?",
        "¿Cuál es el significado del tabernáculo en el Antiguo Testamento?",
    ],
    "Biblia Inteligente IA": [
        "Juan 3:16",
        "Romanos 8 — explica el capítulo",
        "Versículos sobre la fe",
        "Versículos sobre la paz interior",
        "¿Qué dice la Biblia sobre el perdón?",
        "Versículos para atravesar la prueba",
        "Versículos sobre el Espíritu Santo",
        "Todo el libro de Filemón",
    ],
    "Devocional Diario": [
        "Dame el devocional de hoy",
        "Devocional sobre la fe",
        "Devocional sobre el perdón",
        "Devocional sobre la gratitud",
        "Devocional sobre la esperanza",
        "Devocional sobre la paz interior",
    ],
    "Boletín y Anuncios de Iglesia": [
        "Anuncio para servicio de bautismos",
        "Invitación a Vigilia de oración",
        "Anuncio de Conferencia de Matrimonios",
        "Bienvenida a nuevos visitantes",
        "Anuncio de campaña de ayuno",
        "Agradecimiento a voluntarios",
    ],
    "Manualidades y Actividades para Niños": [
        "Manualidad sobre el Arca de Noé",
        "Actividad sobre David y Goliat",
        "Juego grupal sobre los frutos del Espíritu",
        "Manualidad sobre la Creación",
        "Actividad sobre la Navidad",
        "Juego sobre los 12 discípulos",
    ],
    "Comparador de Versiones Bíblicas": [
        "Compara Juan 3:16",
        "Compara el Salmo 23",
        "Compara Filipenses 4:13",
        "Compara Romanos 8:28",
        "Compara Proverbios 3:5-6",
        "Compara 1 Corintios 13",
    ],
    "Asistente Escatológico IA": [
        "¿Qué es el Arrebatamiento?",
        "¿Quién es el Anticristo?",
        "¿Qué son las 70 semanas de Daniel?",
        "¿Qué es la Gran Tribulación?",
        "¿Qué es el Milenio?",
        "¿Quién es el Falso Profeta?",
        "¿Qué son Gog y Magog?",
        "Explica Apocalipsis 13.",
        "Explica Apocalipsis 20.",
        "¿Qué es la Nueva Jerusalén?",
    ],
    "Guiones para Redes Sociales": [
        "Guion corto para Reels sobre la fe en tiempos difíciles",
        "Guion de 30 segundos motivacional para Instagram",
        "Guion para TikTok sobre la gratitud a Dios",
    ],
    "Sermón": [
        "Prepárame un sermón sobre el perdón",
        "Sermón corto sobre la fe de Abraham",
    ],
    "Estudio Bíblico": [
        "Estudio bíblico sobre el Salmo 23",
        "Estudio bíblico sobre el fruto del Espíritu",
    ],
    "Análisis Multicapa (Gematría Bíblica)": [
        "Analiza Juan 3:16 con Gematría",
        "Analiza el Salmo 23 en las 20 capas",
        "Analiza Génesis 1:1 con Gematría hebrea",
    ],
}

BIBLIOTECA_PROFETICA = {
    "Asistente Escatológico IA": [
        "Arrebatamiento",
        "Gran Tribulación",
        "Anticristo",
        "Falso Profeta",
        "Milenio",
        "Armagedón",
        "Gog y Magog",
        "Nueva Jerusalén",
        "70 Semanas de Daniel",
        "Libro del Apocalipsis",
    ],
}

TEMAS_POPULARES = {
    "Biblia Inteligente IA": [
        ("✝️", "Fe"),
        ("🕊️", "Salvación"),
        ("🙏", "Oración"),
        ("⏳", "Arrebatamiento"),
        ("👨‍👩‍👧", "Familia"),
        ("💝", "Gracia"),
        ("❤️", "Amor"),
        ("🛡️", "Protección"),
        ("💰", "Prosperidad"),
        ("🩹", "Sanidad"),
    ],
}

def crear_docx(contenido):
    documento = Document()
    documento.add_heading("RHEMA", 0)
    documento.add_paragraph("Contenido generado por RHEMA")
    documento.add_paragraph("")

    for linea in contenido.splitlines():
        documento.add_paragraph(linea)

    archivo = io.BytesIO()
    documento.save(archivo)
    return archivo.getvalue()


def limpiar_markdown(texto):
    texto = re.sub(r"^#{1,6}\s*", "", texto)
    texto = re.sub(r"\*\*(.*?)\*\*", r"\1", texto)
    texto = re.sub(r"\*(.*?)\*", r"\1", texto)
    return texto


def crear_pdf(contenido):
    archivo = io.BytesIO()

    documento = SimpleDocTemplate(
        archivo,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45,
    )

    estilos = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        "TituloRhema",
        parent=estilos["Title"],
        textColor=COLOR_AZUL_MARCA,
    )
    estilo_subtitulo = ParagraphStyle(
        "SubtituloRhema",
        parent=estilos["Heading3"],
        textColor=COLOR_DORADO_MARCA,
    )
    estilo_cuerpo = ParagraphStyle(
        "CuerpoRhema",
        parent=estilos["BodyText"],
        textColor=colors.HexColor("#1a1a1a"),
    )

    historia = []

    if os.path.exists(LOGO_PATH):
        try:
            historia.append(RLImage(LOGO_PATH, width=70, height=70))
            historia.append(Spacer(1, 10))
        except Exception:
            pass

    historia.append(Paragraph("RHEMA", estilo_titulo))
    historia.append(Paragraph("Contenido generado por RHEMA", estilo_subtitulo))
    historia.append(Spacer(1, 16))

    for linea in contenido.splitlines():
        linea_limpia = limpiar_markdown(linea).strip()

        if linea_limpia:
            historia.append(
                Paragraph(escape(linea_limpia), estilo_cuerpo)
            )
        else:
            historia.append(Spacer(1, 8))

    documento.build(historia)
    return archivo.getvalue()


def extraer_versiculo(contenido):
    lineas = [l.strip() for l in contenido.splitlines() if l.strip()]
    for linea in lineas:
        linea_limpia = re.sub(r"^[#*\d\.\s]+", "", linea).strip()
        if len(linea_limpia) > 5:
            return limpiar_markdown(linea_limpia)
    return "Dios es fiel."


def crear_imagen_versiculo(texto_versiculo, ancho=1080, alto=1080):
    imagen = Image.new("RGB", (ancho, alto), color=(20, 30, 60))
    dibujo = ImageDraw.Draw(imagen)

    try:
        fuente = ImageFont.truetype(
            "/System/Library/Fonts/Supplemental/Georgia.ttf", 54
        )
    except Exception:
        fuente = ImageFont.load_default()

    texto_envuelto = textwrap.fill(texto_versiculo, width=28)
    lineas = texto_envuelto.split("\n")

    alturas_linea = []
    for linea in lineas:
        bbox = dibujo.textbbox((0, 0), linea, font=fuente)
        alturas_linea.append(bbox[3] - bbox[1])

    alto_total = sum(alturas_linea) + (len(lineas) - 1) * 20
    y = (alto - alto_total) // 2

    for linea, alto_linea in zip(lineas, alturas_linea):
        bbox = dibujo.textbbox((0, 0), linea, font=fuente)
        ancho_linea = bbox[2] - bbox[0]
        x = (ancho - ancho_linea) // 2
        dibujo.text((x, y), linea, font=fuente, fill=(255, 215, 130))
        y += alto_linea + 20

    salida = io.BytesIO()
    imagen.save(salida, format="PNG")
    return salida.getvalue()


def acciones_respuesta(contenido, mensaje_id):
    col_pdf, col_docx, col_copiar, col_whatsapp, col_favorito = st.columns(5)

    with col_pdf:
        st.download_button(
            "📄 PDF",
            data=crear_pdf(contenido),
            file_name="rhema_contenido.pdf",
            mime="application/pdf",
            key=f"pdf_{mensaje_id}",
            use_container_width=True,
        )

    with col_docx:
        st.download_button(
            "📝 DOCX",
            data=crear_docx(contenido),
            file_name="rhema_contenido.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key=f"docx_{mensaje_id}",
            use_container_width=True,
        )

    with col_copiar:
        texto_json = json.dumps(contenido)

        components.html(
            f"""
            <button onclick="copiarTexto()" style="
                width: 100%;
                height: 38px;
                border-radius: 7px;
                border: 1px solid #d0d0d0;
                background: white;
                cursor: pointer;
                font-size: 14px;">
                📋 Copiar
            </button>

            <script>
                async function copiarTexto() {{
                    const texto = {texto_json};
                    try {{
                        await navigator.clipboard.writeText(texto);
                        document.querySelector("button").innerText = "✅ Copiado";
                    }} catch (error) {{
                        document.querySelector("button").innerText = "Error al copiar";
                    }}
                }}
            </script>
            """,
            height=42,
        )

    with col_whatsapp:
        texto_wp = urllib.parse.quote(contenido)
        link_wp = f"https://wa.me/?text={texto_wp}"
        st.markdown(
            f"""
            <a href="{link_wp}" target="_blank" style="
                display: flex;
                align-items: center;
                justify-content: center;
                width: 100%;
                height: 38px;
                border-radius: 7px;
                border: 1px solid #d0d0d0;
                background: white;
                color: black;
                text-decoration: none;
                font-size: 14px;">
                📲 WhatsApp
            </a>
            """,
            unsafe_allow_html=True,
        )

    with col_favorito:
        ya_es_favorito = any(
            favorito["id"] == mensaje_id
            for favorito in st.session_state.favoritos
        )

        texto_boton = "⭐ Guardado" if ya_es_favorito else "⭐ Favorito"

        if st.button(
            texto_boton,
            key=f"favorito_{mensaje_id}",
            use_container_width=True,
        ):
            if ya_es_favorito:
                st.session_state.favoritos = [
                    favorito
                    for favorito in st.session_state.favoritos
                    if favorito["id"] != mensaje_id
                ]
            else:
                titulo = next(
                    (
                        linea.strip()[:55]
                        for linea in contenido.splitlines()
                        if linea.strip()
                    ),
                    "Contenido de RHEMA",
                )

                st.session_state.favoritos.append({
                    "id": mensaje_id,
                    "titulo": titulo,
                    "contenido": contenido,
                })

            st.rerun()

    if st.session_state.get("modo_actual") == "Devocional Diario":
        versiculo = extraer_versiculo(contenido)
        imagen_bytes = crear_imagen_versiculo(versiculo)

        st.download_button(
            "🖼️ Descargar imagen del versículo",
            data=imagen_bytes,
            file_name="versiculo_rhema.png",
            mime="image/png",
            key=f"imagen_{mensaje_id}",
            use_container_width=True,
        )
#col1, col2, col3 = st.columns([1, 2, 1])
#with col2:
    #st.image("logo.png", use_container_width=True)


st.markdown("""
<style>
.st-key-caja_logo {
    background-color: #D4AF37;
    border-radius: 10px;
    padding: 12px 10px;
    margin-bottom: 8px;
}
.st-key-caja_logo img {
    display: block;
    margin: 0 auto;
}
.st-key-caja_logo div[data-testid="stAlert"] {
    background-color: #0B1E3F !important;
    border: 1px solid #0B1E3F !important;
}
.st-key-caja_logo div[data-testid="stAlert"] * {
    color: #F5E6C8 !important;
}
</style>
""", unsafe_allow_html=True)

if "modo_actual" not in st.session_state:
    st.session_state.modo_actual = list(MODOS.keys())[0]

modo_sidebar = st.session_state.modo_actual

with st.sidebar.container(key="caja_logo"):
    st.image("logo.png", width=90)
    st.info(f"Modo activo: **{modo_sidebar}**")

st.sidebar.markdown("---")
ICONOS_MODOS = {
    "Sermón": "🎙️",
    "Estudio Bíblico": "📖",
    "Oración": "🙏",
    "Consejería Pastoral": "🕊️",
    "Estudio para Mujeres": "👩",
    "Estudio para Hombres": "👨",
    "Estudio para Niños": "🧒",
    "Estudio para Jóvenes": "✨",
    "Matrimonios": "💍",
    "Células en Hogares": "🏠",
    "Multiplicación de Células": "🌱",
    "Biblia Inteligente IA": "🔎",
    "Asistente Escatológico IA": "🌙",
    "Asistente Teológico IA": "🎓",
    "Plan de Estudio Temático": "🗂️",
    "Series de Células (Multi-semana)": "📅",
    "Conferencias y Formación Avanzada": "🎤",
    "Guiones para Redes Sociales": "🎬",
        "Creador y Asistente de Libros": "📘",
    "Análisis Multicapa (Gematría Bíblica)": "🔢",
    "Devocional Diario": "🙏",
    "Boletín y Anuncios de Iglesia": "📢",
    "Manualidades y Actividades para Niños": "✂️",
    "Comparador de Versiones Bíblicas": "📚",
    "Gestión de Miembros y Asistencia": "👥",
    "Ofrendas y Finanzas": "💰",
    "Liderazgo Bíblico": "👑",
    "Reuniones de Equipo": "🗓️",
    "Podcast Evangelístico": "🎙️",
    "Matrimonio en Crecimiento": "💍",
}
st.markdown('<div class="rhema-seccion">¿Qué necesitas hoy?</div>', unsafe_allow_html=True)

if "modo_actual" not in st.session_state:
    st.session_state.modo_actual = list(MODOS.keys())[0]

# CSS para las tarjetas (solo dentro del contenedor de modos)
st.markdown("""
    <style>
    .st-key-grid_modos div.stButton > button {
        width: 100%;
        height: 96px;
        min-height: 96px;
        border-radius: 12px;
        border: 1px solid #D4AF37 !important;
        background-color: #FFFFFF !important;
        color: #0B1E3F !important;
        font-size: 11px;
        font-weight: 600;
        white-space: normal;
        overflow-wrap: break-word;
        word-break: break-word;
        padding: 6px;
        line-height: 1.25;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    .st-key-grid_modos div.stButton > button * {
        color: #0B1E3F !important;
    }
    .st-key-grid_modos div.stButton > button:hover {
        border: 2px solid #D4AF37 !important;
        background-color: #FFFFFF !important;
        color: #0B1E3F !important;
    }
    .st-key-grid_modos div.stButton > button:hover * {
        color: #0B1E3F !important;
    }
    .st-key-grid_modos div.stButton > button[kind="primary"] {
        background-color: #D4AF37 !important;
        color: #0B1E3F !important;
        border: 2px solid #0B1E3F !important;
    }
    .st-key-grid_modos div.stButton > button[kind="primary"] *,
    .st-key-grid_modos div.stButton > button[kind="primary"]:hover,
    .st-key-grid_modos div.stButton > button[kind="primary"]:hover * {
        color: #0B1E3F !important;
        background-color: #D4AF37 !important;
    }
    </style>
""", unsafe_allow_html=True)

nombres_modos = list(MODOS.keys())
columnas_por_fila = 6

with st.container(key="grid_modos"):
    idx_global = 0
    for i in range(0, len(nombres_modos), columnas_por_fila):
        fila = nombres_modos[i:i + columnas_por_fila]
        cols = st.columns(columnas_por_fila)
        for col, nombre_modo in zip(cols, fila):
            icono = ICONOS_MODOS.get(nombre_modo, "")
            es_activo = st.session_state.modo_actual == nombre_modo
            activo = "✅ " if es_activo else ""
            with col:
                if st.button(
                    f"{activo}{icono} {nombre_modo}",
                    key=f"btn_modo_{idx_global}",
                    type="primary" if es_activo else "secondary",
                ):
                    st.session_state.modo_actual = nombre_modo
                    st.rerun()
            idx_global += 1

modo = st.session_state.modo_actual
st.markdown(f"### Modo actual: {ICONOS_MODOS.get(modo,'')} {modo}")
st.divider()

if st.sidebar.button("🗑️ Nueva conversación"):
    st.session_state.messages = []
    st.rerun()

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

if "prompts_guardados" not in st.session_state:
    st.session_state.prompts_guardados = []
if "favoritos" not in st.session_state:
    st.session_state.favoritos = []
st.sidebar.markdown("---")
st.sidebar.subheader("⭐ Mis Prompts Guardados")
st.sidebar.markdown("---")
st.sidebar.subheader("⭐ Mis Favoritos")

if not st.session_state.favoritos:
    st.sidebar.caption("Todavía no tienes contenidos favoritos.")
else:
    for favorito in st.session_state.favoritos:
        with st.sidebar.expander(f"⭐ {favorito['titulo']}"):
            st.write(favorito["contenido"])
nuevo_nombre = st.sidebar.text_input("Nombre del prompt", key="nuevo_prompt_nombre")
nuevo_texto = st.sidebar.text_area("Texto del prompt", key="nuevo_prompt_texto")

if st.sidebar.button("💾 Guardar prompt"):
    if nuevo_nombre and nuevo_texto:
        st.session_state.prompts_guardados.append({"nombre": nuevo_nombre, "texto": nuevo_texto})
        st.rerun()

for i, p in enumerate(st.session_state.prompts_guardados):
    col1, col2 = st.sidebar.columns([4, 1])
    if col1.button(f"📌 {p['nombre']}", key=f"prompt_guardado_{i}"):
        st.session_state.pending_prompt = p["texto"]
    if col2.button("🗑️", key=f"borrar_prompt_{i}"):
        st.session_state.prompts_guardados.pop(i)
        st.rerun()

if "modo_previo" not in st.session_state:
    st.session_state.modo_previo = modo

if modo != st.session_state.modo_previo or "messages" not in st.session_state or not st.session_state.messages:
    system_content = BASE_PROMPT + MODOS[modo]
    st.session_state.messages = [{"role": "system", "content": system_content}]
    st.session_state.modo_previo = modo
if st.session_state.get("modo_actual") != modo:
    system_content = BASE_PROMPT + MODOS[modo]
    st.session_state.messages[0] = {"role": "system", "content": system_content}
    st.session_state.modo_actual = modo
if modo == "Sermón":
    tab_generar_sermon, tab_series_sermon, tab_historial_sermon = st.tabs([
        "✨ Generar Sermón",
        "📚 Series de Sermones",
        "📂 Historial de Sermones"
    ])

    with tab_generar_sermon:
        st.markdown("#### ✨ Sugerencia automática de pasaje y objetivo")
        tema_sugerencia_sermon = st.text_input(
            "Escribe el tema y la IA sugerirá el pasaje bíblico y el objetivo",
            key="tema_sermon_sugerencia",
            placeholder="Ej: La gracia de Dios"
        )
        if st.button("🔍 Sugerir pasaje bíblico y objetivo", key="btn_sugerir_sermon"):
            if tema_sugerencia_sermon.strip():
                prompt_sugerencia_sermon = f"""Eres un asistente pastoral experto en homilética y exégesis bíblica.

    Tema: {tema_sugerencia_sermon}

    Sugiere:
    1. Un pasaje bíblico (libro, capítulo y versículo) que se conecte claramente con este tema. No inventes citas textuales; usa una referencia real y coherente con el tema.
    2. Un objetivo claro y conciso para un sermón basado en ese pasaje y tema (una sola oración, orientado a la transformación o aplicación práctica).

    Responde ÚNICAMENTE en este formato exacto, sin texto adicional:
    Pasaje: <referencia>
    Objetivo: <objetivo>"""
                try:
                    with st.spinner("Buscando pasaje y objetivo sugeridos..."):
                        resultado_sugerencia_sermon = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "Eres un asistente pastoral experto en homilética y estructura de sermones."},
                                {"role": "user", "content": prompt_sugerencia_sermon}
                            ]
                        ).choices[0].message.content

                    pasaje_sugerido_sermon = ""
                    objetivo_sugerido_sermon = ""
                    for linea in resultado_sugerencia_sermon.splitlines():
                        if linea.lower().startswith("pasaje:"):
                            pasaje_sugerido_sermon = linea.split(":", 1)[1].strip()
                        elif linea.lower().startswith("objetivo:"):
                            objetivo_sugerido_sermon = linea.split(":", 1)[1].strip()

                    st.session_state["sermon_tema_prefill"] = tema_sugerencia_sermon
                    st.session_state["sermon_texto_prefill"] = pasaje_sugerido_sermon
                    st.session_state["sermon_objetivo_prefill"] = objetivo_sugerido_sermon
                    st.success("Sugerencia generada. Revisa el formulario debajo para confirmarla o ajustarla.")
                except Exception as e:
                    st.error(f"No se pudo generar la sugerencia: {e}")
            else:
                st.warning("Escribe un tema antes de solicitar la sugerencia.")

        with st.expander("🎤 Generador de Sermones IA (formulario especializado)", expanded=False):
            with st.form("form_sermon"):
                col1, col2 = st.columns(2)
                with col1:
                    tema = st.text_input(
                        "Tema",
                        value=st.session_state.get("sermon_tema_prefill", ""),
                        placeholder="Ej: La gracia de Dios"
                    )
                    tipo_sermon = st.selectbox("Tipo de sermón", [
                        "Expositivo",
                        "Temático",
                        "Textual",
                        "Profético",
                        "Narrativo/Ilustrativo",
                        "Apologético",
                        "Doctrinal",
                        "Evangelístico",
                        "Pastoral/Consejería",
                        "Celebrativo (bodas, funerales, etc.)",
                    ])
                    duracion = st.selectbox("Duración prevista", [
                        "15-20 minutos",
                        "20-30 minutos",
                        "30-40 minutos",
                        "40-60 minutos",
                    ])
                    objetivo = st.text_input(
                        "Objetivo",
                        value=st.session_state.get("sermon_objetivo_prefill", ""),
                        placeholder="Ej: Conducir al arrepentimiento"
                    )
                with col2:
                    texto_biblico = st.text_input(
                        "Texto bíblico",
                        value=st.session_state.get("sermon_texto_prefill", ""),
                        placeholder="Ej: Efesios 2:1-10"
                    )
                    publico = st.selectbox("Público", [
                        "Congregación general",
                        "Jóvenes",
                        "Niños",
                        "Nuevos creyentes",
                        "Líderes / Ministerio",
                        "Hombres",
                        "Mujeres",
                        "Matrimonios",
                    ])
                    nivel = st.selectbox("Nivel de profundidad", [
                        "Básico",
                        "Medio",
                        "Avanzado",
                        "Académico",
                    ])

                enviado = st.form_submit_button("✨ Generar sermón")

            if enviado:
                if tema:
                    prompt_sermon = f"""Genera un sermón completo con los siguientes parámetros:

    - Tema: {tema}
    - Texto bíblico: {texto_biblico or 'elige el más adecuado según el tema'}
    - Tipo de sermón: {tipo_sermon}
    - Público: {publico}
    - Duración prevista: {duracion}
    - Nivel de profundidad: {nivel}
    - Objetivo: {objetivo or 'no especificado, usa tu criterio pastoral'}

    Ten en cuenta el nivel de profundidad indicado: si es "Básico" usa lenguaje sencillo y ejemplos cotidianos; si es "Medio" incluye algo de contexto bíblico; si es "Avanzado" profundiza en el idioma original y contexto histórico; si es "Académico" incluye referencias exegéticas y teológicas más rigurosas.

    Independientemente del nivel elegido, incluye SIEMPRE una sección de contexto histórico, cultural y hebreo/judío del pasaje o tema, con estos elementos quando aplique:
    - Marco histórico y político de la época (situación bajo el Imperio Romano, autoridades religiosas judías, etc.).
    - Costumbres, tradiciones y estructura social judía relevantes al pasaje (sinagoga, sanedrín, fariseos, saduceos, templo, pureza ritual, fiestas judías, etc.).
    - Trasfondo veterotestamentario (Antiguo Testamento) que ilumine el texto: personajes, leyes, profecías o eventos conectados.
    - Significado de palabras o expresiones clave en hebreo o arameo original cuando enriquezcan la comprensión del texto (explica el término, su transliteración simple y su significado, sin inventar etimologías).
    - Cómo pensaban y vivían los judíos de esa época en relación al tema tratado (expectativas mesiánicas, relación con Dios, vida comunitaria, etc.).

    Integra este contexto de forma natural dentro del desarrollo del sermón (no como una nota aparte y desconectada), de manera que enriquezca la comprensión del pasaje sin convertirse en una clase académica aislada del mensaje espiritual. No inventes citas, datos históricos ni afirmaciones que no puedas sustentar con razonable certeza.

    Genera el sermón completo, listo para predicar, siguiendo la estructura del modo Sermón."""
                    st.session_state["sermon_pendiente_meta"] = {
                        "tema": tema,
                        "texto_biblico": texto_biblico,
                        "tipo": tipo_sermon,
                        "publico": publico,
                        "duracion": duracion,
                        "nivel": nivel,
                        "objetivo": objetivo,
                    }
                    st.session_state.pending_prompt = prompt_sermon
                    st.rerun()
                else:
                    st.warning("Por favor completa al menos el campo Tema.")

    with tab_series_sermon:
        st.markdown("## 📚 Generador de Series de Sermones")
        st.caption(
            "Crea una serie completa. Cada sermón incluirá estructura homilética "
            "y las 20 capas del Análisis Multicapa."
        )

        with st.form("form_serie_sermon"):
            nombre_serie = st.text_input(
                "Nombre o tema de la serie",
                placeholder="Ej: Caminando por el Evangelio de Juan"
            )

            col1, col2 = st.columns(2)

            with col1:
                libro_o_tema_serie = st.text_input(
                    "Libro bíblico o enfoque principal",
                    placeholder="Ej: Efesios, El fruto del Espíritu, La vida de David"
                )

                cantidad_sermones_serie = st.selectbox(
                    "Cantidad de sermones",
                    [2, 3, 4, 5, 6],
                    index=2
                )

                tipo_serie_sermon = st.selectbox(
                    "Tipo de serie",
                    [
                        "Expositiva por libro bíblico",
                        "Temática",
                        "Doctrinal",
                        "Evangelística",
                        "Profética",
                        "Para discipulado",
                        "Para jóvenes",
                        "Para familias",
                    ]
                )

            with col2:
                publico_serie_sermon = st.selectbox(
                    "Público",
                    [
                        "Congregación general",
                        "Jóvenes",
                        "Niños",
                        "Nuevos creyentes",
                        "Líderes / Ministerio",
                        "Hombres",
                        "Mujeres",
                        "Matrimonios",
                    ]
                )

                duracion_serie_sermon = st.selectbox(
                    "Duración estimada por sermón",
                    [
                        "15-20 minutos",
                        "20-30 minutos",
                        "30-40 minutos",
                        "40-60 minutos",
                    ]
                )

                nivel_serie_sermon = st.selectbox(
                    "Nivel de profundidad",
                    ["Básico", "Medio", "Avanzado", "Académico"]
                )

            objetivo_serie_sermon = st.text_area(
                "Objetivo general de la serie",
                placeholder=(
                    "Ej: Guiar a la congregación a comprender y vivir "
                    "la gracia de Dios en su vida diaria."
                )
            )

            enviado_serie = st.form_submit_button(
                "✨ Generar serie completa con 20 capas"
            )

        if enviado_serie:
            if nombre_serie.strip() and libro_o_tema_serie.strip():
                prompt_serie_sermon = f"""Eres un pastor, homileta y estudioso bíblico experto.
Genera una SERIE COMPLETA DE SERMONES, lista para predicar, siguiendo cuidadosamente
las instrucciones siguientes.

DATOS DE LA SERIE:
- Nombre de la serie: {nombre_serie}
- Libro bíblico o enfoque: {libro_o_tema_serie}
- Cantidad de sermones: {cantidad_sermones_serie}
- Tipo de serie: {tipo_serie_sermon}
- Público: {publico_serie_sermon}
- Duración estimada por sermón: {duracion_serie_sermon}
- Nivel de profundidad: {nivel_serie_sermon}
- Objetivo general: {objetivo_serie_sermon or 'Usa un objetivo pastoral adecuado según el tema.'}

PRIMERO, incluye:
# Información general de la serie
- Nombre de la serie
- Idea central
- Objetivo general
- Público objetivo
- Orden sugerido de predicación
- Recomendación pastoral para conectar cada sermón con el siguiente

DESPUÉS, desarrolla cada sermón de forma separada, usando este formato:

# Sermón 1: <título>
- Texto bíblico principal
- Tema
- Objetivo específico
- Idea central
- Bosquejo homilético completo: introducción, puntos principales, ilustraciones,
  transiciones, aplicación y conclusión.
- Llamado final u oración.

Luego incluye obligatoriamente las siguientes 20 capas para ESE sermón,
con títulos numerados exactamente en este orden:

1. Texto literal (traducción directa o sentido fiel del pasaje)
2. Contexto histórico-cultural
3. Contexto literario (género, autor y propósito del libro)
4. Análisis gramatical del idioma original (hebreo o griego según corresponda)
5. Etimología de las palabras clave en el idioma original
6. Gematría hebrea o Isopsefía griega: explica con prudencia; para palabras clave,
   muestra letras, valores numéricos y suma solamente cuando sea verificable.
7. Paralelismos y estructuras quiásticas
8. Referencias cruzadas bíblicas relacionadas
9. Tipología (si aplica)
10. Sentido profético (si aplica)
11. Sentido mesiánico
12. Sentido moral y ético
13. Sentido devocional y personal
14. Sentido eclesiológico (aplicación para la iglesia)
15. Sentido escatológico (si aplica)
16. Simbolismo numérico bíblico general
17. Nombres de Dios mencionados o implícitos
18. Estructura poética (si aplica)
19. Aplicación práctica para hoy
20. Oración o reflexión final breve

Repite esa estructura para cada sermón de la serie.

REGLAS IMPORTANTES:
- No inventes citas bíblicas, palabras originales, significados, valores numéricos
  ni datos históricos.
- Si una capa no aplica claramente al pasaje, indícalo con honestidad y explica
  brevemente por qué.
- La gematría y la isopsefía deben tratarse como herramientas secundarias de
  estudio y meditación, nunca como fundamento doctrinal.
- Ajusta la profundidad al nivel solicitado.
- Mantén el contenido pastoral, bíblicamente responsable y listo para predicar.
- Al final de toda la serie agrega esta nota:
  "Nota: Este análisis, especialmente las secciones de Gematría o Isopsefía,
  es una herramienta de estudio y meditación. Verifica datos lingüísticos,
  históricos y cálculos numéricos antes de usarlos como base doctrinal en una prédica."
"""

                st.session_state["serie_sermon_pendiente_meta"] = {
                    "nombre": nombre_serie,
                    "libro_o_tema": libro_o_tema_serie,
                    "cantidad_sermones": cantidad_sermones_serie,
                    "tipo": tipo_serie_sermon,
                    "publico": publico_serie_sermon,
                    "duracion": duracion_serie_sermon,
                    "nivel": nivel_serie_sermon,
                    "objetivo": objetivo_serie_sermon,
                }

                st.session_state.pending_prompt = prompt_serie_sermon
                st.rerun()
            else:
                st.warning(
                    "Completa al menos el nombre de la serie y el libro bíblico o enfoque principal."
                )

        st.markdown("---")
        st.markdown("### 💾 Series guardadas")

        series_guardadas = cargar_datos_json(SERIES_SERMONES_FILE)

        if not series_guardadas:
            st.info("Aún no has generado ninguna serie de sermones.")
        else:
            busqueda_serie = st.text_input(
                "🔎 Buscar serie por nombre, libro o tema",
                key="busqueda_series_sermon"
            )

            series_filtradas = series_guardadas

            if busqueda_serie:
                termino_serie = busqueda_serie.lower()
                series_filtradas = [
                    serie for serie in series_guardadas
                    if termino_serie in serie.get("nombre", "").lower()
                    or termino_serie in serie.get("libro_o_tema", "").lower()
                ]

            if not series_filtradas:
                st.warning("No se encontraron series con ese criterio.")
            else:
                for serie in reversed(series_filtradas):
                    titulo_serie = (
                        f"📚 {serie.get('nombre', 'Serie sin nombre')} "
                        f"— {serie.get('fecha', '')}"
                    )

                    with st.expander(titulo_serie):
                        st.markdown(
                            f"**Libro o tema:** {serie.get('libro_o_tema') or 'No especificado'}"
                        )
                        st.markdown(
                            f"**Cantidad de sermones:** {serie.get('cantidad_sermones', '')}"
                        )
                        st.markdown(f"**Tipo:** {serie.get('tipo', '')}")
                        st.markdown(f"**Público:** {serie.get('publico', '')}")
                        st.markdown(f"**Duración:** {serie.get('duracion', '')}")
                        st.markdown(f"**Nivel:** {serie.get('nivel', '')}")
                        st.markdown(
                            f"**Objetivo:** {serie.get('objetivo') or 'No especificado'}"
                        )
                        st.markdown("---")
                        st.markdown(serie.get("contenido", ""))

                        # ── Desarrollo con IA de un sermón de la serie ──
                        cantidad = serie.get("cantidad_sermones", "10")
                        try:
                            total_sermones = int(cantidad)
                        except (TypeError, ValueError):
                            total_sermones = 10

                        opciones_sermon = list(range(1, total_sermones + 1))
                        numero_sermon = st.selectbox(
                            "Selecciona el sermón que deseas desarrollar",
                            opciones_sermon,
                            format_func=lambda n: f"Sermón {n}",
                            key=f"selector_sermon_ia_{serie['id']}"
                        )

                        clave_respuesta_serie = (
                            f"desarrollo_serie_{serie['id']}_{numero_sermon}"
                        )

                        if st.button(
                            "🤖 Desarrollar sermón con IA",
                            key=f"btn_desarrollar_serie_{serie['id']}_{numero_sermon}",
                            use_container_width=True
                        ):
                            contenido_serie = serie.get("contenido", "")
                            marca_inicio = f"SERMÓN {numero_sermon}:"

                            if marca_inicio not in contenido_serie:
                                st.warning(
                                    "No se encontró el bosquejo de este sermón dentro de la serie."
                                )
                            else:
                                bloque_sermon = contenido_serie.split(
                                    marca_inicio, 1
                                )[1]

                                # Corta el contenido al comenzar el sermón siguiente.
                                for siguiente in range(numero_sermon + 1, total_sermones + 1):
                                    marca_siguiente = f"SERMÓN {siguiente}:"
                                    if marca_siguiente in bloque_sermon:
                                        bloque_sermon = bloque_sermon.split(
                                            marca_siguiente, 1
                                        )[0]
                                        break

                                bosquejo_sermon = marca_inicio + bloque_sermon

                                prompt = f"""Actúa como un pastor, maestro bíblico y predicador cristiano responsable.

Desarrolla un sermón completo en español basado exclusivamente en el siguiente bosquejo de una serie.

Serie: {serie.get('nombre', 'Serie de sermones')}
Sermón seleccionado: {numero_sermon}
Público: {serie.get('publico', 'Iglesia general')}
Duración objetivo: {serie.get('duracion', '30-45 min')}
Nivel: {serie.get('nivel', 'Avanzado')}

BOSQUEJO BASE:
{bosquejo_sermon}

Entrega un sermón listo para predicar que incluya:
1. Título y texto bíblico principal.
2. Introducción atractiva y fiel al contexto.
3. Contexto histórico y bíblico relevante del pasaje (marco general del libro de Hechos, situación política y religiosa de la época).
4. Contexto histórico, cultural y hebreo/judío específico:
   - Costumbres, tradiciones y estructura social judía relevantes al pasaje.
   - Trasfondo veterotestamentario (Antiguo Testamento) que ilumina el texto: personajes, leyes, profecías o eventos previos conectados.
   - Significado de términos o expresiones hebreas/arameas clave si aplica (aunque Hechos esté en griego, muchos conceptos y personajes tienen raíz hebrea que conviene explicar: por ejemplo, sinagoga, sanedrín, fariseos, saduceos, kashrut, shaliaj, etc.)
   - Cómo pensaban y vivían los judíos de esa época (relación con Roma, expectativas mesiánicas, pureza ritual, el templo, la diáspora).
5. Desarrollo claro de cada punto del bosquejo, integrando el contexto histórico-cultural de forma natural (no como bloque aparte y aburrido, sino tejido dentro de la enseñanza).
6. Explicación bíblica responsable, sin inventar citas, datos ni afirmaciones históricas no verificables.
7. Ilustraciones o ejemplos pastorales prácticos cuando sean apropiados.
8. Aplicaciones concretas para la iglesia actual.
9. Conclusión con llamado pastoral.
10. Oración final breve.

Usa Markdown con títulos y subtítulos. Mantén un tono cristocéntrico, bíblico, pastoral y esperanzador. El contexto histórico-cultural-hebreo debe enriquecer la comprensión del pasaje, no convertirse en una clase académica aislada del mensaje espiritual."""

                                try:
                                    with st.spinner(
                                        "La IA está desarrollando el sermón..."
                                    ):
                                        respuesta = client.chat.completions.create(
                                            model="gpt-4o-mini",
                                            messages=[
                                                {
                                                    "role": "system",
                                                    "content": (
                                                        "Eres un pastor y maestro bíblico "
                                                        "evangélico, responsable, profundo, "
                                                        "claro y fiel a las Escrituras."
                                                    )
                                                },
                                                {"role": "user", "content": prompt}
                                            ]
                                        ).choices[0].message.content

                                    st.session_state[clave_respuesta_serie] = respuesta

                                except Exception as e:
                                    st.error(
                                        f"No se pudo desarrollar el sermón con IA: {e}"
                                    )

                        if st.session_state.get(clave_respuesta_serie):
                            st.markdown("---")
                            st.markdown(
                                f"## 🤖 Sermón {numero_sermon} desarrollado con IA"
                            )
                            st.markdown(
                                st.session_state[clave_respuesta_serie]
                            )

                        if st.button(
                            "🗑️ Eliminar esta serie",
                            key=f"eliminar_serie_{serie['id']}"
                        ):
                            series_guardadas = [
                                s for s in series_guardadas
                                if s["id"] != serie["id"]
                            ]
                            guardar_datos_json(
                                SERIES_SERMONES_FILE,
                                series_guardadas
                            )
                            st.rerun()


    with tab_historial_sermon:
        sermones_guardados = cargar_datos_json(SERMONES_FILE)

        if not sermones_guardados:
            st.info("Aún no has generado ningún sermón.")
        else:
            busqueda_sermon = st.text_input(
                "🔎 Buscar por tema o texto bíblico",
                key="busqueda_historial_sermon"
            )

            sermones_filtrados = sermones_guardados
            if busqueda_sermon:
                termino = busqueda_sermon.lower()
                sermones_filtrados = [
                    s for s in sermones_guardados
                    if termino in s.get("tema", "").lower()
                    or termino in s.get("texto_biblico", "").lower()
                ]

            if not sermones_filtrados:
                st.warning("No se encontraron sermones con ese criterio.")
            else:
                for sermon in reversed(sermones_filtrados):
                    titulo_expander = f"🎤 {sermon.get('tema', 'Sin tema')} — {sermon.get('fecha', '')}"
                    with st.expander(titulo_expander):
                        st.markdown(f"**Texto bíblico:** {sermon.get('texto_biblico') or 'No especificado'}")
                        st.markdown(f"**Tipo:** {sermon.get('tipo', '')}")
                        st.markdown(f"**Público:** {sermon.get('publico', '')}")
                        st.markdown(f"**Duración:** {sermon.get('duracion', '')}")
                        st.markdown(f"**Nivel:** {sermon.get('nivel', '')}")
                        st.markdown(f"**Objetivo:** {sermon.get('objetivo') or 'No especificado'}")
                        st.markdown("---")
                        st.markdown(sermon.get("contenido", ""))

                        if st.button("🗑️ Eliminar este sermón", key=f"eliminar_sermon_{sermon['id']}"):
                            sermones_guardados = [
                                s for s in sermones_guardados if s["id"] != sermon["id"]
                            ]
                            guardar_datos_json(SERMONES_FILE, sermones_guardados)
                            st.rerun()


if modo == "Análisis Multicapa (Gematría Bíblica)":
    with st.expander("🔢 Análisis Multicapa IA (formulario especializado)", expanded=False):
        with st.form("form_gematria"):
            versiculo_gematria = st.text_input("Versículo o pasaje", placeholder="Ej: Juan 3:16")
            enfoque_gematria = st.selectbox("Enfoque especial (opcional)", [
                "Análisis completo (las 20 capas)",
                "Enfocado en Gematría/Isopsefía",
                "Enfocado en sentido profético y mesiánico",
                "Enfocado en aplicación práctica y devocional",
                "Resumen para predicar (listo para Sermón)",
            ])
            enviado_gematria = st.form_submit_button("✨ Generar análisis")

        if enviado_gematria:
            if versiculo_gematria:
                prompt_gematria = f"""Realiza el análisis multicapa (incluyendo Gematría) del siguiente pasaje:

- Pasaje: {versiculo_gematria}
- Enfoque solicitado: {enfoque_gematria}

Sigue la estructura de las 20 capas del modo Análisis Multicapa. Si el enfoque solicitado no es "Análisis completo", desarrolla todas las capas brevemente pero profundiza especialmente en las capas relacionadas con el enfoque indicado."""
                st.session_state.pending_prompt = prompt_gematria
                st.rerun()
            else:
                st.warning("Por favor ingresa un versículo o pasaje.")
if modo == "Guiones para Redes Sociales":
    with st.expander("🎬 Generador de Guiones para Redes (formulario especializado)", expanded=False):
        with st.form("form_guion"):
            tema_guion = st.text_input("Versículo o tema", placeholder="Ej: Filipenses 4:13")
            col1, col2 = st.columns(2)
            with col1:
                duracion_guion = st.selectbox("Duración del video", [
                    "15 segundos",
                    "30 segundos",
                    "60 segundos",
                ])
            with col2:
             plataforma_guion = st.selectbox("Plataforma", [
    "TikTok",
    "Instagram Reels",
    "YouTube Shorts",
    "Facebook Reels",
])

            enviado_guion = st.form_submit_button("✨ Generar guion")

        if enviado_guion:
            if tema_guion:
                prompt_guion = f"""Genera un guion para video de redes sociales con estos parámetros:

- Versículo o tema: {tema_guion}
- Duración: {duracion_guion}
- Plataforma: {plataforma_guion}

Sigue la estructura del modo Guiones para Redes Sociales."""
                st.session_state.pending_prompt = prompt_guion
                st.rerun()
            else:
                st.warning("Por favor completa el campo del versículo o tema.")
if modo == "Conferencias y Formación Avanzada":
    with st.expander("🎓 Generador de Conferencias (formulario especializado)", expanded=False):
        with st.form("form_conferencia"):
            tema_conf = st.text_input("Tema o versículo", placeholder="Ej: La fe que mueve montañas")
            col1, col2 = st.columns(2)
            with col1:
                duracion_conf = st.selectbox("Duración", [
                    "30 minutos",
                    "45 minutos",
                    "60 minutos",
                ])
            with col2:
                incluir_folletos = st.selectbox("¿Incluir folletos por audiencia?", [
                    "Sí",
                    "No",
                ])

            enviado_conf = st.form_submit_button("✨ Generar conferencia")

        if enviado_conf:
            if tema_conf:
                prompt_conf = f"""Genera una conferencia completa con estos parámetros:

- Tema o versículo: {tema_conf}
- Duración: {duracion_conf}
- Incluir folletos segmentados por audiencia: {incluir_folletos}

Si "Incluir folletos" es "No", omite la sección de folletos y enfócate solo en el esquema completo de la conferencia.

Sigue la estructura del modo Conferencias y Formación Avanzada."""
                st.session_state.pending_prompt = prompt_conf
                st.rerun()
            else:
                st.warning("Por favor completa el campo del tema o versículo.")
if modo in ["Estudio Bíblico", "Estudio para Mujeres", "Estudio para Hombres", "Matrimonios"]:
    with st.expander(f"📖 Generador de {modo} (formulario especializado)", expanded=False):
        personaje_estudio = None
        if modo in ["Estudio para Mujeres", "Estudio para Hombres"]:
            lista_personajes_sel = MUJERES_BIBLIA if modo == "Estudio para Mujeres" else HOMBRES_BIBLIA
            personaje_estudio = st.selectbox(
                "Personaje bíblico (opcional)",
                ["-- Ninguno / tema libre --"] + lista_personajes_sel,
                key=f"personaje_estudio_select_{modo}",
            )
        with st.form("form_estudio"):
            pasaje_estudio = st.text_input("Pasaje bíblico", placeholder="Ej: Juan 15:1-8")
            tema_estudio = st.text_input("Tema o enfoque (opcional)", placeholder="Ej: Permanecer en Cristo")
            nivel_estudio = st.selectbox("Nivel de profundidad", [
                "Básico",
                "Medio",
                "Avanzado",
            ])

            incluir_dinamica_estudio = False
            if modo in ["Estudio para Mujeres", "Estudio para Hombres"]:
                incluir_dinamica_estudio = st.checkbox("🎲 Incluir dinámica de conexión (rompehielos)")

            enviado_estudio = st.form_submit_button("✨ Generar estudio")

        if enviado_estudio:
            personaje_valido = personaje_estudio and personaje_estudio != "-- Ninguno / tema libre --"
            if pasaje_estudio or tema_estudio or personaje_valido:
                linea_personaje = f"- Personaje bíblico a estudiar: {personaje_estudio}\n" if personaje_valido else ""
                linea_dinamica = "\nIncluye al inicio una dinámica de conexión (rompehielos) breve y apropiada para el grupo, antes de comenzar el estudio." if incluir_dinamica_estudio else ""
                prompt_estudio = f"""Genera un estudio bíblico con estos parámetros:

{linea_personaje}- Pasaje bíblico: {pasaje_estudio or 'elige el más adecuado según el personaje o tema'}
- Tema o enfoque: {tema_estudio or 'no especificado, usa tu criterio según el pasaje o personaje'}
- Nivel de profundidad: {nivel_estudio}

Ten en cuenta el nivel de profundidad: si es "Básico" usa lenguaje sencillo y ejemplos cotidianos; si es "Medio" incluye algo de contexto histórico; si es "Avanzado" profundiza en el idioma original y contexto teológico.
{linea_dinamica}
Sigue la estructura del modo {modo}."""
                st.session_state.pending_prompt = prompt_estudio
                if personaje_valido:
                    marcar_personaje_estudiado(personaje_estudio, modo)
                st.rerun()
            else:
                st.warning("Por favor completa al menos el pasaje bíblico, el tema o selecciona un personaje.")

if modo in ["Estudio para Mujeres", "Estudio para Hombres"]:
    grupo_evento = "mujeres" if modo == "Estudio para Mujeres" else "hombres"
    with st.expander("🎉 Ideas para Eventos de Evangelización y Conexión", expanded=False):
        st.caption(
            f"Genera ideas de eventos para el ministerio de {grupo_evento}, enfocados en "
            "evangelizar y conectar a nuevas personas para que se integren a la iglesia."
        )
        with st.form("form_evento_evangelismo"):
            tipo_evento = st.selectbox(
                "Tipo de evento",
                [
                    "Evento evangelístico (invitar no creyentes)",
                    "Evento de conexión / fraternidad (integrar nuevos miembros)",
                    "Servicio comunitario / acción social",
                    "Retiro o convivencia",
                    "Desayuno, brunch o cena especial",
                    "Otro (especificar en el tema)",
                ],
            )
            tema_evento = st.text_input(
                "Tema, ocasión o enfoque (opcional)",
                placeholder="Ej: Día de las madres, inicio de año, sanidad interior",
            )
            presupuesto_evento = st.selectbox(
                "Presupuesto disponible",
                ["Bajo (sencillo, bajo costo)", "Medio", "Alto (evento grande)"],
            )
            asistentes_evento = st.text_input(
                "Cantidad aproximada de asistentes (opcional)",
                placeholder="Ej: 20-30 personas",
            )
            enviado_evento = st.form_submit_button("✨ Generar ideas de evento")

        if enviado_evento:
            prompt_evento = f"""Genera ideas para un evento del ministerio de {grupo_evento} de la iglesia, con estos parámetros:

- Tipo de evento: {tipo_evento}
- Tema u ocasión: {tema_evento or 'libre, usa tu criterio'}
- Presupuesto: {presupuesto_evento}
- Asistentes aproximados: {asistentes_evento or 'no especificado'}

El objetivo principal es EVANGELIZAR e invitar a nuevas personas, y CONECTARLAS para que se animen a ser parte de nuestra iglesia.

Estructura la respuesta así:
1. Nombre creativo del evento
2. Objetivo del evento
3. Versículo o tema bíblico central
4. Actividades sugeridas (dinámicas, charlas, testimonios, juegos, etc.)
5. Ideas para romper el hielo con los invitados nuevos
6. Estrategia de seguimiento (cómo conectar a los nuevos después del evento para que se integren a la iglesia)
7. Lista básica de materiales o logística necesaria
8. Frase o mensaje de invitación para compartir en redes sociales o volantes"""
            st.session_state.pending_prompt = prompt_evento
            st.rerun()

        st.markdown("**💡 Ideas rápidas:**")
        col_ev1, col_ev2 = st.columns(2)
        with col_ev1:
            if st.button("🎉 Idea de evento evangelístico", key=f"idea_evang_{modo}"):
                st.session_state.pending_prompt = (
                    f"Dame 3 ideas creativas de eventos evangelísticos para el ministerio de {grupo_evento} "
                    "de la iglesia, pensados para invitar personas nuevas y que quieran integrarse. "
                    "Incluye nombre del evento, objetivo y actividades principales para cada idea."
                )
                st.rerun()
        with col_ev2:
            if st.button("🤝 Idea de evento de conexión", key=f"idea_conexion_{modo}"):
                st.session_state.pending_prompt = (
                    f"Dame 3 ideas creativas de eventos de conexión y fraternidad para el ministerio de {grupo_evento} "
                    "de la iglesia, pensados para que los nuevos miembros se sientan parte y se animen a integrarse. "
                    "Incluye nombre del evento, objetivo y actividades principales para cada idea."
                )
                st.rerun()

if modo == "Plan de Estudio Temático":
    with st.expander("📖 Generador de Plan de Estudio Temático (formulario especializado)", expanded=False):
        libro_plan_tematico = st.selectbox(
            "Libro de la Biblia (opcional, Génesis a Apocalipsis)",
            ["-- Ninguno / tema libre --"] + LIBROS_BIBLIA,
            key="libro_plan_tematico_select",
        )
        with st.form("form_plan_tematico"):
            tema_plan_tematico = st.text_input(
                "Tema o enfoque específico (opcional)",
                placeholder="Ej: Los frutos del Espíritu (Gálatas 5)",
            )
            col1, col2 = st.columns(2)
            with col1:
                nivel_plan_tematico = st.selectbox("Nivel de profundidad", [
                    "Básico",
                    "Medio",
                    "Avanzado",
                ])
            with col2:
                publico_plan_tematico = st.selectbox("Tipo de público", [
                    "General / congregación",
                    "Nuevos creyentes",
                    "Líderes y maestros",
                    "Jóvenes",
                    "Grupo pequeño / célula",
                ])
            duracion_plan_tematico = st.selectbox("Duración del plan", [
                "Estudio único (una sola sesión)",
                "4 semanas",
                "5 semanas",
                "6 semanas",
                "7 semanas",
                "8 semanas",
            ])
            enviado_plan_tematico = st.form_submit_button("✨ Generar con IA")

        if enviado_plan_tematico:
            libro_valido = libro_plan_tematico and libro_plan_tematico != "-- Ninguno / tema libre --"
            if tema_plan_tematico or libro_valido:
                es_plan_semanas = duracion_plan_tematico != "Estudio único (una sola sesión)"
                if es_plan_semanas:
                    instruccion_duracion = (
                        f"Este es un PLAN DE ESTUDIO DE {duracion_plan_tematico.upper()}: divide el tema en "
                        f"esa cantidad de semanas, con un hilo temático conductor que avance semana a semana. "
                        f"Para cada semana entrega: título, fundamento bíblico, raíces del idioma original "
                        f"(cuando aplique), aplicación práctica y preguntas de reflexión."
                    )
                else:
                    instruccion_duracion = "Genera un estudio único (una sola sesión), completo y profundo."

                if libro_valido and tema_plan_tematico:
                    desc_tema = f"El libro de {libro_plan_tematico}, con enfoque específico en: {tema_plan_tematico}"
                elif libro_valido:
                    desc_tema = f"El libro completo de {libro_plan_tematico} (elige los pasajes o secciones más relevantes según la duración indicada)"
                else:
                    desc_tema = tema_plan_tematico

                prompt_plan_tematico = f"""Genera un plan de estudio temático completo con estos parámetros:

- Tema del estudio: {desc_tema}
- Nivel de profundidad: {nivel_plan_tematico}
- Tipo de público: {publico_plan_tematico}
- Duración: {duracion_plan_tematico}

{instruccion_duracion}
Ten en cuenta el nivel de profundidad: si es "Básico" usa lenguaje sencillo y ejemplos cotidianos; si es "Medio" incluye algo de contexto histórico; si es "Avanzado" profundiza en el idioma original y contexto teológico.
Adapta el tono, el vocabulario y las preguntas de reflexión al tipo de público indicado.
Incluye introducción, desarrollo, aplicación y conclusión.

Sigue la estructura del modo Plan de Estudio Temático."""
                st.session_state.pending_prompt = prompt_plan_tematico
                st.rerun()
            else:
                st.warning("Por favor completa el tema del estudio o selecciona un libro de la Biblia.")
if modo in ["Estudio para Niños", "Estudio para Jóvenes"]:
    with st.expander(f"📖 Generador de {modo} (formulario especializado)", expanded=False):
        with st.form("form_bilingue"):
            pasaje_bilingue = st.text_input("Pasaje bíblico o tema", placeholder="Ej: David y Goliat")
            col1, col2 = st.columns(2)
            with col1:
                if modo == "Estudio para Niños":
                    edad_bilingue = st.selectbox("Edad", [
                        "4-6 años",
                        "7-9 años",
                        "10-12 años",
                    ])
                else:
                    edad_bilingue = st.selectbox("Edad", [
                        "13-15 años",
                        "16-18 años",
                        "19-25 años",
                    ])
            with col2:
                duracion_bilingue = st.selectbox("Duración", [
                    "20 minutos",
                    "30 minutos",
                    "45 minutos",
                ])

            incluir_dinamica_bilingue = st.checkbox("🎲 Incluir dinámica de conexión (rompehielos)")

            enviado_bilingue = st.form_submit_button("✨ Generar estudio")

        if enviado_bilingue:
            if pasaje_bilingue:
                linea_dinamica_bilingue = "\nIncluye al inicio una dinámica de conexión (rompehielos) breve y apropiada para la edad del grupo, antes de comenzar el estudio. Descríbela en español e inglés." if incluir_dinamica_bilingue else ""
                prompt_bilingue = f"""Genera un estudio bíblico bilingüe con estos parámetros:

- Pasaje bíblico o tema: {pasaje_bilingue}
- Edad: {edad_bilingue}
- Duración: {duracion_bilingue}
{linea_dinamica_bilingue}
Sigue la estructura del modo {modo} (formato bilingüe español/inglés)."""
                st.session_state.pending_prompt = prompt_bilingue
                st.rerun()
            else:
                st.warning("Por favor completa el pasaje bíblico o tema.")
SESIONES_FILE = "sesiones_consejeria.json"

def cargar_sesiones():
    if os.path.exists(SESIONES_FILE):
        with open(SESIONES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_sesion(nombre_persona, categoria, situacion, respuesta):
    sesiones = cargar_sesiones()
    sesiones.append({
        "nombre": nombre_persona,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "categoria": categoria,
        "situacion": situacion,
        "respuesta": respuesta,
    })
    with open(SESIONES_FILE, "w", encoding="utf-8") as f:
        json.dump(sesiones, f, ensure_ascii=False, indent=2)

def eliminar_sesion(indice):
    sesiones = cargar_sesiones()
    if 0 <= indice < len(sesiones):
        sesiones.pop(indice)
        with open(SESIONES_FILE, "w", encoding="utf-8") as f:
            json.dump(sesiones, f, ensure_ascii=False, indent=2)

def eliminar_sesiones_persona(nombre_persona):
    sesiones = cargar_sesiones()
    sesiones = [s for s in sesiones if s["nombre"] != nombre_persona]
    with open(SESIONES_FILE, "w", encoding="utf-8") as f:
        json.dump(sesiones, f, ensure_ascii=False, indent=2)

if modo in ["Oración", "Consejería Pastoral"]:
    etiqueta = "Motivo de oración" if modo == "Oración" else "Situación a tratar"
    with st.expander(f"🙏 Generador de {modo} (formulario especializado)", expanded=False):
        with st.form("form_oracion"):
            categoria_consejeria = None
            nombre_persona = None
            if modo == "Consejería Pastoral":
                nombre_persona = st.text_input("Nombre de la persona", placeholder="Ej: María G.")
                categoria_consejeria = st.selectbox("Categoría", [
                    "Matrimonio",
                    "Jóvenes / Adolescentes",
                    "Divorcio / Separación",
                    "Duelo / Pérdida",
                    "Familia / Hijos",
                    "Finanzas",
                    "Salud / Enfermedad",
                    "Depresión / Ansiedad",
                    "Propósito de vida / Vocación",
                    "Adicciones",
                    "Otro",
                ])
            situacion = st.text_area(etiqueta, placeholder="Ej: Sanidad para un familiar enfermo")

            enviado_oracion = st.form_submit_button("✨ Generar")

        if enviado_oracion:
            if situacion:
                if modo == "Oración":
                    prompt_oracion = f"""Genera una oración guiada para esta situación:

- Situación: {situacion}

Sigue la estructura del modo Oración (texto fluido, cálido, sin listas ni títulos)."""
                else:
                    if not nombre_persona:
                        nombre_persona = "Sin nombre"

                    sesiones_previas = [s for s in cargar_sesiones() if s["nombre"].strip().lower() == nombre_persona.strip().lower()]
                    contexto_previo = ""
                    if sesiones_previas:
                        resumen_previas = "\n".join([
                            f"- {s['fecha']} ({s['categoria']}): {s['situacion']}"
                            for s in sesiones_previas[-3:]
                        ])
                        contexto_previo = f"""

Historial de sesiones previas con esta persona:
{resumen_previas}

Ten en cuenta este historial para dar continuidad al consejo, si es relevante."""

                    prompt_oracion = f"""Genera consejería pastoral para esta situación:

- Persona: {nombre_persona}
- Categoría: {categoria_consejeria}
- Situación: {situacion}{contexto_previo}

Sigue la estructura del modo Consejería Pastoral, adaptando los versículos y consejos según la categoría indicada."""

                    st.session_state.guardar_sesion_pendiente = {
                        "nombre": nombre_persona,
                        "categoria": categoria_consejeria,
                        "situacion": situacion,
                    }
                st.session_state.pending_prompt = prompt_oracion
                st.rerun()
            else:
                st.warning("Por favor describe la situación.")
if modo in ["Células en Hogares", "Multiplicación de Células", "Series de Células (Multi-semana)"]:
    with st.expander(f"🏠 Generador de {modo} (formulario especializado)", expanded=False):
        with st.form("form_celulas"):
            tema_celula = st.text_input("Tema o pasaje bíblico", placeholder="Ej: El buen pastor")

            if modo == "Series de Células (Multi-semana)":
                col1, col2 = st.columns(2)
                with col1:
                    num_semanas = st.selectbox("Número de semanas", [
                        "4 semanas",
                        "6 semanas",
                        "8 semanas",
                    ])
                with col2:
                    duracion_celula = st.selectbox("Duración de cada reunión", [
                        "45 minutos",
                        "60 minutos",
                    ])
            else:
                duracion_celula = st.selectbox("Duración de la reunión", [
                    "45 minutos",
                    "60 minutos",
                ])
                num_semanas = None

            enviado_celula = st.form_submit_button("✨ Generar")

        if enviado_celula:
            if tema_celula:
                extra_semanas = f"- Número de semanas: {num_semanas}\n" if num_semanas else ""
                prompt_celula = f"""Genera contenido para células con estos parámetros:

- Tema o pasaje bíblico: {tema_celula}
{extra_semanas}- Duración de la reunión: {duracion_celula}

Sigue la estructura del modo {modo}."""
                st.session_state.pending_prompt = prompt_celula
                st.rerun()
            else:
                st.warning("Por favor completa el tema o pasaje bíblico.")           
if modo == "Asistente Escatológico IA":
    st.info(
        "Tu especialista en profecías bíblicas y eventos del fin de los tiempos. "
        "Pregunta cualquier cosa sobre Apocalipsis, Daniel, Arrebatamiento, Gran Tribulación, "
        "Anticristo, Falso Profeta, Milenio, Armagedón, Gog y Magog y otros temas proféticos."
    )

if modo == "Asistente Teológico IA":
    st.info(
        "Haz cualquier pregunta bíblica y recibe una respuesta teológica profunda."
    )

if modo == "Biblia Inteligente IA":
    st.info(
        "Busca un versículo, un capítulo, un libro, un tema bíblico o una palabra clave. "
        "La IA cita las Escrituras, explica y propone referencias cruzadas."
    )

if modo in SUGERENCIAS:
    st.markdown("**💡 Haz tu pregunta o elige una sugerencia:**")
    sugerencias_modo = SUGERENCIAS[modo]
    filas = [sugerencias_modo[i:i + 3] for i in range(0, len(sugerencias_modo), 3)]
    for fila_idx, fila in enumerate(filas):
        cols = st.columns(len(fila))
        for i, sugerencia in enumerate(fila):
            if cols[i].button(sugerencia, key=f"sugerencia_{modo}_{fila_idx}_{i}"):
                st.session_state.pending_prompt = sugerencia

if modo in BIBLIOTECA_PROFETICA:
    st.markdown("**📚 Biblioteca Profética:**")
    temas_biblioteca = BIBLIOTECA_PROFETICA[modo]
    filas_b = [temas_biblioteca[i:i + 5] for i in range(0, len(temas_biblioteca), 5)]
    for fila_idx, fila in enumerate(filas_b):
        cols_b = st.columns(len(fila))
        for i, tema in enumerate(fila):
            if cols_b[i].button(f"📖 {tema}", key=f"biblioteca_{modo}_{fila_idx}_{i}"):
                st.session_state.pending_prompt = f"Explica en profundidad el tema profético: {tema}"

if modo in TEMAS_POPULARES:
    st.markdown("**🔖 Temas Populares:**")
    temas_pop = TEMAS_POPULARES[modo]
    filas_t = [temas_pop[i:i + 5] for i in range(0, len(temas_pop), 5)]
    for fila_idx, fila in enumerate(filas_t):
        cols_t = st.columns(len(fila))
        for i, (emoji, tema) in enumerate(fila):
            if cols_t[i].button(f"{emoji} {tema}", key=f"tema_popular_{modo}_{fila_idx}_{i}"):
                st.session_state.pending_prompt = f"¿Qué dice la Biblia sobre {tema.lower()}? Cita versículos y explica."

if modo == "Consejería Pastoral":
    with st.expander("📋 Historial de Sesiones", expanded=False):
        sesiones = cargar_sesiones()
        if not sesiones:
            st.info("Aún no hay sesiones guardadas.")
        else:
            nombres = sorted(set(s["nombre"] for s in sesiones))
            persona_seleccionada = st.selectbox("Selecciona una persona", nombres, key="historial_persona")

            indices_persona = [i for i, s in enumerate(sesiones) if s["nombre"] == persona_seleccionada]
            indices_persona.sort(key=lambda i: sesiones[i]["fecha"], reverse=True)

            col_titulo, col_borrar_todo = st.columns([3, 1])
            with col_titulo:
                st.markdown(f"**{len(indices_persona)} sesión(es) con {persona_seleccionada}:**")
            with col_borrar_todo:
                if st.button("🗑️ Borrar todas", key="borrar_todas_persona"):
                    eliminar_sesiones_persona(persona_seleccionada)
                    st.success(f"Sesiones de {persona_seleccionada} eliminadas.")
                    st.rerun()

            for idx in indices_persona:
                s = sesiones[idx]
                with st.expander(f"🗓️ {s['fecha']} — {s['categoria']}"):
                    st.markdown(f"**Situación:** {s['situacion']}")
                    st.markdown("---")
                    st.markdown(s["respuesta"])
                    st.markdown("---")
                    if st.button("🗑️ Borrar esta sesión", key=f"borrar_sesion_{idx}"):
                        eliminar_sesion(idx)
                        st.success("Sesión eliminada.")
                        st.rerun()

if modo in ["Estudio para Mujeres", "Estudio para Hombres"]:
    with st.expander("📊 Progreso de Estudios por Personaje", expanded=False):
        lista_completa = MUJERES_BIBLIA if modo == "Estudio para Mujeres" else HOMBRES_BIBLIA
        estudios_todos = cargar_estudios_personajes()
        estudios_categoria = [e for e in estudios_todos if e["categoria"] == modo]
        personajes_estudiados = {e["personaje"]: e["fecha"] for e in estudios_categoria}

        total = len(lista_completa)
        hechos = len([p for p in lista_completa if p in personajes_estudiados])
        st.markdown(f"**Progreso: {hechos} / {total} personajes estudiados**")
        if total > 0:
            st.progress(hechos / total)

        col_check, col_borrar = st.columns([3, 1])
        with col_check:
            mostrar_pendientes = st.checkbox("Mostrar solo pendientes", key=f"pendientes_{modo}")
        with col_borrar:
            if st.button("🗑️ Reiniciar progreso", key=f"reset_progreso_{modo}"):
                estudios_restantes = [e for e in estudios_todos if e["categoria"] != modo]
                with open(ESTUDIOS_PERSONAJES_FILE, "w", encoding="utf-8") as f:
                    json.dump(estudios_restantes, f, ensure_ascii=False, indent=2)
                st.success(f"Progreso de {modo} reiniciado.")
                st.rerun()

        for personaje in lista_completa:
            if personaje in personajes_estudiados:
                if not mostrar_pendientes:
                    st.markdown(f"✅ **{personaje}** — estudiado el {personajes_estudiados[personaje]}")
            else:
                st.markdown(f"⬜ {personaje}")


if modo == "Gestión de Miembros y Asistencia":
    tab_miembros, tab_asistencia, tab_reportes_m = st.tabs(["Directorio de Miembros", "Tomar Asistencia", "Metricas y Cumpleanos"])
    miembros = cargar_datos_json(MIEMBROS_FILE)
    asistencias = cargar_datos_json(ASISTENCIAS_FILE)

    with tab_miembros:
        st.subheader("Directorio de Miembros")
        with st.expander("Registrar Nuevo Miembro", expanded=False):
            with st.form("form_nuevo_miembro"):
                col_nom, col_tel = st.columns(2)
                nombre = col_nom.text_input("Nombre completo *")
                telefono = col_tel.text_input("Telefono / WhatsApp")
                col_email, col_cumple = st.columns(2)
                email = col_email.text_input("Correo electronico")
                cumple = col_cumple.date_input("Fecha de nacimiento", value=datetime(1995, 1, 1), min_value=datetime(1920, 1, 1), max_value=datetime.today())
                col_min, col_rol = st.columns(2)
                ministerio = col_min.selectbox("Ministerio principal", ["Ninguno / General", "Alabanza", "Ujieres", "Ninos / Cuna", "Jovenes", "Matrimonios", "Intercesion", "Medios / Sonido", "Liderazgo"])
                estado = col_rol.selectbox("Estado", ["Activo", "En seguimiento", "Inactivo", "Nuevo creyente"])
                direccion = st.text_input("Direccion o barrio")
                guardar_m = st.form_submit_button("Guardar Miembro", use_container_width=True)
                if guardar_m:
                    if nombre.strip():
                        nuevo = {"id": str(uuid.uuid4())[:8], "nombre": nombre.strip(), "telefono": telefono.strip(), "email": email.strip(), "cumpleanos": cumple.strftime("%Y-%m-%d"), "ministerio": ministerio, "estado": estado, "direccion": direccion.strip(), "fecha_registro": datetime.now().strftime("%Y-%m-%d")}
                        miembros.append(nuevo)
                        guardar_datos_json(MIEMBROS_FILE, miembros)
                        st.success("Miembro guardado con exito!")
                        st.rerun()
                    else:
                        st.error("El nombre es obligatorio.")
        if miembros:
            filtro_busqueda = st.text_input("Buscar miembro por nombre, telefono o ministerio:", "")
            miembros_filtrados = [m for m in miembros if filtro_busqueda.lower() in m["nombre"].lower() or filtro_busqueda.lower() in m.get("ministerio", "").lower() or filtro_busqueda.lower() in m.get("telefono", "")]
            st.markdown("Total registrados: " + str(len(miembros_filtrados)) + " miembros")
            for idx, m in enumerate(miembros_filtrados):
                with st.container():
                    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                    c1.markdown("**" + m["nombre"] + "** (" + m.get("estado", "Activo") + ")")
                    c1.caption("Tel: " + m.get("telefono", "S/N") + " | Email: " + m.get("email", "S/N"))
                    c2.markdown("Ministerio: " + m.get("ministerio", "General"))
                    c2.caption("Cumple: " + m.get("cumpleanos", "N/D"))
                    c3.caption("Registrado: " + m.get("fecha_registro", "N/D"))
                    if c4.button("Eliminar", key="del_m_" + m["id"]):
                        miembros = [item for item in miembros if item["id"] != m["id"]]
                        guardar_datos_json(MIEMBROS_FILE, miembros)
                        st.rerun()
                    st.divider()
        else:
            st.info("No hay miembros registrados todavia.")

    with tab_asistencia:
        st.subheader("Registro de Asistencia")
        if not miembros:
            st.warning("Primero registra miembros en el directorio para tomar asistencia.")
        else:
            with st.form("form_asistencia"):
                col_fec, col_tipo = st.columns(2)
                fecha_asist = col_fec.date_input("Fecha del Servicio/Reunion", value=datetime.today())
                tipo_evento = col_tipo.selectbox("Tipo de Reunion", ["Culto General / Domingo", "Culto de Oracion", "Celula / Hogar", "Reunion de Jovenes", "Reunion de Mujeres", "Reunion de Hombres", "Otro"])
                st.markdown("Marcar presentes:")
                presentes_ids = []
                for m in miembros:
                    if st.checkbox(m["nombre"] + " (" + m.get("ministerio", "General") + ")", key="asist_" + m["id"]):
                        presentes_ids.append(m["id"])
                visitas_nuevas = st.number_input("Numero de personas nuevas / visitas", min_value=0, step=1, value=0)
                guardar_asist = st.form_submit_button("Guardar Asistencia", use_container_width=True)
                if guardar_asist:
                    registro_asist = {"id": str(uuid.uuid4())[:8], "fecha": fecha_asist.strftime("%Y-%m-%d"), "tipo": tipo_evento, "presentes_count": len(presentes_ids), "presentes_ids": presentes_ids, "visitas": int(visitas_nuevas), "total": len(presentes_ids) + int(visitas_nuevas)}
                    asistencias.append(registro_asist)
                    guardar_datos_json(ASISTENCIAS_FILE, asistencias)
                    st.success("Asistencia guardada correctamente.")
                    st.rerun()

    with tab_reportes_m:
        st.subheader("Resumen y Cumpleanos del Mes")
        mes_actual = datetime.today().month
        cumpleaneros = [m for m in miembros if m.get("cumpleanos") and int(m["cumpleanos"].split("-")[1]) == mes_actual]
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Total Miembros Activos", len([m for m in miembros if m.get("estado") == "Activo"]))
        col_m2.metric("Cumpleanos este mes", len(cumpleaneros))
        if cumpleaneros:
            st.markdown("Cumpleaneros de este mes:")
            for c in cumpleaneros:
                st.write("- " + c["nombre"] + " - Dia: " + c["cumpleanos"].split("-")[2])
        if asistencias:
            st.markdown("---")
            st.markdown("Ultimas Asistencias Registradas")
            for a in reversed(asistencias[-10:]):
                st.write(a["fecha"] + " | " + a["tipo"] + " -> " + str(a.get("total", 0)) + " personas")

    st.stop()


if modo == "Ofrendas y Finanzas":
    tab_reg_fin, tab_historial_fin, tab_balance = st.tabs(["Registrar Entrada / Salida", "Historial de Transacciones", "Balance General"])
    ofrendas = cargar_datos_json(OFRENDAS_FILE)

    with tab_reg_fin:
        st.subheader("Registrar Movimiento Financiero")
        with st.form("form_finanzas"):
            col_t, col_f = st.columns(2)
            tipo_mov = col_t.selectbox("Tipo de Movimiento", ["Entrada (Ingreso)", "Salida (Gasto)"])
            fecha_mov = col_f.date_input("Fecha", value=datetime.today())
            col_cat, col_monto = st.columns(2)
            if tipo_mov == "Entrada (Ingreso)":
                categoria = col_cat.selectbox("Categoria", ["Diezmo", "Ofrenda General", "Ofrenda Misionera", "Pro-Templo / Construccion", "Donacion Especial", "Evento / Actividad", "Otro"])
            else:
                categoria = col_cat.selectbox("Categoria", ["Servicios (Luz/Agua/Internet)", "Alquiler de Local", "Honorarios Pastorales", "Ayuda Social / Misericordia", "Mantenimiento / Compras", "Evangelismo / Eventos", "Otro Gasto"])
            monto = col_monto.number_input("Monto ($)", min_value=0.01, step=1.0, format="%.2f")
            col_metodo, col_resp = st.columns(2)
            metodo = col_metodo.selectbox("Metodo de Pago", ["Efectivo", "Transferencia Bancaria", "Tarjeta / En linea", "Cheque"])
            persona = col_resp.text_input("Entregado por / Pagado a (Opcional)")
            nota = st.text_area("Notas / Observaciones", height=70)
            guardar_fin = st.form_submit_button("Guardar Transaccion", use_container_width=True)
            if guardar_fin:
                transaccion = {"id": str(uuid.uuid4())[:8], "fecha": fecha_mov.strftime("%Y-%m-%d"), "tipo": tipo_mov, "categoria": categoria, "monto": float(monto), "metodo": metodo, "persona": persona.strip(), "nota": nota.strip(), "registrado_en": datetime.now().strftime("%Y-%m-%d %H:%M")}
                ofrendas.append(transaccion)
                guardar_datos_json(OFRENDAS_FILE, ofrendas)
                st.success("Transaccion registrada correctamente.")
                st.rerun()

    with tab_historial_fin:
        st.subheader("Historial de Movimientos")
        if ofrendas:
            for t in reversed(ofrendas):
                c1, c2, c3, c4 = st.columns([2, 3, 2, 1])
                signo = "+" if "Entrada" in t["tipo"] else "-"
                c1.markdown("**" + t["fecha"] + "**")
                c1.caption(t.get("metodo", "Efectivo"))
                c2.markdown("**" + t["categoria"] + "**")
                if t.get("nota"):
                    c2.caption(t.get("persona", "Anonimo") + " - " + t["nota"])
                else:
                    c2.caption(t.get("persona", "Anonimo"))
                c3.markdown("### " + signo + "$" + format(t["monto"], ",.2f"))
                if c4.button("Eliminar", key="del_fin_" + t["id"]):
                    ofrendas = [item for item in ofrendas if item["id"] != t["id"]]
                    guardar_datos_json(OFRENDAS_FILE, ofrendas)
                    st.rerun()
                st.divider()
        else:
            st.info("No hay transacciones registradas.")

    with tab_balance:
        st.subheader("Balance Financiero")
        total_ingresos = sum(t["monto"] for t in ofrendas if "Entrada" in t["tipo"])
        total_gastos = sum(t["monto"] for t in ofrendas if "Salida" in t["tipo"])
        balance_neto = total_ingresos - total_gastos
        c_in, c_out, c_bal = st.columns(3)
        c_in.metric("Total Ingresos", "$" + format(total_ingresos, ",.2f"))
        c_out.metric("Total Gastos", "$" + format(total_gastos, ",.2f"))
        c_bal.metric("Balance Neto", "$" + format(balance_neto, ",.2f"))

    st.stop()


if modo == "Liderazgo Bíblico":
    st.title("👑 Liderazgo Bíblico")
    st.caption("Formación de líderes para la iglesia y el hogar, siguiendo el modelo de Jesús.")


    def mostrar_ensenanza_liderazgo(tema, enfoque, texto_base, clave):
        """Muestra la enseñanza actual y permite expandirla con IA."""
        st.write(texto_base)

        clave_estado = "ensenanza_profunda_" + clave

        if st.button(
            "✨ Desarrollar enseñanza completa con IA",
            key="btn_ensenanza_" + clave,
            use_container_width=True
        ):
            with st.spinner("Desarrollando enseñanza bíblica profunda..."):
                prompt = f"""Actúa como un pastor, maestro bíblico y mentor de líderes cristianos.

Desarrolla una enseñanza completa y lista para compartir en una reunión de liderazgo.

Tema: {tema}
Enfoque: {enfoque}
Idea inicial ya existente: {texto_base}

Escribe en español, con tono pastoral, claro, maduro y cristocéntrico.
La enseñanza debe incluir:
1. Una introducción que conecte con la realidad del líder.
2. Desarrollo bíblico y teológico en 4 a 6 párrafos completos.
3. Explicación de cómo Jesús modela este principio.
4. Riesgos o errores comunes que deben evitarse.
5. Aplicaciones prácticas para el hogar, ministerio e iglesia.
6. Una conclusión breve y desafiante.

No inventes versículos. Mantén fidelidad al contexto bíblico.
Usa títulos en Markdown para facilitar su lectura."""

                try:
                    respuesta = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system",
                                "content": "Eres un maestro bíblico responsable, pastoral, cristocéntrico y práctico."
                            },
                            {"role": "user", "content": prompt}
                        ]
                    ).choices[0].message.content

                    st.session_state[clave_estado] = respuesta

                except Exception as e:
                    st.error(f"No se pudo generar la enseñanza: {e}")

        if st.session_state.get(clave_estado):
            st.divider()
            st.markdown("### 📖 Enseñanza desarrollada")
            st.markdown(st.session_state[clave_estado])

            if st.button("💾 Guardar para compartir", key="guardar_" + clave_estado, use_container_width=True):
                guardado = cargar_datos_json(LIDERAZGO_GUARDADO_FILE)
                if not isinstance(guardado, list):
                    guardado = []
                guardado.append({
                    "id": str(uuid.uuid4())[:8],
                    "tipo": "Enseñanza",
                    "titulo": tema,
                    "contenido": st.session_state[clave_estado],
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                guardar_datos_json(LIDERAZGO_GUARDADO_FILE, guardado)
                st.success("✅ Enseñanza guardada. Ve a la pestaña 📂 Guardado para verla.")


    def mostrar_dinamica_liderazgo(titulo, objetivo, idea_base, clave):
        """Genera dinámicas detalladas según la duración elegida."""
        duracion = st.selectbox(
            "⏱️ Duración de la dinámica",
            ["10 minutos", "15 minutos", "30 minutos", "45 minutos", "60 minutos"],
            index=1,
            key="duracion_dinamica_" + clave
        )

        st.write(f"**Objetivo:** {objetivo}")
        st.caption("Versión breve actual:")
        st.markdown(idea_base)

        clave_estado = "dinamica_profunda_" + clave

        if st.button(
            "🔄 Desarrollar dinámica completa con IA",
            key="btn_dinamica_" + clave,
            use_container_width=True
        ):
            with st.spinner("Diseñando dinámica de conexión..."):
                prompt = f"""Actúa como facilitador experto de reuniones de liderazgo cristiano.

Crea una dinámica de conexión completa, segura, participativa y bíblicamente centrada.

Título de la dinámica: {titulo}
Objetivo: {objetivo}
Duración total disponible: {duracion}
Idea inicial: {idea_base}

Desarrolla exactamente estas secciones:

## Preparación
Materiales necesarios, tamaño recomendado del grupo y disposición del espacio.

## Distribución del tiempo
Divide los {duracion} en etapas claras, indicando los minutos de cada etapa.

## Instrucciones paso a paso
Explica con detalle qué debe decir y hacer el facilitador, y qué deben hacer los participantes.

## Preguntas de reflexión
Incluye 3 a 5 preguntas profundas, respetuosas y aplicables.

## Conexión bíblica
Incluye uno o dos pasajes bíblicos pertinentes y explica brevemente cómo conectan con la actividad.

## Cierre y oración
Da una guía breve de oración final y un compromiso práctico para la semana.

La dinámica debe servir para líderes de iglesia, fomentar participación y evitar exponer asuntos privados de forma insegura."""

                try:
                    respuesta = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system",
                                "content": "Eres un facilitador pastoral cristiano, creativo, práctico y sensible."
                            },
                            {"role": "user", "content": prompt}
                        ]
                    ).choices[0].message.content

                    st.session_state[clave_estado] = respuesta

                except Exception as e:
                    st.error(f"No se pudo generar la dinámica: {e}")

        if st.session_state.get(clave_estado):
            st.divider()
            st.markdown("### 🔗 Dinámica desarrollada")
            st.markdown(st.session_state[clave_estado])

            if st.button("💾 Guardar para compartir", key="guardar_" + clave_estado, use_container_width=True):
                guardado = cargar_datos_json(LIDERAZGO_GUARDADO_FILE)
                if not isinstance(guardado, list):
                    guardado = []
                guardado.append({
                    "id": str(uuid.uuid4())[:8],
                    "tipo": "Dinámica",
                    "titulo": titulo,
                    "contenido": st.session_state[clave_estado],
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                guardar_datos_json(LIDERAZGO_GUARDADO_FILE, guardado)
                st.success("✅ Dinámica guardada. Ve a la pestaña 📂 Guardado para verla.")


    tab_ensenar, tab_formar, tab_multiplicar, tab_servir, tab_plan, tab_restauracion, tab_faq, tab_guardado = st.tabs([
        "📚 Enseñar",
        "🛠️ Formar",
        "🌱 Multiplicar",
        "🤝 Servir",
        "🧭 Plan de crecimiento",
        "🕊️ Restauración",
        "❓ Preguntas frecuentes",
        "📂 Guardado"
    ])

    with tab_ensenar:
        st.subheader("El fundamento del liderazgo bíblico")
        st.write(
            "Un líder cristiano no lidera para ser servido, sino para servir, "
            "edificar personas y reflejar el carácter de Cristo."
        )

        temas_ensenar = [
            {
                "titulo": "1. El líder es siervo primero",
                "versiculo": "Mateo 20:26 — «El que quiera hacerse grande entre vosotros será vuestro servidor.»",
                "ensenanza": (
                    "Jesús cambió el modelo de liderazgo del mundo. En el Reino de Dios, "
                    "la grandeza no se mide por el cargo, el reconocimiento o la cantidad de personas "
                    "que siguen a alguien, sino por su disposición a servir. Un líder bíblico cuida, "
                    "acompaña, escucha y ayuda a otros a crecer."
                ),
                "aplicacion": "¿A quién puedo servir esta semana sin esperar reconocimiento?",
                "pasajes": ["Marcos 10:42-45", "Filipenses 2:5-8", "Juan 13:12-17"]
            },
            {
                "titulo": "2. El carácter antes que el don",
                "versiculo": "1 Timoteo 3:2 — «Pero es necesario que el obispo sea irreprensible...»",
                "ensenanza": (
                    "Los dones, talentos y habilidades pueden abrir oportunidades, pero el carácter "
                    "es lo que sostiene a un líder con el tiempo. La humildad, la integridad, el dominio "
                    "propio, la fidelidad y el buen testimonio son indispensables para liderar de una forma "
                    "que honre a Dios."
                ),
                "aplicacion": "¿Qué área de mi carácter necesita ser trabajada por Dios hoy?",
                "pasajes": ["1 Timoteo 3:1-7", "Tito 1:6-9", "Gálatas 5:22-23"]
            },
            {
                "titulo": "3. Autoridad bajo autoridad",
                "versiculo": "Hebreos 13:17 — «Obedeced a vuestros pastores, y sujetaos a ellos...»",
                "ensenanza": (
                    "Ningún líder saludable trabaja aislado. El liderazgo bíblico reconoce la cobertura, "
                    "recibe corrección y mantiene un corazón enseñable. Estar bajo autoridad espiritual "
                    "no disminuye al líder: lo protege, lo forma y le ayuda a permanecer humilde."
                ),
                "aplicacion": "¿Tengo personas maduras en la fe que puedan aconsejarme y corregirme?",
                "pasajes": ["Romanos 13:1-2", "1 Pedro 5:5", "Efesios 5:21"]
            },
            {
                "titulo": "4. Visión que viene de Dios, no del ego",
                "versiculo": "Nehemías 2:12 — «No declaré a hombre alguno lo que Dios había puesto en mi corazón...»",
                "ensenanza": (
                    "La visión bíblica nace en la oración y en la sensibilidad a la necesidad de las personas. "
                    "Nehemías recibió una carga por Jerusalén, oró, planificó y movilizó al pueblo. "
                    "Un líder no busca construir su propio nombre; busca cumplir el propósito de Dios."
                ),
                "aplicacion": "¿Qué carga o necesidad ha puesto Dios en mi corazón para servir?",
                "pasajes": ["Habacuc 2:2-3", "Proverbios 29:18", "Nehemías 2:17-18"]
            },
            {
                "titulo": "5. Los dones espirituales al servicio del cuerpo",
                "versiculo": "1 Corintios 12:7 — «A cada uno le es dada la manifestación del Espíritu para provecho.»",
                "ensenanza": (
                    "Cada creyente ha recibido dones para edificar a otros. El liderazgo no consiste en "
                    "hacerlo todo solo, sino en reconocer, afirmar y activar los dones de las personas. "
                    "Cuando cada miembro sirve, el cuerpo de Cristo crece con salud."
                ),
                "aplicacion": "¿Cómo puedo usar mis dones para edificar a alguien esta semana?",
                "pasajes": ["Romanos 12:4-8", "Efesios 4:11-13", "1 Pedro 4:10-11"]
            }
        ]

        for tema in temas_ensenar:
            with st.expander(tema["titulo"], expanded=False):
                st.markdown("### 📖 Versículo clave")
                st.info(tema["versiculo"])

                st.markdown("### ✨ Enseñanza")
                mostrar_ensenanza_liderazgo(
                    tema["titulo"],
                    tema["versiculo"],
                    tema["ensenanza"],
                    "ensenar_" + str(temas_ensenar.index(tema))
                )

                st.markdown("### 🎯 Pregunta de aplicación")
                st.success(tema["aplicacion"])

                st.markdown("### 📚 Más pasajes para profundizar")
                for pasaje in tema["pasajes"]:
                    st.write("- " + pasaje)

        st.divider()
        st.subheader("🔗 Dinámica de conexión: El liderazgo que deja huella")
        mostrar_dinamica_liderazgo(
            "El liderazgo que deja huella",
            "Identificar el tipo de liderazgo que Dios quiere formar en cada persona.",
            """1. Formen grupos de 2 o 3 personas.
2. Cada participante responde: ¿Qué líder cristiano ha impactado mi vida y qué cualidad de Cristo vi en él o ella?
3. Cada persona comparte una cualidad que desea desarrollar como líder.
4. Finalicen orando unos por otros, pidiendo a Dios un corazón de siervo.""",
            "huella"
        )

        st.divider()
        st.subheader("🤖 Pregúntale a la IA sobre Enseñanza")
        pregunta_ensenar = st.text_input("Ej: ¿Cómo enseño humildad a un líder orgulloso?", key="pregunta_ensenar")
        if st.button("Preguntar", key="btn_ensenar"):
            if pregunta_ensenar.strip():
                with st.spinner("Pensando..."):
                    respuesta = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Eres un mentor experto en ENSEÑAR liderazgo biblico: fundamentos, caracter, autoridad, vision y dones espirituales. Responde claro, practico, breve y con referencias biblicas cuando aplique."},
                            {"role": "user", "content": pregunta_ensenar}
                        ]
                    ).choices[0].message.content
                st.session_state["respuesta_ensenar"] = respuesta
        if st.session_state.get("respuesta_ensenar"):
            st.info(st.session_state["respuesta_ensenar"])

    with tab_formar:
        st.subheader("Desarrollo práctico del líder")
        st.write("Enseñar da fundamento; formar da herramientas.")
        temas_formar = [
            {"titulo": "1. Cómo dirigir una reunión con propósito",
             "objetivo": "Estructurar una célula con orden, contenido y conexión espiritual.",
             "pasos": ["Prepara el tema y ora antes.", "Comienza con dinámica de conexión (5-10 min).",
                       "Desarrolla el tema con participación.", "Deja espacio para oración.",
                       "Cierra con compromiso práctico."],
             "practica": "Dirige una reunión siguiendo estos 5 pasos esta semana.",
             "pasajes": ["Hechos 2:42-47", "Eclesiastés 3:1"]},
            {"titulo": "2. Cómo dar seguimiento a un discípulo",
             "objetivo": "Acompañar el crecimiento espiritual constante.",
             "pasos": ["Agenda un encuentro breve semanal.", "Pregunta por su vida devocional.",
                       "Escucha más de lo que hablas.", "Ora con la persona.", "Dale una tarea pequeña."],
             "practica": "Elige a alguien e inicia un seguimiento intencional.",
             "pasajes": ["1 Tesalonicenses 5:11", "Hebreos 10:24-25"]},
            {"titulo": "3. Manejo de conflictos con sabiduría",
             "objetivo": "Resolver desacuerdos sin dividir al equipo.",
             "pasos": ["Busca momento y lugar adecuado.", "Escucha primero.", "Habla con verdad y amor.",
                       "Busca solución concreta.", "Cierra en oración."],
             "practica": "Aplica estos pasos a un conflicto pendiente.",
             "pasajes": ["Mateo 18:15-17", "Proverbios 15:1", "Santiago 1:19-20"]},
            {"titulo": "4. Hablar con claridad y convicción",
             "objetivo": "Comunicar ideas claras ante un grupo.",
             "pasos": ["Define un mensaje central.", "Usa ejemplos concretos.", "Sé breve pero profundo.",
                       "Practica en voz alta.", "Termina con aplicación clara."],
             "practica": "Prepara una idea de 3 minutos y compártela esta semana.",
             "pasajes": ["Colosenses 4:6", "Proverbios 25:11"]},
            {"titulo": "5. Planificación con visión",
             "objetivo": "Organizar metas concretas.",
             "pasos": ["Define una meta clara.", "Escribe 3 acciones concretas.", "Asigna fechas.",
                       "Revisa el avance semanal.", "Ajusta el plan si es necesario."],
             "practica": "Escribe hoy una meta y sus 3 pasos.",
             "pasajes": ["Proverbios 16:3", "Lucas 14:28-30"]},
            {"titulo": "6. Delegar con sabiduría",
             "objetivo": "Aprender a soltar responsabilidades sin perder el control ni sobrecargarte.",
             "pasos": ["Identifica qué tareas puedes delegar.", "Elige a la persona adecuada según su carácter y disposición.",
                       "Da instrucciones claras y el resultado esperado.", "Da seguimiento sin controlar cada detalle.",
                       "Reconoce y celebra el resultado."],
             "practica": "Delega una tarea concreta esta semana y da seguimiento sin hacerla tú mismo.",
             "pasajes": ["Éxodo 18:17-23", "Hechos 6:2-4"]}
        ]
        for tema in temas_formar:
            with st.expander(tema["titulo"], expanded=False):
                st.markdown("### 🎯 Objetivo")
                st.info(tema["objetivo"])

                st.markdown("### ✨ Enseñanza a compartir")
                mostrar_ensenanza_liderazgo(
                    tema["titulo"],
                    "Formación práctica de líderes cristianos",
                    tema["objetivo"],
                    "formar_" + str(temas_formar.index(tema))
                )

                st.markdown("### 🧭 Pasos prácticos")
                for paso in tema["pasos"]:
                    st.write("- " + paso)
                st.markdown("### 📝 Tarea de práctica")
                st.success(tema["practica"])

                st.markdown("### 📚 Más pasajes para profundizar")
                for pasaje in tema["pasajes"]:
                    st.write("- " + pasaje)
        st.divider()
        st.subheader("🔗 Dinámica: Roles en acción")
        mostrar_dinamica_liderazgo(
            "Roles en acción",
            "Practicar liderazgo en un ambiente seguro.",
            """1. Formen parejas.
2. Una persona representa una situación real de liderazgo.
3. La otra practica una respuesta bíblica y sabia.
4. Intercambien roles.
5. Cierren orando.""",
            "roles"
        )

        st.divider()
        st.subheader("🤖 Pregúntale a la IA sobre Formación")
        pregunta_formar = st.text_input("Ej: ¿Cómo debo empezar a formar líderes en mi célula?", key="pregunta_formar")
        if st.button("Preguntar", key="btn_formar"):
            if pregunta_formar.strip():
                with st.spinner("Pensando..."):
                    respuesta = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Eres un mentor experto en FORMAR lideres cristianos de manera practica: dirigir reuniones, dar seguimiento, resolver conflictos, comunicar con claridad y planificar con vision. Da consejos concretos, aplicables paso a paso."},
                            {"role": "user", "content": pregunta_formar}
                        ]
                    ).choices[0].message.content
                st.session_state["respuesta_formar"] = respuesta
        if st.session_state.get("respuesta_formar"):
            st.info(st.session_state["respuesta_formar"])

    with tab_multiplicar:
        st.subheader("Levantar nuevos líderes")
        st.write("El liderazgo bíblico se reproduce (Mateo 28:19-20).")
        temas_multiplicar = [
            {"titulo": "1. Identificar el potencial en otros",
             "principio": "2 Timoteo 2:2 — encarga a hombres fieles idóneos para enseñar a otros.",
             "ensenanza": "El potencial se nota primero en la fidelidad en lo pequeño (Lucas 16:10).",
             "ejercicio": "Piensa en 2 personas fieles e invierte en ellas esta semana.",
             "pasajes": ["Lucas 6:12-13", "1 Samuel 16:7"]},
            {"titulo": "2. Delegar con propósito",
             "principio": "Éxodo 18:21-22 — Jetro aconseja nombrar hombres capaces.",
             "ensenanza": "Delegar es formar a otros dándoles responsabilidad real.",
             "ejercicio": "Entrega una responsabilidad tuya a alguien en formación.",
             "pasajes": ["Números 11:16-17", "Hechos 6:1-4"]},
            {"titulo": "3. Mentoría uno a uno",
             "principio": "1 Tesalonicenses 2:8 — entregar también nuestras propias vidas.",
             "ensenanza": "La multiplicación ocurre en relación cercana, no solo enseñanza masiva.",
             "ejercicio": "Invita a alguien a hablar de su caminar con Dios esta semana.",
             "pasajes": ["2 Timoteo 1:5-6", "Rut 1:16"]},
            {"titulo": "4. Reproducir el carácter, no solo el conocimiento",
             "principio": "1 Corintios 11:1 — Sed imitadores de mí, así como yo de Cristo.",
             "ensenanza": "El discípulo aprende observando cómo su líder ora, sirve y perdona.",
             "ejercicio": "Invita a alguien a acompañarte en una actividad de servicio.",
             "pasajes": ["Filipenses 4:9", "2 Reyes 2:9-15"]},
            {"titulo": "5. Soltar con confianza",
             "principio": "Hechos 1:8 — me seréis testigos hasta lo último de la tierra.",
             "ensenanza": "Retener el control impide que otros crezcan como líderes.",
             "ejercicio": "Entrega por completo una tarea a alguien este mes, sin intervenir.",
             "pasajes": ["Juan 14:12", "Josué 1:1-9"]}
        ]
        for tema in temas_multiplicar:
            with st.expander(tema["titulo"], expanded=False):
                st.markdown("### 📖 Principio bíblico")
                st.info(tema["principio"])
                st.markdown("### ✨ Enseñanza")
                mostrar_ensenanza_liderazgo(
                    tema["titulo"],
                    tema["principio"],
                    tema["ensenanza"],
                    "multiplicar_" + str(temas_multiplicar.index(tema))
                )
                st.markdown("### 🌱 Ejercicio de multiplicación")
                st.success(tema["ejercicio"])

                st.markdown("### 📚 Más pasajes para profundizar")
                for pasaje in tema["pasajes"]:
                    st.write("- " + pasaje)
        st.divider()
        st.subheader("🔗 Dinámica: A quién estoy formando")
        mostrar_dinamica_liderazgo(
            "A quién estoy formando",
            "Identificar a quién discipula cada líder y definir un siguiente paso.",
            """1. Escribe uno o dos nombres de personas que estés formando.
2. Si aún no tienes a alguien, ora pidiendo a Dios que te muestre a quién acompañar.
3. En parejas, compartan qué necesita esa persona.
4. Cierren orando.""",
            "formando"
        )

        st.divider()
        st.subheader("🤖 Pregúntale a la IA sobre Multiplicación")
        pregunta_multiplicar = st.text_input("Ej: ¿Cómo identifico a quién debo levantar como líder?", key="pregunta_multiplicar")
        if st.button("Preguntar", key="btn_multiplicar"):
            if pregunta_multiplicar.strip():
                with st.spinner("Pensando..."):
                    respuesta = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Eres un mentor experto en MULTIPLICAR lideres: identificar potencial, delegar, mentoria uno a uno, reproducir caracter y soltar con confianza. Da consejos concretos y practicos, con base biblica cuando aplique."},
                            {"role": "user", "content": pregunta_multiplicar}
                        ]
                    ).choices[0].message.content
                st.session_state["respuesta_multiplicar"] = respuesta
        if st.session_state.get("respuesta_multiplicar"):
            st.info(st.session_state["respuesta_multiplicar"])

    with tab_servir:
        st.subheader("El liderazgo que sirve")
        st.write(
            "Jesús mismo dio el ejemplo máximo: lavó los pies de sus discípulos (Juan 13:1-17). "
            "El liderazgo bíblico se demuestra, no solo se predica."
        )

        temas_servir = [
            {
                "titulo": "1. Servir en el hogar antes que en el ministerio",
                "principio": "1 Timoteo 3:5 — «Pues el que no sabe gobernar su propia casa, ¿cómo cuidará de la iglesia de Dios?»",
                "ensenanza": (
                    "El liderazgo verdadero comienza en casa. Un líder que sirve, ama y "
                    "cuida a su familia con paciencia y humildad, refleja el mismo carácter "
                    "que necesita para servir a la iglesia. El ministerio no reemplaza al hogar; "
                    "el hogar es el primer ministerio."
                ),
                "practica": "Esta semana, haz un acto concreto de servicio en tu casa sin que te lo pidan.",
                "pasajes": ["Efesios 5:25", "Efesios 6:4", "Josué 24:15"]
            },
            {
                "titulo": "2. Servir sin buscar reconocimiento",
                "principio": "Juan 13:14-15 — «Pues si yo, el Señor y el Maestro, he lavado vuestros pies... también vosotros debéis lavaros los pies los unos a los otros.»",
                "ensenanza": (
                    "Jesús tomó el lugar del siervo más humilde para enseñar que el liderazgo "
                    "no busca el aplauso ni el puesto visible. El verdadero servicio muchas veces "
                    "ocurre en lo oculto: ayudando, limpiando, escuchando, sin que nadie lo note."
                ),
                "practica": "Haz un servicio esta semana que nadie vea ni sepa que hiciste tú.",
                "pasajes": ["Mateo 6:1-4", "Colosenses 3:23-24"]
            },
            {
                "titulo": "3. Servir con humildad ante la corrección",
                "principio": "Proverbios 15:32 — «El que escucha la corrección tiene entendimiento.»",
                "ensenanza": (
                    "Un líder que sirve también sabe recibir corrección sin defenderse ni "
                    "justificarse. La humildad para ser corregido es una de las señales más "
                    "claras de madurez espiritual y de un corazón dispuesto a crecer."
                ),
                "practica": "La próxima vez que recibas una corrección, agradece antes de responder.",
                "pasajes": ["Proverbios 12:1", "Hebreos 12:11"]
            },
            {
                "titulo": "4. Servir a los que no pueden retribuir",
                "principio": "Lucas 14:13-14 — «...llama a los pobres, los mancos, los cojos y los ciegos... serás bienaventurado, porque ellos no te pueden recompensar.»",
                "ensenanza": (
                    "El servicio bíblico no busca beneficio propio. Servir a quienes no pueden "
                    "devolver el favor revela un corazón que refleja la gracia de Dios, "
                    "quien nos amó primero sin que lo mereciéramos."
                ),
                "practica": "Identifica a alguien que no puede 'devolverte el favor' y sírvele esta semana.",
                "pasajes": ["Mateo 25:35-40", "Santiago 1:27"]
            },
            {
                "titulo": "5. Servir con constancia, no solo con emoción",
                "principio": "Gálatas 6:9 — «No nos cansemos de hacer bien, porque a su tiempo segaremos, si no desmayamos.»",
                "ensenanza": (
                    "El liderazgo que sirve no depende del ánimo del momento. La fidelidad "
                    "constante, incluso en temporadas de cansancio o poco fruto visible, "
                    "es lo que finalmente da frutos duraderos en el tiempo de Dios."
                ),
                "practica": "Continúa sirviendo esta semana en algo que ya haces, aunque no sientas ánimo.",
                "pasajes": ["1 Corintios 15:58", "Hebreos 6:10"]
            }
        ]

        for tema in temas_servir:
            with st.expander(tema["titulo"], expanded=False):
                st.markdown("### 📖 Principio bíblico")
                st.info(tema["principio"])

                st.markdown("### ✨ Enseñanza")
                mostrar_ensenanza_liderazgo(
                    tema["titulo"],
                    tema["principio"],
                    tema["ensenanza"],
                    "servir_" + str(temas_servir.index(tema))
                )

                st.markdown("### 🤝 Práctica de servicio")
                st.success(tema["practica"])

                st.markdown("### 📚 Más pasajes para profundizar")
                for pasaje in tema["pasajes"]:
                    st.write("- " + pasaje)

        st.divider()
        st.subheader("🔗 Dinámica de conexión: El servicio invisible")
        mostrar_dinamica_liderazgo(
            "El servicio invisible",
            "Practicar el servicio sin buscar reconocimiento.",
            """1. Cada participante piensa en una persona de su iglesia, célula o familia.
2. Planea un acto de servicio para esa persona sin anunciar que fue realizado por ti.
3. En la siguiente reunión compartan, sin señalar a nadie, cómo se sintieron al servir en silencio.
4. Cierren orando por un corazón de siervo como el de Jesús.""",
            "servicio_invisible"
        )

        st.divider()
        st.subheader("🤖 Pregúntale a la IA sobre Servicio")
        pregunta_servir = st.text_input("Ej: ¿Cómo sirvo a mi iglesia sin descuidar a mi familia?", key="pregunta_servir")
        if st.button("Preguntar", key="btn_servir"):
            if pregunta_servir.strip():
                with st.spinner("Pensando..."):
                    respuesta = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Eres un mentor experto en el liderazgo que SIRVE: servicio en el hogar, servicio sin reconocimiento, humildad ante correccion, servicio desinteresado y constancia. Da consejos practicos, humildes y con base biblica cuando aplique."},
                            {"role": "user", "content": pregunta_servir}
                        ]
                    ).choices[0].message.content
                st.session_state["respuesta_servir"] = respuesta
        if st.session_state.get("respuesta_servir"):
            st.info(st.session_state["respuesta_servir"])

    with tab_plan:
        st.subheader("🧭 Plan de crecimiento personal")
        st.write(
            "Elige las áreas en las que quieres crecer y el tiempo disponible. "
            "La IA generará un plan semanal con enseñanza, práctica y un versículo guía."
        )

        areas_disponibles = ["Enseñar (fundamentos)", "Formar (herramientas prácticas)",
                              "Multiplicar (levantar líderes)", "Servir (carácter y humildad)"]

        areas_elegidas = st.multiselect(
            "Áreas de enfoque (elige 1 a 4)",
            areas_disponibles,
            default=[areas_disponibles[0]],
            key="plan_areas"
        )

        duracion_plan = st.selectbox(
            "Duración del plan",
            ["2 semanas", "4 semanas", "8 semanas"],
            index=1,
            key="plan_duracion"
        )

        nota_personal = st.text_area(
            "Contexto personal (opcional)",
            placeholder="Ej: Soy líder de célula hace 1 año, me cuesta delegar y dar seguimiento...",
            key="plan_contexto"
        )

        if st.button("🧭 Generar mi plan de crecimiento", key="btn_generar_plan", use_container_width=True):
            if not areas_elegidas:
                st.warning("Elige al menos un área para generar el plan.")
            else:
                with st.spinner("Generando tu plan de crecimiento..."):
                    prompt = f"""Actúa como un mentor pastoral experto en formación de líderes cristianos.

Crea un plan de crecimiento personal para un líder de iglesia.

Áreas de enfoque elegidas: {", ".join(areas_elegidas)}
Duración total: {duracion_plan}
Contexto personal del líder: {nota_personal if nota_personal.strip() else "No proporcionó contexto adicional."}

Genera el plan organizado semana por semana (usa "## Semana 1", "## Semana 2", etc.).
Para cada semana incluye:
- Un versículo guía relacionado al área de esa semana.
- Un objetivo claro y alcanzable.
- Una breve enseñanza (2-3 párrafos) relacionada al área.
- Una acción práctica concreta para aplicar esa semana.
- Una pregunta de reflexión personal.

Combina las áreas elegidas de forma equilibrada a lo largo de las semanas.
Sé cálido, pastoral, realista y evita sonar genérico. Escribe en español."""

                    try:
                        respuesta = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "Eres un mentor pastoral que diseña planes de crecimiento personalizados, bíblicos y prácticos para líderes cristianos."},
                                {"role": "user", "content": prompt}
                            ]
                        ).choices[0].message.content

                        st.session_state["plan_crecimiento_generado"] = respuesta

                    except Exception as e:
                        st.error(f"No se pudo generar el plan: {e}")

        if st.session_state.get("plan_crecimiento_generado"):
            st.divider()
            st.markdown("### 🧭 Tu plan de crecimiento")
            st.markdown(st.session_state["plan_crecimiento_generado"])

            if st.button("💾 Guardar para compartir", key="guardar_plan_crecimiento", use_container_width=True):
                guardado = cargar_datos_json(LIDERAZGO_GUARDADO_FILE)
                if not isinstance(guardado, list):
                    guardado = []
                guardado.append({
                    "id": str(uuid.uuid4())[:8],
                    "tipo": "Plan de crecimiento",
                    "titulo": "Plan (" + duracion_plan + ") - " + ", ".join(areas_elegidas),
                    "contenido": st.session_state["plan_crecimiento_generado"],
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                guardar_datos_json(LIDERAZGO_GUARDADO_FILE, guardado)
                st.success("✅ Plan guardado. Ve a la pestaña 📂 Guardado para verlo.")

    with tab_restauracion:
        st.subheader("🕊️ Restauración del líder caído")
        st.write(
            "Todo líder puede caer, fallar o desanimarse profundamente. "
            "La Biblia no oculta las caídas de sus líderes: muestra también el camino de regreso."
        )

        st.markdown("### 📖 La gracia que restaura")
        st.info(
            "Salmo 51:12 — «Vuélveme el gozo de tu salvación, y espíritu noble me sustente.»"
        )
        st.write(
            "Pedro negó a Jesús tres veces, y aun así fue restaurado y comisionado a apacentar "
            "las ovejas (Juan 21:15-17). David cometió adulterio y homicidio, y aun así Dios lo "
            "llamó \"varón conforme a su corazón\" después de su arrepentimiento genuino (Salmo 51). "
            "Jonás huyó de su llamado, y Dios lo buscó, lo corrigió y lo volvió a enviar (Jonás 3:1-2). "
            "La caída no es el final de la historia cuando hay arrepentimiento verdadero y se recibe "
            "la gracia de Dios."
        )

        st.markdown("### 🧭 Pasos bíblicos hacia la restauración")
        st.markdown("""
        1. **Reconocer sin excusas** — 1 Juan 1:9: confesar el pecado con honestidad, sin minimizarlo ni justificarlo.
        2. **Someterse a un proceso, no solo a una decisión** — Gálatas 6:1: dejarse restaurar "con espíritu de mansedumbre", con acompañamiento y rendición de cuentas real.
        3. **Aceptar consecuencias con humildad** — a veces la restauración espiritual no elimina consecuencias prácticas (tiempo fuera del ministerio, reparación, terapia, etc.).
        4. **Recibir tiempo y proceso** — la restauración no es inmediata ni automática; requiere paciencia y trabajo interior.
        5. **Volver a servir, si Dios y la cobertura espiritual lo confirman** — no toda caída significa el fin del llamado, pero tampoco toda caída debe restaurarse apresuradamente.
        """)

        st.warning(
            "⚠️ Esta sección ofrece acompañamiento y orientación bíblica general. "
            "No sustituye la consejería pastoral, psicológica o el acompañamiento presencial. "
            "Si la situación involucra abuso, violencia, adicciones graves o riesgo para ti u otra persona, "
            "busca ayuda profesional y pastoral de inmediato, además de usar este espacio."
        )

        st.divider()
        st.subheader("🤖 Espacio de acompañamiento personal")
        st.caption("Este espacio es privado. Puedes escribir con libertad lo que estás viviendo.")

        situacion_restauracion = st.text_area(
            "¿Qué estás enfrentando?",
            placeholder="Ej: Fallé moralmente y me alejé del liderazgo, me siento indigno de servir de nuevo...",
            key="situacion_restauracion",
            height=150
        )

        if st.button("🕊️ Pedir acompañamiento", key="btn_restauracion", use_container_width=True):
            if situacion_restauracion.strip():
                with st.spinner("Preparando una palabra de acompañamiento..."):
                    prompt = f"""Actúa como un pastor experimentado, compasivo, firme en la verdad bíblica y cuidadoso emocionalmente.

Una persona en liderazgo cristiano comparte lo siguiente sobre su caída o situación difícil:

"{situacion_restauracion}"

Responde con un mensaje pastoral que incluya:
1. Validación emocional genuina, sin minimizar lo que vive.
2. Verdad bíblica clara sobre la gracia, el arrepentimiento y la restauración (usa pasajes reales, sin inventarlos).
3. Pasos concretos y realistas para comenzar un proceso de restauración.
4. Una recomendación explícita de buscar acompañamiento pastoral o profesional presencial, especialmente si hay riesgo, abuso, adicción o daño a terceros.
5. Una palabra final de esperanza, sin prometer resultados que no se pueden garantizar.

No emitas juicios condenatorios. No digas que puedes reemplazar el acompañamiento pastoral real. Escribe en español, con calidez y firmeza a la vez."""

                    try:
                        respuesta = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {
                                    "role": "system",
                                    "content": "Eres un pastor compasivo, bíblicamente sólido y emocionalmente sabio, especializado en restauración de líderes caídos."
                                },
                                {"role": "user", "content": prompt}
                            ]
                        ).choices[0].message.content

                        st.session_state["respuesta_restauracion"] = respuesta

                    except Exception as e:
                        st.error(f"No se pudo generar la respuesta: {e}")
            else:
                st.warning("Escribe brevemente tu situación para poder acompañarte.")

        if st.session_state.get("respuesta_restauracion"):
            st.divider()
            st.markdown("### 🕊️ Palabra de acompañamiento")
            st.markdown(st.session_state["respuesta_restauracion"])

            if st.button("💾 Guardar de forma privada", key="guardar_restauracion", use_container_width=True):
                guardado = cargar_datos_json(LIDERAZGO_GUARDADO_FILE)
                if not isinstance(guardado, list):
                    guardado = []
                guardado.append({
                    "id": str(uuid.uuid4())[:8],
                    "tipo": "Restauración (privado)",
                    "titulo": "Acompañamiento personal",
                    "contenido": st.session_state["respuesta_restauracion"],
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                guardar_datos_json(LIDERAZGO_GUARDADO_FILE, guardado)
                st.success("✅ Guardado. Podrás verlo en 📂 Guardado, identificado como privado.")

    with tab_faq:
        st.subheader("❓ Preguntas frecuentes de líderes")
        st.caption("Respuestas ya preparadas a dudas comunes del liderazgo cristiano. No requieren IA.")

        faq_liderazgo = [
            {
                "categoria": "Discipulado",
                "pregunta": "¿Qué hago si nadie quiere ser discipulado?",
                "respuesta": (
                    "Primero revisa si el discipulado se está ofreciendo como invitación genuina y no como "
                    "obligación religiosa. Muchas veces las personas no rechazan el discipulado, sino la forma "
                    "en que se les invita.\n\n"
                    "Empieza con relaciones informales: invita a tomar un café, comparte tu vida, sirve junto a "
                    "esa persona antes de proponerle una reunión formal. Jesús discipuló caminando con sus "
                    "discípulos en la vida diaria (Marcos 3:14). Si aun así nadie responde, ora pidiendo a Dios "
                    "que prepare corazones, y sé fiel invirtiendo en 1 o 2 personas, aunque el grupo sea pequeño."
                )
            },
            {
                "categoria": "Discipulado",
                "pregunta": "¿Cómo discipulo a alguien mayor que yo?",
                "respuesta": (
                    "La edad no determina la madurez espiritual ni la autoridad para servir. Aborda la relación "
                    "con humildad, reconociendo su experiencia de vida, pero sin renunciar al llamado que Dios te dio.\n\n"
                    "En vez de posicionarte como \"maestro\", preséntate como un compañero de camino: \"Quiero "
                    "caminar contigo en esto, aprendamos juntos\". Pablo discipuló a Timoteo con autoridad "
                    "espiritual, pero con un trato de padre a hijo, no de superioridad (1 Timoteo 1:2). El respeto "
                    "mutuo abre la puerta, no la edad."
                )
            },
            {
                "categoria": "Conflictos",
                "pregunta": "¿Cómo manejo un conflicto entre dos miembros de mi célula o equipo?",
                "respuesta": (
                    "Sigue el patrón de Mateo 18:15-17: habla primero en privado con cada parte, escucha sin tomar "
                    "partido de inmediato, y busca la reconciliación antes que \"tener la razón\".\n\n"
                    "No permitas que el conflicto se resuelva por chismes o terceros. Si después de hablar en "
                    "privado no hay avance, involucra a otro líder o pastor como mediador. El objetivo no es "
                    "señalar culpables, sino restaurar la relación y proteger la unidad del grupo."
                )
            },
            {
                "categoria": "Conflictos",
                "pregunta": "¿Qué hago si alguien cuestiona mi liderazgo delante de otros?",
                "respuesta": (
                    "No respondas a la defensiva ni busques \"ganar\" delante del grupo. Responde con calma, "
                    "reconociendo si hay algo válido en el comentario, y propone hablarlo en privado después.\n\n"
                    "Ejemplo: \"Entiendo tu punto, hablemos de esto con calma al terminar para poder escucharte "
                    "mejor\". Esto protege tu carácter y evita que el momento se convierta en un enfrentamiento "
                    "público. Un liderazgo seguro no necesita imponerse; se sostiene con humildad y claridad."
                )
            },
            {
                "categoria": "Desánimo",
                "pregunta": "¿Qué hago cuando siento que ya no tengo fuerzas para liderar?",
                "respuesta": (
                    "El desánimo en el liderazgo es normal, incluso Elías lo sintió después de una gran victoria "
                    "espiritual (1 Reyes 19:4). No ignores la señal: descansa, aliméntate espiritualmente y busca "
                    "a alguien con quien hablarlo, no cargues esto solo.\n\n"
                    "Pregúntate si estás sirviendo por obligación o por convicción. A veces el desánimo revela que "
                    "necesitas un tiempo de pausa, no que debas renunciar al llamado. Habla con tu pastor o "
                    "cobertura espiritual antes de tomar decisiones drásticas."
                )
            },
            {
                "categoria": "Desánimo",
                "pregunta": "¿Es normal dudar de mi llamado como líder?",
                "respuesta": (
                    "Sí, es completamente normal. Moisés dudó de su llamado (Éxodo 4:10-13), Jeremías también "
                    "(Jeremías 1:6), y ambos fueron usados poderosamente por Dios.\n\n"
                    "La duda no siempre es falta de fe; a veces es una señal de humildad genuina frente a una "
                    "responsabilidad grande. Lo importante es no tomar decisiones definitivas en medio de la duda: "
                    "busca consejo, ora, y dale tiempo al proceso antes de renunciar al llamado."
                )
            },
            {
                "categoria": "Multiplicación",
                "pregunta": "¿Cómo sé si una persona está lista para liderar su propia célula o grupo?",
                "respuesta": (
                    "Evalúa 3 áreas: carácter (¿es fiel, humilde, enseñable?), fruto (¿ya está sirviendo y "
                    "discipulando informalmente?) y disposición (¿tiene el deseo y el tiempo para asumirlo?).\n\n"
                    "No esperes perfección, sino fidelidad en lo poco (Lucas 16:10). Acompáñalo en un proceso de "
                    "prueba: déjalo liderar una reunión mientras tú observas, y da retroalimentación antes de "
                    "enviarlo por completo."
                )
            },
            {
                "categoria": "Multiplicación",
                "pregunta": "¿Qué hago si la persona que formé como líder se aleja o abandona el grupo?",
                "respuesta": (
                    "Duele, pero no invalida el trabajo invertido. Jesús mismo invirtió en Judas y aun así lo "
                    "amó y sirvió hasta el final (Juan 13:1-5).\n\n"
                    "Evalúa con humildad si hubo algo que pudiste hacer diferente, pero no cargues con una culpa "
                    "que no te corresponde. Mantén la puerta abierta para el diálogo y la reconciliación, sin "
                    "forzar la relación. Sigue invirtiendo en otros; el fruto de tu labor no depende de un solo caso."
                )
            }
        ]

        col_busqueda, col_categoria = st.columns([2, 1])

        busqueda_faq = col_busqueda.text_input(
            "🔍 Buscar por palabra clave",
            placeholder="Ej: desánimo, conflicto, discipulado...",
            key="busqueda_faq"
        )

        categorias_faq = ["Todas"] + sorted(set(item["categoria"] for item in faq_liderazgo))
        categoria_elegida_faq = col_categoria.selectbox(
            "Categoría",
            categorias_faq,
            key="categoria_faq"
        )

        faq_filtrado = []
        for item in faq_liderazgo:
            coincide_categoria = (categoria_elegida_faq == "Todas" or item["categoria"] == categoria_elegida_faq)
            coincide_busqueda = (
                not busqueda_faq.strip()
                or busqueda_faq.lower() in item["pregunta"].lower()
                or busqueda_faq.lower() in item["respuesta"].lower()
            )
            if coincide_categoria and coincide_busqueda:
                faq_filtrado.append(item)

        if not faq_filtrado:
            st.info("No se encontraron preguntas con ese filtro o búsqueda.")
        else:
            for item in faq_filtrado:
                with st.expander(f"[{item['categoria']}] {item['pregunta']}"):
                    st.markdown(item["respuesta"])

    with tab_guardado:
        st.subheader("📂 Enseñanzas y Dinámicas Guardadas")
        st.caption("Aquí se guarda todo el contenido que marcaste con 💾 Guardar para compartir.")

        guardado_liderazgo = cargar_datos_json(LIDERAZGO_GUARDADO_FILE)
        if not isinstance(guardado_liderazgo, list):
            guardado_liderazgo = []

        if not guardado_liderazgo:
            st.info("Todavía no has guardado ninguna enseñanza ni dinámica. Genera una con IA y presiona 'Guardar para compartir'.")
        else:
            filtro_tipo = st.radio(
                "Filtrar por tipo",
                ["Todos", "Enseñanza", "Dinámica"],
                horizontal=True
            )

            lista_filtrada = [
                item for item in guardado_liderazgo
                if filtro_tipo == "Todos" or item.get("tipo") == filtro_tipo
            ]

            for item in reversed(lista_filtrada):
                emoji_item = "📖" if item.get("tipo") == "Enseñanza" else "🔗"
                with st.expander(f"{emoji_item} [{item.get('tipo')}] {item.get('titulo')} — {item.get('fecha')}"):
                    st.markdown(item.get("contenido", ""))

                    col_dl, col_del = st.columns(2)

                    col_dl.download_button(
                        "⬇️ Descargar TXT",
                        data=item.get("contenido", ""),
                        file_name=(item.get("titulo", "contenido").replace(" ", "_") + ".txt"),
                        mime="text/plain",
                        use_container_width=True,
                        key="dl_lid_" + item.get("id", "")
                    )

                    if col_del.button(
                        "🗑️ Eliminar",
                        key="del_lid_" + item.get("id", ""),
                        use_container_width=True
                    ):
                        guardado_liderazgo = [
                            g for g in guardado_liderazgo if g.get("id") != item.get("id")
                        ]
                        guardar_datos_json(LIDERAZGO_GUARDADO_FILE, guardado_liderazgo)
                        st.rerun()

    st.stop()



if modo == "Matrimonio en Crecimiento":
    st.title("💍 Matrimonio en Crecimiento")
    st.caption("Recursos bíblicos y prácticos para fortalecer la comunicación, el amor, la fe y la unidad en pareja.")

    def guardar_matrimonio(tipo, titulo, contenido):
        guardado = cargar_datos_json(MATRIMONIO_GUARDADO_FILE)
        if not isinstance(guardado, list):
            guardado = []

        guardado.append({
            "id": str(uuid.uuid4())[:8],
            "tipo": tipo,
            "titulo": titulo,
            "contenido": contenido,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        guardar_datos_json(MATRIMONIO_GUARDADO_FILE, guardado)

    def desarrollar_matrimonio(titulo, idea_base, clave):
        st.write(idea_base)
        clave_respuesta = "matrimonio_respuesta_" + clave

        if st.button("✨ Desarrollar con IA", key="btn_matrimonio_" + clave, use_container_width=True):
            prompt = f"""Actúa como un consejero matrimonial cristiano, pastor y maestro bíblico responsable.

Desarrolla una enseñanza práctica para un matrimonio cristiano.

Tema: {titulo}
Idea base: {idea_base}

Escribe en español, con tono pastoral, respetuoso, esperanzador y cristocéntrico.
Incluye:
1. Una breve introducción.
2. Principios bíblicos aplicables, sin inventar versículos.
3. Acciones prácticas que ambos esposos puedan realizar.
4. Una pregunta para conversar en pareja.
5. Una oración final breve.

No juzgues ni des consejos manipuladores. Si hay violencia, abuso o peligro, recomienda buscar ayuda profesional y protección inmediata."""
            try:
                with st.spinner("Preparando contenido para la pareja..."):
                    respuesta = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system",
                                "content": "Eres un consejero matrimonial cristiano prudente, bíblico, compasivo y práctico."
                            },
                            {"role": "user", "content": prompt}
                        ]
                    ).choices[0].message.content
                st.session_state[clave_respuesta] = respuesta
            except Exception as e:
                st.error(f"No se pudo generar el contenido: {e}")

        if st.session_state.get(clave_respuesta):
            st.markdown("### 💬 Desarrollo para la pareja")
            st.markdown(st.session_state[clave_respuesta])

            if st.button("💾 Guardar contenido", key="guardar_matrimonio_" + clave, use_container_width=True):
                guardar_matrimonio("Enseñanza", titulo, st.session_state[clave_respuesta])
                st.success("Contenido guardado correctamente.")

    tab_estudios, tab_conexion, tab_circunstancias, tab_preguntas, tab_guardado_m = st.tabs([
        "📖 Estudios bíblicos",
        "💞 Dinámicas de conexión",
        "🧭 Circunstancias específicas",
        "❓ Preguntas frecuentes",
        "📂 Guardado"
    ])

    with tab_estudios:
        st.subheader("Fundamentos para crecer juntos")
        estudios = [
            ("El pacto y la unidad", "El matrimonio es una alianza de amor, fidelidad, servicio y compromiso delante de Dios."),
            ("Comunicación con gracia", "Escuchar con atención y responder con mansedumbre protege la unidad del hogar."),
            ("Perdón y restauración", "Perdonar no niega el dolor; abre un camino de verdad, arrepentimiento y restauración."),
            ("Amor que sirve", "El amor bíblico busca el bien del otro, honra, cuida y da lugar a la humildad."),
            ("Fe compartida en el hogar", "Orar, leer la Palabra y tomar decisiones buscando a Dios fortalece la vida matrimonial.")
        ]

        for indice, (titulo, idea) in enumerate(estudios):
            with st.expander(f"📖 {titulo}"):
                desarrollar_matrimonio(titulo, idea, f"estudio_{indice}")

        st.divider()
        st.markdown("#### 🤖 Genera un estudio bíblico según su situación")
        tema_estudio = st.text_area(
            "Escribe un tema o situación que quieran estudiar como pareja",
            placeholder="Ejemplo: Cómo cultivar el perdón después de una ofensa recurrente.",
            key="input_tema_estudio_matrimonio"
        )

        if st.button("✨ Generar estudio bíblico", key="generar_estudio_personalizado", use_container_width=True):
            if tema_estudio.strip():
                prompt_estudio = f"""Actúa como consejero matrimonial cristiano y maestro bíblico prudente.

Tema o situación de la pareja: {tema_estudio}

Crea un estudio bíblico breve para esta pareja, en español, con esta estructura:

1. Título del estudio.
2. Introducción breve (2-3 líneas) sobre la relevancia del tema para el matrimonio.
3. Base bíblica: incluye de 1 a 3 pasajes relevantes (libro, capítulo y versículo). No inventes citas textuales; si no estás seguro de la cita exacta, menciona solo la referencia y explica el principio con tus propias palabras.
4. Explicación de cómo cada pasaje aplica a la vida matrimonial.
5. Tres preguntas de discusión para conversar en pareja.
6. Una oración breve de cierre.

Sé claro, práctico y evita tecnicismos teológicos innecesarios."""
                try:
                    with st.spinner("Preparando el estudio bíblico..."):
                        respuesta_estudio = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "Eres un consejero matrimonial cristiano y maestro bíblico prudente, claro y práctico."},
                                {"role": "user", "content": prompt_estudio}
                            ]
                        ).choices[0].message.content
                    st.session_state["respuesta_estudio_personalizado"] = respuesta_estudio
                except Exception as e:
                    st.error(f"No se pudo generar el estudio: {e}")
            else:
                st.warning("Escribe un tema o situación antes de continuar.")

        if st.session_state.get("respuesta_estudio_personalizado"):
            st.markdown("### 📖 Estudio bíblico personalizado")
            st.markdown(st.session_state["respuesta_estudio_personalizado"])
            if st.button("💾 Guardar estudio personalizado", key="guardar_estudio_personalizado", use_container_width=True):
                guardar_matrimonio("Estudio personalizado", tema_estudio.strip() or "Estudio bíblico personalizado", st.session_state["respuesta_estudio_personalizado"])
                st.success("Estudio guardado correctamente.")


    with tab_conexion:
        st.subheader("Tiempo intencional para fortalecer la relación")
        dinamicas = [
            ("La conversación de gratitud", [
                "Cada uno comparte tres cosas que agradece del otro.",
                "Eviten corregir, debatir o minimizar lo que el otro diga.",
                "Terminen orando y dando gracias a Dios por su matrimonio."
            ]),
            ("Escucha de corazón", [
                "Uno habla durante cinco minutos sobre algo que está sintiendo.",
                "El otro escucha sin interrumpir ni ofrecer soluciones de inmediato.",
                "Quien escuchó resume lo entendido y pregunta: “¿Te comprendí bien?”.",
                "Luego intercambien los roles."
            ]),
            ("Nuestra visión de hogar", [
                "Conversen sobre cómo desean que sea su hogar dentro de un año.",
                "Escriban tres valores que quieren practicar como familia.",
                "Elijan una acción concreta para comenzar esta semana.",
                "Oren pidiendo sabiduría y unidad."
            ])
        ]

        for indice, (titulo, pasos) in enumerate(dinamicas):
            with st.expander(f"💞 {titulo}"):
                for paso in pasos:
                    st.write("• " + paso)

                contenido_dinamica = "\n".join(f"• {paso}" for paso in pasos)

                col_guardar, col_ampliar = st.columns(2)
                with col_guardar:
                    if st.button("💾 Guardar dinámica", key=f"guardar_dinamica_{indice}", use_container_width=True):
                        guardar_matrimonio("Dinámica", titulo, contenido_dinamica)
                        st.success("Dinámica guardada correctamente.")

                clave_ia = f"dinamica_ia_{indice}"
                clave_resp_ia = "matrimonio_respuesta_" + clave_ia

                with col_ampliar:
                    if st.button("✨ Ampliar con IA", key="btn_" + clave_ia, use_container_width=True):
                        prompt_dinamica = (
                            "Actúa como consejero matrimonial cristiano, prudente y práctico.\n\n"
                            f"Dinámica: {titulo}\n"
                            f"Pasos:\n{contenido_dinamica}\n\n"
                            "Desarrolla en español:\n"
                            "1. Por qué esta dinámica fortalece el matrimonio (sin inventar versículos).\n"
                            "2. Dos variaciones útiles según la etapa de la pareja.\n"
                            "3. Una pregunta de reflexión adicional.\n"
                            "4. Una oración breve para cerrar."
                        )
                        try:
                            with st.spinner("Preparando contenido..."):
                                respuesta_ia = client.chat.completions.create(
                                    model="gpt-4o-mini",
                                    messages=[
                                        {"role": "system", "content": "Eres un consejero matrimonial cristiano prudente, bíblico y práctico."},
                                        {"role": "user", "content": prompt_dinamica}
                                    ]
                                ).choices[0].message.content
                            st.session_state[clave_resp_ia] = respuesta_ia
                        except Exception as e:
                            st.error(f"No se pudo generar el contenido: {e}")

                if st.session_state.get(clave_resp_ia):
                    st.markdown("### 💬 Ampliación con IA")
                    st.markdown(st.session_state[clave_resp_ia])
                    if st.button("💾 Guardar ampliación", key="guardar_" + clave_ia, use_container_width=True):
                        guardar_matrimonio("Dinámica ampliada", titulo, st.session_state[clave_resp_ia])
                        st.success("Ampliación guardada correctamente.")

        st.divider()
        st.markdown("#### 🤖 ¿Quieres otra dinámica o idea personalizada?")
        pregunta_dinamica = st.text_area(
            "Pídele a la IA una dinámica según tu situación",
            placeholder="Ejemplo: Necesitamos una dinámica para reconectar después de una discusión fuerte.",
            key="input_pregunta_dinamica"
        )

        if st.button("✨ Generar dinámica personalizada", key="btn_pregunta_dinamica", use_container_width=True):
            if pregunta_dinamica.strip():
                prompt_personalizada = (
                    "Actúa como consejero matrimonial cristiano, creativo y práctico.\n\n"
                    f"Situación o pedido de la pareja: {pregunta_dinamica}\n\n"
                    "Crea una dinámica de conexión matrimonial en español con:\n"
                    "1. Un título breve.\n"
                    "2. Entre 3 y 5 pasos claros y prácticos.\n"
                    "3. Una pregunta de reflexión para conversar en pareja.\n"
                    "4. Una oración breve para cerrar.\n"
                    "No inventes versículos bíblicos."
                )
                try:
                    with st.spinner("Creando una dinámica para ustedes..."):
                        respuesta_personalizada = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "Eres un consejero matrimonial cristiano creativo, prudente y práctico."},
                                {"role": "user", "content": prompt_personalizada}
                            ]
                        ).choices[0].message.content
                    st.session_state["respuesta_pregunta_dinamica"] = respuesta_personalizada
                except Exception as e:
                    st.error(f"No se pudo generar la dinámica: {e}")
            else:
                st.warning("Escribe una situación o pedido antes de continuar.")

        if st.session_state.get("respuesta_pregunta_dinamica"):
            st.markdown("### 💬 Dinámica personalizada")
            st.markdown(st.session_state["respuesta_pregunta_dinamica"])
            if st.button("💾 Guardar dinámica personalizada", key="guardar_pregunta_dinamica", use_container_width=True):
                guardar_matrimonio("Dinámica personalizada", "Dinámica generada por IA", st.session_state["respuesta_pregunta_dinamica"])
                st.success("Dinámica guardada correctamente.")


    with tab_circunstancias:
        st.subheader("Orientación para situaciones reales")
        circunstancias = [
            ("Manejo de conflictos", "Cómo conversar cuando hay desacuerdos sin herir, ignorar ni acumular resentimiento."),
            ("Finanzas en pareja", "Cómo construir transparencia, orden, prioridades y acuerdos económicos saludables."),
            ("Crianza y diferencias familiares", "Cómo buscar unidad al tomar decisiones sobre hijos, límites y relaciones familiares."),
            ("Intimidad, afecto y cercanía", "Cómo hablar con respeto sobre necesidades emocionales y físicas dentro del matrimonio."),
            ("Cansancio, rutina y distancia emocional", "Cómo recuperar espacios de conexión, descanso, conversación y oración juntos.")
        ]

        for indice, (titulo, idea) in enumerate(circunstancias):
            with st.expander(f"🧭 {titulo}"):
                desarrollar_matrimonio(titulo, idea, f"circunstancia_{indice}")

        st.warning("Si existe violencia, amenazas, abuso, control coercitivo o peligro inmediato, busca ayuda local profesional y protección urgente. La reconciliación nunca debe exigir tolerar el abuso.")

    with tab_preguntas:
        st.subheader("Preguntas frecuentes sobre el matrimonio")

        faq_matrimonio = [
            ("¿Qué hacemos cuando ya no sabemos cómo comunicarnos?",
             "Es común llegar a sentir que las palabras ya no conectan. El primer paso no es hablar más, sino escuchar mejor: separen un momento sin distracciones, sin corregir ni interrumpir, y practiquen resumir lo que el otro dice antes de responder. La comunicación sana se reconstruye con paciencia, no con un solo intento.",
             "Santiago 1:19 — \"...todo hombre sea pronto para oír, tardo para hablar, tardo para airarse.\""),

            ("¿Es normal discutir tanto en el matrimonio?",
             "Sí, el conflicto en sí no es el problema; cómo se maneja sí lo es. Discutir con respeto, sin insultos ni desprecio, y buscando entender (no solo ganar), puede fortalecer la relación. Lo preocupante es el desprecio constante, el silencio prolongado como castigo, o la falta total de reparación después del conflicto.",
             "Efesios 4:26 — \"Airaos, pero no pequéis; no se ponga el sol sobre vuestro enojo.\""),

            ("¿Cómo recuperamos la intimidad y cercanía que sentíamos antes?",
             "La cercanía se construye con pequeños hábitos sostenidos: tiempo a solas sin pantallas, gestos de afecto cotidianos, conversaciones honestas sobre necesidades y expectativas, y también paciencia mutua. No suele regresar de golpe, sino con constancia semana tras semana.",
             "Génesis 2:24 — \"...dejará el hombre a su padre y a su madre, y se unirá a su mujer, y serán una sola carne.\""),

            ("¿Qué hacer si sentimos que ya no tenemos nada en común?",
             "Esto suele pasar cuando la rutina y las responsabilidades ocupan todo el espacio. Es momento de preguntarse juntos: ¿qué disfrutábamos hacer al inicio? ¿qué proyecto pequeño podemos compartir hoy? Reconstruir intereses comunes, aunque sean nuevos, ayuda a renovar la conexión.",
             "Eclesiastés 4:9-10 — \"Mejor son dos que uno... porque si cayeren, el uno levantará a su compañero.\""),

            ("¿Cómo manejamos las diferencias de opinión sobre la crianza de los hijos?",
             "Es clave hablarlo en privado, no frente a los hijos, y buscar acuerdos básicos antes de que surja el conflicto (no en medio de él). Ambos padres pueden tener estilos distintos, pero necesitan mostrar unidad hacia los hijos, aunque negocien los detalles a solas.",
             "Amós 3:3 — \"¿Andarán dos juntos, si no estuvieren de acuerdo?\""),

            ("¿Qué hacemos si el dinero se ha vuelto motivo constante de conflicto?",
             "Las finanzas suelen reflejar valores y miedos distintos. Ayuda establecer una conversación regular (no solo cuando hay tensión), ser transparentes con ingresos y gastos, y definir juntos prioridades y límites claros, en lugar de decisiones unilaterales.",
             "Proverbios 24:3-4 — \"Con sabiduría se edifica la casa, y con prudencia se afirma.\""),

            ("¿Es posible sanar después de una infidelidad?",
             "Es posible, pero requiere tiempo, verdad completa, arrepentimiento genuino y, en la mayoría de los casos, acompañamiento profesional o pastoral. La sanidad no significa minimizar el dolor, sino procesarlo con honestidad antes de intentar reconstruir la confianza.",
             "1 Corintios 13:7 — \"Todo lo sufre, todo lo cree, todo lo espera, todo lo soporta.\""),

            ("¿Qué hacemos cuando uno quiere trabajar en la relación y el otro no muestra interés?",
             "No se puede forzar el cambio del otro, pero sí se puede sostener el propio esfuerzo con humildad, sin manipular ni presionar. En muchos casos, buscar un espacio neutral (consejería, un mentor, un pastor) ayuda a abrir el diálogo cuando la comunicación directa está estancada.",
             "Romanos 12:18 — \"Si es posible, en cuanto dependa de vosotros, estad en paz con todos los hombres.\""),

            ("¿Cómo sabemos si necesitamos ayuda profesional o pastoral?",
             "Si el conflicto es constante, si hay heridas del pasado sin resolver, si sienten que no logran avanzar solos, o si existe cualquier forma de abuso o control, buscar ayuda profesional no es un fracaso: es un acto de responsabilidad y cuidado hacia el matrimonio.",
             "Proverbios 11:14 — \"En la multitud de consejeros hay seguridad.\""),

            ("¿Qué lugar debe tener la fe en medio de las dificultades matrimoniales?",
             "La fe no elimina los problemas, pero da un marco de esperanza, humildad y propósito compartido. Orar juntos, buscar sabiduría más allá de uno mismo, y recordar el compromiso original del pacto matrimonial, ayuda a sostener el proceso incluso en tiempos difíciles.",
             "Eclesiastés 4:12 — \"...cordón de tres dobleces no se rompe pronto.\"")
        ]

        for indice, (pregunta, respuesta, versiculo) in enumerate(faq_matrimonio):
            with st.expander(f"❓ {pregunta}"):
                st.write(respuesta)
                st.markdown(f"📖 *{versiculo}*")
                contenido_faq_guardar = respuesta + "\n\n📖 " + versiculo
                if st.button("💾 Guardar respuesta", key=f"guardar_faq_{indice}", use_container_width=True):
                    guardar_matrimonio("Pregunta frecuente", pregunta, contenido_faq_guardar)
                    st.success("Guardado correctamente.")

        st.divider()
        st.markdown("#### 🤖 ¿Tu pregunta no está en la lista?")
        pregunta_matrimonio = st.text_area(
            "Escribe tu propia pregunta sobre tu matrimonio",
            placeholder="Ejemplo: ¿Cómo podemos volver a hablar con respeto después de una discusión?"
        )

        if st.button("🤖 Obtener orientación", key="preguntar_matrimonio", use_container_width=True):
            if pregunta_matrimonio.strip():
                prompt = f"""Responde como un consejero matrimonial cristiano prudente y compasivo.

Pregunta: {pregunta_matrimonio}

Da orientación práctica, respetuosa y fundamentada en principios bíblicos.

Organiza la respuesta con estos apartados:
1. Orientación para la situación.
2. Base bíblica: incluye de 1 a 3 pasajes bíblicos relevantes, indicando libro, capítulo y versículo.
3. Explica brevemente cómo aplicar cada pasaje a la situación de la pareja.
4. Pasos conversables y prácticos para realizar esta semana.
5. Una oración breve.

No inventes versículos, referencias ni citas bíblicas. Si no estás seguro de una cita textual, menciona únicamente la referencia y explica el principio con tus propias palabras.
No diagnostiques problemas clínicos.
Si el tema incluye violencia, abuso, amenazas o peligro, prioriza la seguridad y la ayuda profesional/local; la reconciliación nunca debe exigir tolerar el abuso."""
                try:
                    with st.spinner("Preparando orientación..."):
                        respuesta = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "Eres un consejero matrimonial cristiano responsable, compasivo y práctico."},
                                {"role": "user", "content": prompt}
                            ]
                        ).choices[0].message.content
                    st.session_state["respuesta_pregunta_matrimonio"] = respuesta
                except Exception as e:
                    st.error(f"No se pudo generar la respuesta: {e}")
            else:
                st.warning("Escribe una pregunta antes de continuar.")

        if st.session_state.get("respuesta_pregunta_matrimonio"):
            st.markdown(st.session_state["respuesta_pregunta_matrimonio"])
            if st.button("💾 Guardar esta orientación", key="guardar_respuesta_pregunta_matrimonio", use_container_width=True):
                guardar_matrimonio("Pregunta personalizada", pregunta_matrimonio.strip() or "Pregunta personalizada", st.session_state["respuesta_pregunta_matrimonio"])
                st.success("Guardado correctamente.")

    with tab_guardado_m:
        st.subheader("Contenidos guardados")
        guardado_matrimonio = cargar_datos_json(MATRIMONIO_GUARDADO_FILE)

        if not isinstance(guardado_matrimonio, list) or not guardado_matrimonio:
            st.info("Todavía no tienes contenidos guardados.")
        else:
            for item in reversed(guardado_matrimonio):
                titulo_item = item.get("titulo", "Contenido sin título")
                with st.expander(f"{item.get('tipo', 'Contenido')} · {titulo_item}"):
                    st.caption(item.get("fecha", ""))
                    st.markdown(item.get("contenido", ""))

                    col_descarga, col_eliminar = st.columns(2)
                    with col_descarga:
                        st.download_button(
                            "⬇️ Descargar",
                            data=item.get("contenido", ""),
                            file_name=titulo_item.replace(" ", "_") + ".txt",
                            mime="text/plain",
                            key="descargar_matrimonio_" + item.get("id", "")
                        )
                    with col_eliminar:
                        if st.button("🗑️ Eliminar", key="eliminar_matrimonio_" + item.get("id", "")):
                            guardado_matrimonio = [
                                g for g in guardado_matrimonio if g.get("id") != item.get("id")
                            ]
                            guardar_datos_json(MATRIMONIO_GUARDADO_FILE, guardado_matrimonio)
                            st.rerun()

    st.stop()

if modo == "Reuniones de Equipo":
    st.title("🗓️ Reuniones de Equipo")
    st.caption("Planificación, alineación ministerial, oración en equipo y facilitación con IA.")

    tab_preparar, tab_alinear, tab_unidad, tab_asistente = st.tabs([
        "📋 Preparar Agenda",
        "🎯 Alinear Objetivos",
        "🙏 Peticiones del Equipo",
        "🤖 Asistente de Reuniones"
    ])

    agendas = cargar_datos_json(AGENDAS_FILE)
    objetivos = cargar_datos_json(OBJETIVOS_EQUIPO_FILE)
    oraciones = cargar_datos_json(ORACION_EQUIPO_FILE)

    # ---------------- TAB 1: PREPARAR AGENDA ----------------
    with tab_preparar:
        st.subheader("Planificador de Reuniones")
        
        with st.form("form_nueva_agenda"):
            col_t, col_f = st.columns([2, 1])
            titulo_agenda = col_t.text_input("Título / Motivo de la reunión", placeholder="Ej: Planificación mensual de alabanza / Célula líderes")
            fecha_reunion = col_f.date_input("Fecha de la reunión", value=datetime.today())
            
            tipo_reunion = st.selectbox("Tipo de Reunión", [
                "Reunión de Liderazgo General",
                "Reunión de Ministerio (Alabanza, Jóvenes, Niños, etc.)",
                "Evaluación y Retroalimentación",
                "Planificación de Evento Especial",
                "Devocional y Oración del Equipo",
                "Personalizada"
            ])
            
            duracion = st.select_slider("Duración estimada", options=["30 min", "45 min", "1 hora", "1.5 horas", "2 horas"], value="1 hora")
            
            st.markdown("##### Bloques de la Agenda")
            col_b1, col_b2 = st.columns(2)
            b1 = col_b1.text_input("1. Apertura / Conexión (Minutos + Tema)", value="10 min - Oración y bienvenida")
            b2 = col_b2.text_input("2. Devocional / Reflexión", value="15 min - Pasaje bíblico y alineación")
            b3 = col_b1.text_input("3. Puntos clave / Trabajo", value="25 min - Revisión de metas y tareas")
            b4 = col_b2.text_input("4. Acuerdos y Cierre", value="10 min - Compromisos y oración final")
            
            notas_agenda = st.text_area("Notas o Materiales Necesarios", height=80, placeholder="Ej: Llevar proyector, traer lista de nuevos miembros...")
            
            guardar_ag = st.form_submit_button("Guardar Agenda de Reunión", use_container_width=True)
            if guardar_ag:
                if titulo_agenda.strip():
                    nueva_ag = {
                        "id": str(uuid.uuid4())[:8],
                        "titulo": titulo_agenda.strip(),
                        "fecha": fecha_reunion.strftime("%Y-%m-%d"),
                        "tipo": tipo_reunion,
                        "duracion": duracion,
                        "bloques": [b1.strip(), b2.strip(), b3.strip(), b4.strip()],
                        "notas": notas_agenda.strip(),
                        "creado_en": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    agendas.append(nueva_ag)
                    guardar_datos_json(AGENDAS_FILE, agendas)
                    st.success("Agenda guardada correctamente.")
                    st.rerun()
                else:
                    st.warning("Por favor ingresa un título para la reunión.")

        st.divider()
        st.subheader("Agendas Registradas")
        if agendas:
            for ag in reversed(agendas):
                with st.expander(f"📅 {ag['fecha']} — {ag['titulo']} ({ag['duracion']})"):
                    st.markdown(f"**Tipo:** {ag['tipo']}")
                    st.markdown("**Estructura:**")
                    for bloque in ag.get("bloques", []):
                        if bloque:
                            st.write(f"- {bloque}")
                    if ag.get("notas"):
                        st.info(f"📌 **Notas:** {ag['notas']}")
                    if st.button("Eliminar Agenda", key="del_ag_" + ag["id"]):
                        agendas = [a for a in agendas if a["id"] != ag["id"]]
                        guardar_datos_json(AGENDAS_FILE, agendas)
                        st.rerun()
        else:
            st.info("No hay agendas guardadas aún.")

    # ---------------- TAB 2: ALINEAR OBJETIVOS ----------------
    with tab_alinear:
        st.subheader("Objetivos y Metas del Equipo")
        
        with st.form("form_nuevo_objetivo"):
            col_meta, col_resp = st.columns([2, 1])
            meta = col_meta.text_input("Objetivo o Compromiso", placeholder="Ej: Visitar 5 familias este mes")
            responsable = col_resp.text_input("Responsable(s)", placeholder="Ej: Hermano Juan / Equipo Alabanza")
            col_plazo, col_estado = st.columns(2)
            fecha_limite = col_plazo.date_input("Fecha Límite", value=datetime.today())
            estado = col_estado.selectbox("Estado", ["Pendiente ⏳", "En Proceso 🚀", "Completado ✅"])
            
            guardar_obj = st.form_submit_button("Agregar Objetivo", use_container_width=True)
            if guardar_obj:
                if meta.strip():
                    nuevo_obj = {
                        "id": str(uuid.uuid4())[:8],
                        "meta": meta.strip(),
                        "responsable": responsable.strip() if responsable.strip() else "Equipo",
                        "fecha_limite": fecha_limite.strftime("%Y-%m-%d"),
                        "estado": estado,
                        "creado_en": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    objetivos.append(nuevo_obj)
                    guardar_datos_json(OBJETIVOS_EQUIPO_FILE, objetivos)
                    st.success("Objetivo agregado.")
                    st.rerun()
                else:
                    st.warning("Escribe el objetivo antes de guardar.")

        st.divider()
        st.subheader("Seguimiento de Metas")
        if objetivos:
            for obj in objetivos:
                c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                c1.markdown(f"**{obj['meta']}**")
                c1.caption(f"Responsable: {obj.get('responsable', 'Equipo')}")
                c2.markdown(f"📅 *Límite:* {obj.get('fecha_limite', 'N/A')}")
                c3.markdown(f"**{obj.get('estado', 'Pendiente')}**")
                if c4.button("Borrar", key="del_obj_" + obj["id"]):
                    objetivos = [o for o in objetivos if o["id"] != obj["id"]]
                    guardar_datos_json(OBJETIVOS_EQUIPO_FILE, objetivos)
                    st.rerun()
                st.divider()
        else:
            st.info("No hay objetivos asignados actualmente.")

    # ---------------- TAB 3: UNIDAD Y ORACIÓN ----------------
    with tab_unidad:
        st.subheader("Motivos de Oración y Cuidado Mutuo")
        
        with st.form("form_oracion_equipo"):
            col_sol, col_cat = st.columns([2, 1])
            peticion = col_sol.text_input("Petición de Oración / Motivo de Agradecimiento", placeholder="Ej: Salud de la familia de María, provisión económica...")
            categoria_oracion = col_cat.selectbox("Categoría", ["Salud / Sanidad", "Familia / Matrimonio", "Ministerio / Servicio", "Gratitud / Testimonio", "Provisión / Trabajo", "Otro"])
            miembro = st.text_input("Compartido por", placeholder="Nombre del miembro del equipo")
            
            guardar_or = st.form_submit_button("Registrar Motivo de Oración", use_container_width=True)
            if guardar_or:
                if peticion.strip():
                    nueva_or = {
                        "id": str(uuid.uuid4())[:8],
                        "peticion": peticion.strip(),
                        "categoria": categoria_oracion,
                        "miembro": miembro.strip() if miembro.strip() else "Anónimo",
                        "fecha": datetime.now().strftime("%Y-%m-%d")
                    }
                    oraciones.append(nueva_or)
                    guardar_datos_json(ORACION_EQUIPO_FILE, oraciones)
                    st.success("Petición registrada para orar juntos.")
                    st.rerun()
                else:
                    st.warning("Por favor detalla la petición.")

        st.divider()
        st.subheader("Lista de Oración del Equipo")
        if oraciones:
            for o in reversed(oraciones):
                co1, co2, co3 = st.columns([4, 2, 1])
                co1.markdown(f"🙏 **{o['peticion']}**")
                co1.caption(f"Por: {o.get('miembro', 'Anónimo')} | {o.get('categoria', 'General')}")
                co2.caption(f"Registrado: {o.get('fecha', '')}")
                if co3.button("Eliminar", key="del_or_" + o["id"]):
                    oraciones = [item for item in oraciones if item["id"] != o["id"]]
                    guardar_datos_json(ORACION_EQUIPO_FILE, oraciones)
                    st.rerun()
                st.divider()
        else:
            st.info("No hay motivos de oración registrados.")

    # ---------------- TAB 4: ASISTENTE IA ----------------
    with tab_asistente:
        st.subheader("🤖 Asistente IA para Reuniones de Liderazgo")
        st.write("Genera dinámicas rompehielos, devocionales de 5 minutos, preguntas de alineación o resuelve situaciones prácticas del equipo.")
        
        consulta_reunion = st.text_area("¿Qué necesitas preparar para tu reunión?", placeholder="Ej: Dame un devocional de 5 minutos sobre la unidad para el equipo de alabanza con 2 preguntas de reflexión.")
        if st.button("Consultar Asistente de Reunión", use_container_width=True, key="btn_ia_reuniones"):
            if consulta_reunion.strip():
                with st.spinner("Generando sugerencias bíblicas y prácticas..."):
                    respuesta = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Eres un mentor y facilitador cristiano experto en guiar reuniones de equipo y ministerios con sabiduría pastoral, orden y empatía. Proporciona ideas prácticas, bíblicas, dinámicas participativas y devocionales concisos."},
                            {"role": "user", "content": consulta_reunion}
                        ]
                    ).choices[0].message.content
                st.session_state["resp_ia_reunion"] = respuesta

        if st.session_state.get("resp_ia_reunion"):
            st.markdown("### 💡 Recomendación:")
            st.info(st.session_state["resp_ia_reunion"])

    st.stop()




def _sanitizar_texto_pdf(texto):
    if not texto:
        return ""
    reemplazos = {
        "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-",
        "\u00a0": " ", "\u2026": "...",
        "\t": "    ",
    }
    for k, v in reemplazos.items():
        texto = texto.replace(k, v)
    return texto


def _forzar_saltos_palabras_largas(texto, max_len=35):
    palabras = texto.split(" ")
    resultado = []
    for palabra in palabras:
        if len(palabra) > max_len:
            trozos = [palabra[i:i + max_len] for i in range(0, len(palabra), max_len)]
            resultado.append(" ".join(trozos))
        else:
            resultado.append(palabra)
    return " ".join(resultado)


def _preparar_texto_pdf(texto):
    texto = _sanitizar_texto_pdf(texto or "")
    texto = texto.encode("latin-1", "replace").decode("latin-1")
    lineas = texto.split("\n")
    lineas = [_forzar_saltos_palabras_largas(linea, 35) for linea in lineas]
    return "\n".join(lineas)


def crear_pdf_podcast(titulo, contenido_guion):
    pdf = FPDF()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    titulo_seguro = _preparar_texto_pdf(titulo or "Episodio de podcast").strip()
    if not titulo_seguro:
        titulo_seguro = "Episodio de podcast"

    if os.path.exists(LOGO_PATH):
        try:
            pdf.image(LOGO_PATH, x=pdf.l_margin, y=pdf.t_margin, w=18, h=18)
        except Exception:
            pass

    # Siempre regresar al margen izquierdo antes de escribir.
    pdf.set_xy(pdf.l_margin + 24, pdf.t_margin)
    pdf.set_text_color(*COLOR_AZUL_MARCA_RGB)
    pdf.set_font("Helvetica", "B", 18)
    pdf.multi_cell(pdf.epw - 24, 10, "Conectados con el Evangelio")

    pdf.set_x(pdf.l_margin)
    pdf.set_text_color(*COLOR_DORADO_MARCA_RGB)
    pdf.set_font("Helvetica", "B", 14)
    pdf.multi_cell(pdf.epw, 8, titulo_seguro)

    pdf.ln(4)
    pdf.set_text_color(20, 20, 20)
    pdf.set_font("Helvetica", "", 11)

    texto_limpio = _preparar_texto_pdf(contenido_guion)

    for linea in texto_limpio.split("\n"):
        linea = linea.strip()

        if not linea:
            pdf.ln(4)
        else:
            # FPDF2 mueve el cursor después de multi_cell;
            # por eso lo devolvemos al margen en cada línea.
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(pdf.epw, 6, linea)

    return bytes(pdf.output())


TEMAS_BIBLICOS_PODCAST = {
    "Selecciona un tema sugerido (opcional)": {
        "tema": "",
        "texto": "",
        "enfoque": ""
    },
    "¿Quién es Jesús realmente?": {
        "tema": "¿Quién es Jesús y por qué importa conocerlo?",
        "texto": "Juan 14:6",
        "enfoque": "Presentar a Jesús como el camino, la verdad y la vida para personas que buscan respuestas."
    },
    "El amor de Dios por ti": {
        "tema": "El amor de Dios cuando sientes que no eres suficiente",
        "texto": "Juan 3:16",
        "enfoque": "Explicar el amor de Dios como un regalo de gracia y no como una recompensa por portarse bien."
    },
    "La cruz y el perdón": {
        "tema": "¿Puede Dios perdonar mi pasado?",
        "texto": "Romanos 5:8",
        "enfoque": "Conectar la culpa, el arrepentimiento y el perdón con el sacrificio de Jesús en la cruz."
    },
    "La resurrección y la esperanza": {
        "tema": "La esperanza que vence incluso a la muerte",
        "texto": "Juan 11:25-26",
        "enfoque": "Explicar que la resurrección de Jesús ofrece esperanza real frente al dolor, el duelo y el temor."
    },
    "Volver a Dios": {
        "tema": "¿Puedo volver a Dios después de haberme alejado?",
        "texto": "Lucas 15:20",
        "enfoque": "Mostrar el corazón del Padre que recibe al hijo pródigo con misericordia."
    },
    "Identidad en Cristo": {
        "tema": "Tu valor no depende de lo que logras",
        "texto": "2 Corintios 5:17",
        "enfoque": "Hablar de la nueva identidad que Jesús da a quienes creen en Él."
    },
    "Ansiedad y paz en Jesús": {
        "tema": "Cuando la ansiedad no te deja descansar",
        "texto": "Mateo 11:28",
        "enfoque": "Presentar la invitación de Jesús a descansar en Él en medio de las cargas."
    },
    "Propósito de vida": {
        "tema": "¿Para qué estoy aquí?",
        "texto": "Efesios 2:10",
        "enfoque": "Conectar el propósito personal con haber sido creados y llamados por Dios."
    },
    "Jesús y la mujer samaritana": {
        "tema": "La sed que nada de este mundo puede llenar",
        "texto": "Juan 4:13-14",
        "enfoque": "Mostrar que Jesús conoce nuestra historia y ofrece agua viva para el corazón."
    },
    "Zaqueo: cuando Jesús te encuentra": {
        "tema": "Jesús ve a quienes otros rechazan",
        "texto": "Lucas 19:1-10",
        "enfoque": "Explicar cómo un encuentro con Jesús transforma el corazón y las decisiones."
    },
    "Nicodemo: nacer de nuevo": {
        "tema": "¿Qué significa empezar de nuevo con Dios?",
        "texto": "Juan 3:3",
        "enfoque": "Explicar con sencillez el nuevo nacimiento y la fe en Jesús."
    },
    "Fe cuando hay dudas": {
        "tema": "¿Qué hago cuando tengo dudas sobre Dios?",
        "texto": "Marcos 9:24",
        "enfoque": "Mostrar que Jesús recibe la fe honesta, aun cuando viene acompañada de dudas."
    },
    "Esperanza en medio del dolor": {
        "tema": "¿Dónde está Dios cuando duele?",
        "texto": "Salmo 34:18",
        "enfoque": "Hablar de la cercanía de Dios con el quebrantado y de la esperanza que Cristo ofrece."
    },
    "La Gran Comisión": {
        "tema": "Compartir a Jesús sin miedo ni presión",
        "texto": "Mateo 28:18-20",
        "enfoque": "Animar a los oyentes a compartir el Evangelio con amor, respeto y claridad."
    },
    "Cómo contar tu testimonio": {
        "tema": "Cómo compartir tu historia y apuntar a Jesús",
        "texto": "Apocalipsis 12:11",
        "enfoque": "Enseñar una estructura sencilla para contar un testimonio sin ponerse a uno mismo en el centro."
    }
}




TEMPORADAS_RECOMENDADAS_DATA = {
    "Temporada 1: Volver a lo Esencial": [
        {"n": 1, "titulo": "¿Quién es Jesús realmente?", "pasaje": "Juan 1:1-14", "resumen": "De la religión a la persona de Cristo."},
        {"n": 2, "titulo": "¿Por qué necesitamos salvación?", "pasaje": "Romanos 3:23", "resumen": "El problema del corazón humano."},
        {"n": 3, "titulo": "La Cruz: El amor que tomó nuestro lugar", "pasaje": "Romanos 5:8", "resumen": "La gracia incondicional."},
        {"n": 4, "titulo": "La Resurrección: Comenzar de nuevo con esperanza viva", "pasaje": "1 Corintios 15:3-4,20", "resumen": "Esperanza viva más allá de la muerte."},
        {"n": 5, "titulo": "¿Qué significa entregarse a Jesús?", "pasaje": "Marcos 1:15", "resumen": "Fe y arrepentimiento sincero."},
        {"n": 6, "titulo": "Vivir Conectados con el Evangelio cada día", "pasaje": "Juan 15:5", "resumen": "Permanecer en la Vid."}
    ],
    "Temporada 2: Paz en Medio de la Tormenta": [
        {"n": 1, "titulo": "Cuando la ansiedad no te deja descansar", "pasaje": "Mateo 11:28-30", "resumen": "Descanso real en Cristo."},
        {"n": 2, "titulo": "Sentirse solo rodeado de gente", "pasaje": "Hebreos 4:15", "resumen": "Jesús se compadece de nuestra soledad."},
        {"n": 3, "titulo": "Liberarse de la culpa y la vergüenza", "pasaje": "1 Juan 1:9", "resumen": "Perdón y limpieza genuina."},
        {"n": 4, "titulo": "¿Dónde está Dios en el sufrimiento?", "pasaje": "Juan 11:35", "resumen": "Jesús llora con nosotros."},
        {"n": 5, "titulo": "Vencer el miedo al futuro", "pasaje": "Mateo 6:25-34", "resumen": "Confianza en la provisión de Dios."},
        {"n": 6, "titulo": "Tu verdadera identidad en Cristo", "pasaje": "2 Corintios 5:17", "resumen": "Nueva criatura en Jesús."}
    ],
    "Temporada 3: Compartir a Jesús sin Miedo": [
        {"n": 1, "titulo": "Tu historia importa: Cómo contar tu testimonio", "pasaje": "Apocalipsis 12:11", "resumen": "Estructura sencilla del testimonio personal."},
        {"n": 2, "titulo": "El Evangelio en 3 minutos: Claridad sin rodeos", "pasaje": "1 Corintios 15:1-4", "resumen": "Explicar el Evangelio con sencillez."},
        {"n": 3, "titulo": "Conversaciones que sanan: Hablar con gracia y verdad", "pasaje": "Colosenses 4:5-6", "resumen": "Compartir con respeto y empatía."},
        {"n": 4, "titulo": "El poder de orar por quienes no creen", "pasaje": "1 Timoteo 2:1-4", "resumen": "Intercesión antes de hablar."},
        {"n": 5, "titulo": "La Gran Comisión en el mundo real", "pasaje": "Mateo 28:18-20", "resumen": "Vivir el llamado a diario."}
    ]
}

RUTAS_EVANGELIO = {
    "1. ¿Quién es Jesús? (Conocerle)": [
        {"nombre": "Jesús: Dios hecho hombre", "texto": "Juan 1:1-14", "enfoque": "Presentar la encarnación y cercanía de Dios en Jesús."},
        {"nombre": "Jesús, el Camino, la Verdad y la Vida", "texto": "Juan 14:6", "enfoque": "Jesús como respuesta única a la búsqueda humana de sentido."},
        {"nombre": "Jesús busca al perdido", "texto": "Lucas 19:10", "enfoque": "Mostrar el corazón compasivo de Jesús hacia quienes se sienten lejos."},
        {"nombre": "Jesús conoce tu historia íntima", "texto": "Juan 4:1-26", "enfoque": "La compasión de Cristo que conoce nuestras heridas sin rechazarnos."},
        {"nombre": "Jesús y los que tienen dudas", "texto": "Juan 20:24-29", "enfoque": "Cómo Jesús recibe la honestidad de Tomás con paciencia y amor."}
    ],
    "2. El Evangelio: La Buena Noticia (Fundamentos)": [
        {"nombre": "El amor incondicional de Dios", "texto": "Juan 3:16", "enfoque": "El amor divino demostrado en dar, no en exigir méritos previos."},
        {"nombre": "El problema del pecado y la separación", "texto": "Romanos 3:23", "enfoque": "Nuestra necesidad real de salvación sin caer en condenación legalista."},
        {"nombre": "La Cruz: Jesús tomó nuestro lugar", "texto": "Romanos 5:8", "enfoque": "La gracia de la sustitución y el perdón total de culpas."},
        {"nombre": "Salvación por gracia, no por obras", "texto": "Efesios 2:8-9", "enfoque": "Descanso del agotamiento de querer ganar el favor de Dios."},
        {"nombre": "La Resurrección: Esperanza viva", "texto": "1 Corintios 15:3-4,20", "enfoque": "La victoria sobre la muerte y la garantía de una vida nueva."},
        {"nombre": "¿Qué significa arrepentirse y creer?", "texto": "Marcos 1:15", "enfoque": "Cambio de rumbo de la mente y el corazón hacia Jesús."}
    ],
    "3. Encuentros que Transforman (Historias Bíblicas)": [
        {"nombre": "La Samaritana: La sed del alma", "texto": "Juan 4:13-14", "enfoque": "El agua viva que sacia el vacío que el mundo no puede llenar."},
        {"nombre": "Zaqueo: Cuando Jesús te ve", "texto": "Lucas 19:1-10", "enfoque": "La transformación y restitución que nacen de sentirse amado."},
        {"nombre": "Nicodemo: Nacer de nuevo", "texto": "Juan 3:1-8", "enfoque": "Un nuevo comienzo espiritual más allá de la religión externa."},
        {"nombre": "El Hijo Pródigo: El abrazo del Padre", "texto": "Lucas 15:11-32", "enfoque": "El retorno a casa y la fiesta de la misericordia del Padre."},
        {"nombre": "La mujer sorprendida en pecado: Gracia y verdad", "texto": "Juan 8:1-11", "enfoque": "Ni condena ni complicidad: perdón y libertad para no pecar más."},
        {"nombre": "Pedro: Restauración tras el fracaso", "texto": "Juan 21:15-19", "enfoque": "Jesús restaura tu propósito aun después de haberle fallado."}
    ],
    "4. Jesús en las Luchas Reales (Sanidad y Paz)": [
        {"nombre": "Ansiedad y descanso en Cristo", "texto": "Mateo 11:28-30", "enfoque": "El yugo fácil de Jesús frente al peso del rendimiento moderno."},
        {"nombre": "Soledad: Jesús ha estado allí", "texto": "Hebreos 4:15", "enfoque": "Un Sumo Sacerdote que se compadece de nuestras debilidades."},
        {"nombre": "Culpa, vergüenza y perdón genuino", "texto": "1 Juan 1:9", "enfoque": "La fidelidad de Dios para limpiar toda maldad y restaurar la paz."},
        {"nombre": "Dolor y duelo: Jesús lloró", "texto": "Juan 11:35", "enfoque": "La empatía de Dios frente a la pérdida y la esperanza eterna."},
        {"nombre": "Miedo al futuro y provisión", "texto": "Mateo 6:25-34", "enfoque": "Confiar en el cuidado diario del Padre celestial."},
        {"nombre": "Identidad: Quién eres en Cristo", "texto": "2 Corintios 5:17", "enfoque": "Nueva criatura: tu pasado ya no define tu valor ni tu destino."}
    ],
    "5. Seguir a Jesús Cada Día (Discipulado)": [
        {"nombre": "¿Cómo hablar con Dios? (La oración sencilla)", "texto": "Mateo 6:9-13", "enfoque": "La oración como relación íntima de hijos y no como repetición vacía."},
        {"nombre": "¿Cómo leer la Biblia y escuchar a Dios?", "texto": "Salmo 119:105", "enfoque": "Las Escrituras como lámpara para el camino diario."},
        {"nombre": "El Espíritu Santo: Nuestro Consolador y Guía", "texto": "Juan 14:16-17", "enfoque": "No caminamos en nuestras fuerzas, sino con su presencia viva."},
        {"nombre": "La comunidad: No estamos diseñados para estar solos", "texto": "Hebreos 10:24-25", "enfoque": "El valor vital de congregarse y caminar en hermandad."},
        {"nombre": "Perdonar a otros como fuimos perdonados", "texto": "Efesios 4:32", "enfoque": "La gracia recibida como motor para liberar rencores."},
        {"nombre": "Fe cuando aún quedan preguntas", "texto": "Marcos 9:24", "enfoque": "La honestidad del creyente: 'Creo, ayuda mi incredulidad'."}
    ],
    "6. Compartir a Jesús con Amor (Evangelismo Cercano)": [
        {"nombre": "Cómo contar tu testimonio con sencillez", "texto": "Apocalipsis 12:11", "enfoque": "Estructura simple: mi vida antes, el encuentro con Jesús y mi vida hoy."},
        {"nombre": "Explicar el Evangelio en 3 minutos", "texto": "1 Corintios 15:1-4", "enfoque": "Claridad cristocéntrica sin lenguaje técnico ni debates estériles."},
        {"nombre": "Compartir con gracia y sazón", "texto": "Colosenses 4:5-6", "enfoque": "Responder a las personas con respeto, prudencia y empatía."},
        {"nombre": "Orar por los que aún no conocen a Jesús", "texto": "1 Timoteo 2:1-4", "enfoque": "La intercesión amorosa antes de hablarles de Cristo."},
        {"nombre": "La Gran Comisión en el trabajo y la universidad", "texto": "Mateo 28:18-20", "enfoque": "Vivir el discipulado en la rutina diaria y las relaciones cotidianas."}
    ]
}


if modo == "Podcast Evangelístico":
    st.title("🎙️ Conectados con el Evangelio de Jesús")
    st.caption("Planifica y genera episodios cristocéntricos de máxima profundidad pastoral para llevar oyentes a los pies de Cristo.")

    tab_generar, tab_temporadas, tab_historial = st.tabs([
        "✨ Diseñar y Generar Episodio",
        "🗓️ Planificador de Temporadas",
        "📂 Historial de Episodios"
    ])

    podcasts = cargar_datos_json(PODCAST_FILE)

    with tab_generar:
        st.subheader("1. Selecciona la Ruta del Evangelio")
        col_r1, col_r2 = st.columns(2)
        ruta_elegida = col_r1.selectbox("Ruta Temática", list(RUTAS_EVANGELIO.keys()))
        
        opciones_temas = RUTAS_EVANGELIO[ruta_elegida]
        nombres_temas = ["Personalizado / Otro tema..."] + [t["nombre"] for t in opciones_temas]
        tema_elegido_nombre = col_r2.selectbox("Tema sugerido dentro de esta ruta", nombres_temas)

        # Datos por defecto según selección
        texto_defecto = ""
        enfoque_defecto = ""
        titulo_defecto = ""

        if tema_elegido_nombre != "Personalizado / Otro tema...":
            item_tema = next((t for t in opciones_temas if t["nombre"] == tema_elegido_nombre), None)
            if item_tema:
                texto_defecto = item_tema["texto"]
                enfoque_defecto = item_tema["enfoque"]
                titulo_defecto = item_tema["nombre"]
                st.info(f"📖 **Pasaje Central:** `{texto_defecto}` | 🎯 **Enfoque Teológico:** {enfoque_defecto}")

        st.divider()
        st.subheader("2. Parámetros del Episodio")

        with st.form("form_podcast_profundo"):
            col_t1, col_t2 = st.columns(2)
            titulo_episodio = col_t1.text_input("Título del Episodio", value=titulo_defecto, placeholder="Ej: Cuando la ansiedad no te deja descansar")
            pasaje_biblico = col_t2.text_input(
                "Pasaje Bíblico Clave (opcional)",
                value=texto_defecto,
                placeholder="Déjalo vacío para que la IA sugiera pasajes según el título",
                help="Si escribes un pasaje, será el principal. La IA también buscará pasajes de apoyo relacionados con el título."
            )

            col_p1, col_p2 = st.columns(2)
            publico = col_p1.text_input("Público Objetivo", placeholder="Ej: Jóvenes universitarios, adultos con heridas del pasado, buscadores...")
            enfoque_pastoral = col_p2.text_input("Enfoque Espiritual / Pastoral", value=enfoque_defecto, placeholder="Ej: Mostrar el descanso en la obra consumada de Cristo...")

            col_o1, col_o2 = st.columns(2)
            tono = col_o1.selectbox(
                "Tono del Episodio",
                [
                    "Cercano, profundo y transformador (Charla de café cristocéntrica)",
                    "Cálido, pausado y reflexivo (Para momentos de dolor o soledad)",
                    "Íntimo, testimonial y confesional",
                    "Enérgico, inspirador y de llamado a la acción"
                ]
            )
            duracion = col_o2.select_slider("Duración Estimada", options=["5-7 min", "8-10 min", "12-15 min", "18-20 min"], value="8-10 min")

            testimonio = st.text_area(
                "Testimonio real verídico (opcional)",
                placeholder="Escribe aquí un testimonio real si cuentas con permiso del protagonista...",
                height=70
            )

            usar_testimonio_ilustrativo = st.checkbox(
                "Si no agrego testimonio real, incluir una historia/ejemplo breve rotulado claramente como '[Ejemplo ilustrativo]'."
            )

            detalles_extra = st.text_area(
                "Indicaciones adicionales para la IA (opcional)",
                placeholder="Ej: Enfatizar que no se trata de religión sino de relación; incluir advertencia pastoral sobre buscar ayuda profesional si es caso de salud mental...",
                height=60
            )

            generar = st.form_submit_button("🎬 Generar Plan y Guion Teológico Profundo", use_container_width=True)

        if generar:
            if titulo_episodio.strip() and publico.strip():
                with st.spinner("Buscando pasajes bíblicos relacionados y desarrollando el guion..."):

                    # La IA primero analiza el título para proponer pasajes bíblicos pertinentes.
                    prompt_busqueda_pasajes = f"""Actúa como un asistente de investigación bíblica responsable.
Para el podcast cristocéntrico 'Conectados con el Evangelio de Jesús', sugiere pasajes bíblicos
directamente relacionados con el siguiente tema.

Título del episodio: {titulo_episodio}
Ruta temática: {ruta_elegida}
Enfoque pastoral: {enfoque_pastoral if enfoque_pastoral.strip() else "Cristocéntrico y transformador"}
Pasaje escrito por el usuario: {pasaje_biblico if pasaje_biblico.strip() else "Ninguno; elige el más apropiado"}

Responde en español y usa este formato:
PASO PRINCIPAL: [referencia bíblica]
PASAJES DE APOYO:
- [referencia] — [explicación breve de su relación con el tema]
- [referencia] — [explicación breve de su relación con el tema]
- [referencia] — [explicación breve de su relación con el tema]

Reglas:
- Si el usuario escribió un pasaje, respétalo como pasaje principal.
- Si no escribió uno, escoge un pasaje principal bíblicamente adecuado al título.
- Propón entre 3 y 5 pasajes de apoyo.
- No inventes referencias, citas ni versículos.
- Mantén el enfoque en Jesucristo, su obra, cruz y resurrección cuando sea pertinente."""

                    try:
                        pasajes_sugeridos = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {
                                    "role": "system",
                                    "content": "Eres un asistente bíblico cuidadoso, cristocéntrico y fiel al contexto de las Escrituras."
                                },
                                {"role": "user", "content": prompt_busqueda_pasajes}
                            ]
                        ).choices[0].message.content
                    except Exception as error_pasajes:
                        pasajes_sugeridos = (
                            "No fue posible generar pasajes sugeridos en este momento. "
                            f"Detalle técnico: {error_pasajes}"
                        )

                    instruccion_testimonio = (
                        "Incluye este testimonio real proporcionado por el autor sin alterar sus hechos: " + testimonio.strip()
                        if testimonio.strip()
                        else (
                            "Incluye un ejemplo breve que ilustre el punto, pero titúlalo literalmente '[Ejemplo ilustrativo]' sin fingir que es un caso real específico."
                            if usar_testimonio_ilustrativo
                            else "No incluyas sección de testimonio."
                        )
                    )

                    prompt_sistema = """Actúa como un teólogo pastoral y experimentado creador de podcasts cristianos para el programa 'Conectados con el Evangelio de Jesús'.
Tu meta es conectar la necesidad y el dolor humano real con la persona y la obra redentora de Jesucristo, con suma profundidad teológica, lenguaje contemporáneo (sin 'cristiañol' innecesario) y calidez pastoral.

Debes generar el episodio con la siguiente estructura rigurosa:

=========================================
1. PLAN DEL EPISODIO Y ESCALETA
- Título Oficial:
- Serie / Ruta:
- Idea Central (en una sola frase memorable):
- Objetivo Espiritual:
- Pasaje Bíblico Principal (con breve contexto histórico y literario):
- Duración Total Estimada:
- Escaleta Minuto a Minuto con Bloques:

2. GANCHO DE ENTRADA (HOOK)
- Entrada empática, pregunta o dilema cotidiano honesto que capture el corazón del oyente sin juzgarlo.

3. LA VERDAD DEL EVANGELIO (EXPOSICIÓN BÍBLICA)
- Presentación del texto bíblico y explicación clara, profunda y aplicable de la gracia de Dios.

4. CONEXIÓN DIRECTA CON JESUCRISTO
- Explicación de cómo Jesús vivió, venció o respondió a esta realidad mediante su encarnación, muerte en la cruz y resurrección victoriosa.

5. TESTIMONIO O EJEMPLO
- Sección según las instrucciones proporcionadas.

6. APLICACIÓN PRÁCTICA (EL LLAMADO A SEGUIRLE)
- 3 pasos concretos, medibles y alcanzables para poner en práctica esta semana (Con Dios, en lo personal y con el prójimo).

7. ORACIÓN GUIADA Y DESPEDIDA
- Oración sincera y humilde para abrirle el corazón a Jesús.
- Despedida oficial del podcast 'Conectados con el Evangelio de Jesús' animando a perseverar en la fe e integrarse a una iglesia local.
========================================="""

                    prompt_usuario = f"""Podcast: Conectados con el Evangelio de Jesús
Ruta Temática: {ruta_elegida}
Título: {titulo_episodio}
Pasaje Bíblico indicado por el usuario: {pasaje_biblico if pasaje_biblico.strip() else 'No indicado'}
Investigación IA de pasajes relacionados:
{pasajes_sugeridos}

INSTRUCCIÓN IMPORTANTE:
- Usa como pasaje principal el indicado por el usuario, si existe.
- Si el usuario no indicó uno, selecciona el PASO PRINCIPAL sugerido por la investigación.
- Integra los pasajes de apoyo solo cuando aporten contexto y no fuerces referencias.
- Explica los textos en su contexto y mantén a Jesucristo en el centro.

Enfoque Pastoral: {enfoque_pastoral if enfoque_pastoral.strip() else 'Cristocéntrico y transformador'}
Público Objetivo: {publico}
Tono: {tono}
Duración: {duracion}
Instrucción de Testimonio: {instruccion_testimonio}
Notas Adicionales: {detalles_extra if detalles_extra.strip() else 'Ninguna'}"""

                    respuesta = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": prompt_sistema},
                            {"role": "user", "content": prompt_usuario}
                        ]
                    ).choices[0].message.content

                    st.session_state["guion_podcast_generado"] = respuesta
                    st.session_state["pasajes_sugeridos_podcast"] = pasajes_sugeridos
                    st.session_state["guion_podcast_meta"] = {
                        "titulo": titulo_episodio.strip(),
                        "ruta": ruta_elegida,
                        "pasaje": pasaje_biblico,
                        "publico": publico.strip(),
                        "tono": tono,
                        "duracion": duracion
                    }
            else:
                st.warning("Por favor completa al menos el título y el público objetivo.")

        if st.session_state.get("guion_podcast_generado"):
            st.divider()

            if st.session_state.get("pasajes_sugeridos_podcast"):
                with st.expander("📖 Pasajes bíblicos encontrados por la IA", expanded=True):
                    st.markdown(st.session_state["pasajes_sugeridos_podcast"])

            st.subheader("📜 Plan Teológico y Guion Generado")
            st.markdown(st.session_state["guion_podcast_generado"])

            meta = st.session_state.get("guion_podcast_meta", {})
            titulo_pdf = meta.get("titulo", "Episodio Conectados con el Evangelio")

            col_g1, col_g2, col_g3 = st.columns(3)

            if col_g1.button("💾 Guardar en Historial", use_container_width=True, key="btn_guardar_podcast_profundo"):
                nuevo_ep = {
                    "id": str(uuid.uuid4())[:8],
                    "titulo": titulo_pdf,
                    "ruta": meta.get("ruta", ""),
                    "pasaje": meta.get("pasaje", ""),
                    "publico": meta.get("publico", ""),
                    "tono": meta.get("tono", ""),
                    "duracion": meta.get("duracion", ""),
                    "guion": st.session_state["guion_podcast_generado"],
                    "creado_en": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                podcasts.append(nuevo_ep)
                guardar_datos_json(PODCAST_FILE, podcasts)
                st.success("¡Episodio guardado exitosamente!")

            col_g2.download_button(
                "⬇️ Descargar TXT",
                data=st.session_state["guion_podcast_generado"],
                file_name=f"{titulo_pdf.replace(' ', '_').lower()}.txt",
                mime="text/plain",
                use_container_width=True
            )

            col_g3.download_button(
                "📄 Descargar PDF",
                data=crear_pdf_podcast(titulo_pdf, st.session_state["guion_podcast_generado"]),
                file_name=f"{titulo_pdf.replace(' ', '_').lower()}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    with tab_temporadas:
        st.subheader("🤖 Generador IA de Nuevas Temporadas")
        st.caption("Crea nuevas series bíblicas para que Conectados con el Evangelio de Jesús siga creciendo con profundidad y dirección.")

        temporadas_guardadas = cargar_datos_json(TEMPORADAS_FILE)

        with st.form("form_generar_temporada_ia"):
            col_temp1, col_temp2 = st.columns(2)

            nombre_temporada = col_temp1.text_input(
                "Nombre o idea de la temporada",
                placeholder="Ej: Jesús en mis heridas, Volver a Dios, Fe para tiempos difíciles..."
            )

            ruta_temporada = col_temp2.selectbox(
                "Ruta principal del Evangelio",
                options=list(RUTAS_EVANGELIO.keys())
            )

            col_temp3, col_temp4, col_temp5 = st.columns(3)

            publico_temporada = col_temp3.text_input(
                "Público objetivo",
                placeholder="Ej: Jóvenes adultos, nuevos creyentes, personas alejadas de Dios..."
            )

            cantidad_episodios = col_temp4.selectbox(
                "Cantidad de episodios",
                options=[4, 5, 6, 8, 10, 12],
                index=2
            )

            duracion_episodio_temporada = col_temp5.selectbox(
                "Duración por episodio",
                options=["15 minutos", "30 minutos", "45 minutos", "60 minutos"],
                index=1,
                help="La profundidad y extensión del contenido se ajustará según esta duración."
            )

            objetivo_temporada = st.text_area(
                "Objetivo espiritual de la temporada",
                placeholder="Ej: Ayudar a personas con ansiedad a descubrir la paz, el cuidado y la presencia de Jesús...",
                height=75
            )

            indicaciones_temporada = st.text_area(
                "Temas que deseas incluir, evitar o instrucciones adicionales (opcional)",
                placeholder="Ej: Incluir salud mental con sensibilidad pastoral, enfatizar la cruz y resurrección, evitar lenguaje técnico...",
                height=75
            )

            generar_temporada = st.form_submit_button(
                "✨ Generar Nueva Temporada con IA",
                use_container_width=True
            )

        if generar_temporada:
            if nombre_temporada.strip() and publico_temporada.strip() and objetivo_temporada.strip():
                with st.spinner("La IA está diseñando una temporada bíblica y cristocéntrica..."):

                    prompt_sistema_temporada = """Actúa como teólogo pastoral, estratega de contenido cristiano
y director del podcast 'Conectados con el Evangelio de Jesús'.

Diseña una temporada de podcast de máxima profundidad bíblica, pastoral y cristocéntrica.
La temporada debe llevar a las personas hacia Jesús, su encarnación, su cruz, su resurrección,
su gracia y el llamado a seguirle.

No uses cristiañol innecesario. Usa lenguaje cercano, claro, compasivo y bíblicamente responsable.
No inventes testimonios reales, estadísticas ni historias que parezcan verificables.

Devuelve la respuesta usando EXACTAMENTE esta estructura:

# TÍTULO DE LA TEMPORADA

## VISIÓN Y PROPÓSITO
Explica en un párrafo qué transformación espiritual busca esta temporada.

## AUDIENCIA
Describe brevemente a quién sirve.

## HILO CONDUCTOR DEL EVANGELIO
Explica cómo toda la temporada conecta con Jesucristo, su muerte y resurrección.

## MAPA DE EPISODIOS

IMPORTANTE SOBRE LA DURACIÓN: Ajusta la profundidad y extensión de cada episodio según la duración total
indicada por el usuario. En episodios de 15 minutos sé conciso pero profundo. En episodios de 30 minutos
desarrolla con más ilustraciones y aplicación. En episodios de 45 y 60 minutos incluye subpuntos adicionales,
más de una ilustración o historia bíblica de apoyo, preguntas de reflexión para el oyente y mayor desarrollo
expositivo, manteniendo siempre un tono conversacional y no académico.

Para cada episodio incluye:
- Episodio número y título atractivo.
- Pregunta o lucha humana que aborda.
- Pasaje bíblico principal (con breve contexto histórico y literario).
- IDEA CENTRAL CRISTOCÉNTRICA (DESARROLLO COMPLETO): No escribas solo una frase o resumen. Redacta un
  desarrollo expositivo real de varios párrafos (ajusta la extensión según la duración del episodio: más
  párrafos y profundidad en episodios de 45-60 minutos, más breve pero sustancioso en episodios de 15
  minutos), listo para ser leído o predicado casi textualmente en el podcast. Debe explicar el pasaje bíblico
  con claridad, conectar directamente con la persona, la obra, la muerte y la resurrección de Jesucristo, y
  tender un puente emocional y práctico hacia la vida real del oyente. Evita clichés religiosos vacíos;
  profundiza con contenido bíblico sólido y aplicable.
- Breve resumen del contenido (una línea, para uso en notas de publicación).
- Aplicación práctica semanal (3 pasos concretos: uno con Dios, uno personal, uno con el prójimo).
- Duración recomendada para este bloque dentro del episodio.

## EPISODIO DE APERTURA
Explica por qué debe comenzar con ese episodio.

## EPISODIO DE CIERRE
Explica cómo cerrar la temporada con una invitación a permanecer conectados con el Evangelio de Jesús.

## RECOMENDACIÓN DE PUBLICACIÓN
Sugiere frecuencia semanal, frase promocional y una idea de llamada a la acción para compartir cada episodio.
"""

                    prompt_usuario_temporada = f"""Podcast: Conectados con el Evangelio de Jesús
Nombre o idea de temporada: {nombre_temporada}
Ruta principal: {ruta_temporada}
Público objetivo: {publico_temporada}
Cantidad de episodios: {cantidad_episodios}
Duración deseada por episodio: {duracion_episodio_temporada}
Objetivo espiritual: {objetivo_temporada}
Indicaciones adicionales: {indicaciones_temporada if indicaciones_temporada.strip() else "Ninguna"}

Crea una temporada completa que sea profunda, práctica, evangelística y centrada en Jesucristo."""

                    respuesta_temporada = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": prompt_sistema_temporada},
                            {"role": "user", "content": prompt_usuario_temporada}
                        ]
                    ).choices[0].message.content

                    st.session_state["temporada_generada_ia"] = respuesta_temporada
                    st.session_state["temporada_generada_meta"] = {
                        "nombre": nombre_temporada.strip(),
                        "ruta": ruta_temporada,
                        "publico": publico_temporada.strip(),
                        "cantidad": cantidad_episodios,
                        "duracion_episodio": duracion_episodio_temporada,
                        "objetivo": objetivo_temporada.strip()
                    }
            else:
                st.warning("Completa el nombre, público objetivo y objetivo espiritual de la temporada.")

        if st.session_state.get("temporada_generada_ia"):
            st.divider()
            st.subheader("📜 Nueva Temporada Generada")
            st.markdown(st.session_state["temporada_generada_ia"])

            meta_temporada = st.session_state.get("temporada_generada_meta", {})
            nombre_archivo = meta_temporada.get("nombre", "nueva_temporada")
            nombre_archivo = nombre_archivo.replace(" ", "_").lower()

            col_save_temp, col_download_temp = st.columns(2)

            if col_save_temp.button(
                "💾 Guardar Temporada",
                key="guardar_temporada_ia",
                use_container_width=True
            ):
                nueva_temporada = {
                    "id": str(uuid.uuid4())[:8],
                    "nombre": meta_temporada.get("nombre", "Temporada sin nombre"),
                    "ruta": meta_temporada.get("ruta", ""),
                    "publico": meta_temporada.get("publico", ""),
                    "cantidad": meta_temporada.get("cantidad", ""),
                    "duracion_episodio": meta_temporada.get("duracion_episodio", ""),
                    "objetivo": meta_temporada.get("objetivo", ""),
                    "contenido": st.session_state["temporada_generada_ia"],
                    "creado_en": datetime.now().strftime("%Y-%m-%d %H:%M")
                }

                temporadas_guardadas.append(nueva_temporada)
                guardar_datos_json(TEMPORADAS_FILE, temporadas_guardadas)
                st.success("✅ Temporada guardada correctamente.")

            col_download_temp.download_button(
                "⬇️ Descargar Temporada TXT",
                data=st.session_state["temporada_generada_ia"],
                file_name=f"{nombre_archivo}.txt",
                mime="text/plain",
                use_container_width=True
            )

        st.divider()
        st.subheader("📂 Temporadas Generadas y Guardadas")

        if temporadas_guardadas:
            for temporada in reversed(temporadas_guardadas):
                with st.expander(
                    f"🎙️ {temporada.get('nombre', 'Temporada')} — {temporada.get('creado_en', '')}"
                ):
                    st.caption(
                        f"Ruta: {temporada.get('ruta', '')} | "
                        f"Público: {temporada.get('publico', '')} | "
                        f"Episodios: {temporada.get('cantidad', '')} | "
                        f"Duración c/u: {temporada.get('duracion_episodio', 'N/A')}"
                    )

                    st.markdown(temporada.get("contenido", ""))

                    col_td1, col_td2 = st.columns(2)

                    col_td1.download_button(
                        "⬇️ Descargar TXT",
                        data=temporada.get("contenido", ""),
                        file_name=f"temporada_{temporada.get('id', 'podcast')}.txt",
                        mime="text/plain",
                        key="download_temp_" + temporada.get("id", ""),
                        use_container_width=True
                    )

                    if col_td2.button(
                        "🗑️ Eliminar Temporada",
                        key="delete_temp_" + temporada.get("id", ""),
                        use_container_width=True
                    ):
                        temporadas_guardadas = [
                            t for t in temporadas_guardadas
                            if t.get("id") != temporada.get("id")
                        ]
                        guardar_datos_json(TEMPORADAS_FILE, temporadas_guardadas)
                        st.rerun()
        else:
            st.info("Todavía no has generado temporadas nuevas con IA.")

        st.divider()
        st.subheader("🗓️ Estructura de Temporadas Recomendadas")
        st.caption("Series temáticas listas para grabar y llevar a tu audiencia paso a paso en el camino de la fe.")

        contenido_temporadas_generado = cargar_datos_json(CONTENIDO_TEMPORADAS_FILE)
        if not isinstance(contenido_temporadas_generado, dict):
            contenido_temporadas_generado = {}

        emojis_temporada = {
            "Temporada 1: Volver a lo Esencial": "🌱",
            "Temporada 2: Paz en Medio de la Tormenta": "🕊️",
            "Temporada 3: Compartir a Jesús sin Miedo": "🔥"
        }

        for nombre_temp_rec, episodios_temp_rec in TEMPORADAS_RECOMENDADAS_DATA.items():
            emoji_temp = emojis_temporada.get(nombre_temp_rec, "🎙️")
            expandido_defecto = (nombre_temp_rec == "Temporada 1: Volver a lo Esencial")

            with st.expander(f"{emoji_temp} {nombre_temp_rec} ({len(episodios_temp_rec)} Episodios)", expanded=expandido_defecto):
                lineas_resumen = "\n".join(
                    f"{ep['n']}. **{ep['titulo']}** *({ep['pasaje']})* - {ep['resumen']}"
                    for ep in episodios_temp_rec
                )
                st.markdown(lineas_resumen)
                st.divider()

                if nombre_temp_rec in contenido_temporadas_generado:
                    st.success("✅ Contenido completo ya generado (45 min por episodio).")
                    st.markdown(contenido_temporadas_generado[nombre_temp_rec])

                    col_save, col_regen, col_dl = st.columns(3)

                    ya_guardada = any(
                        t.get("nombre_original") == nombre_temp_rec
                        for t in temporadas_guardadas
                    )

                    if ya_guardada:
                        col_save.success("✅ Guardada")
                    else:
                        if col_save.button(
                            "💾 Guardar en Historial",
                            key="save_rec_" + nombre_temp_rec,
                            use_container_width=True
                        ):
                            nueva_entrada_historial = {
                                "id": str(uuid.uuid4())[:8],
                                "nombre": nombre_temp_rec,
                                "nombre_original": nombre_temp_rec,
                                "ruta": "Serie recomendada",
                                "publico": "General",
                                "cantidad": len(episodios_temp_rec),
                                "duracion_episodio": "45 minutos",
                                "objetivo": "Temporada recomendada de Conectados con el Evangelio de Jesús",
                                "contenido": contenido_temporadas_generado[nombre_temp_rec],
                                "creado_en": datetime.now().strftime("%Y-%m-%d %H:%M")
                            }
                            temporadas_guardadas.append(nueva_entrada_historial)
                            guardar_datos_json(TEMPORADAS_FILE, temporadas_guardadas)
                            st.success("✅ Temporada guardada en el historial.")
                            st.rerun()

                    if col_regen.button(
                        "🔄 Regenerar contenido",
                        key="regen_" + nombre_temp_rec,
                        use_container_width=True
                    ):
                        del contenido_temporadas_generado[nombre_temp_rec]
                        guardar_datos_json(CONTENIDO_TEMPORADAS_FILE, contenido_temporadas_generado)
                        st.rerun()

                    col_dl.download_button(
                        "⬇️ Descargar TXT",
                        data=contenido_temporadas_generado[nombre_temp_rec],
                        file_name=nombre_temp_rec.replace(" ", "_").replace(":", "").lower() + ".txt",
                        mime="text/plain",
                        use_container_width=True,
                        key="dl_" + nombre_temp_rec
                    )
                else:
                    if st.button(
                        "🚀 Generar Contenido Completo (45 min c/u)",
                        key="gen_" + nombre_temp_rec,
                        use_container_width=True
                    ):
                        with st.spinner(f"Desarrollando '{nombre_temp_rec}' con profundidad teológica (esto puede tardar un momento)..."):

                            lista_episodios_texto = "\n".join(
                                f"- Episodio {ep['n']}: {ep['titulo']} | Pasaje: {ep['pasaje']} | Enfoque: {ep['resumen']}"
                                for ep in episodios_temp_rec
                            )

                            prompt_sistema_dev = """Actúa como teólogo pastoral y guionista principal del podcast
'Conectados con el Evangelio de Jesús'. Vas a desarrollar el contenido COMPLETO de una temporada
ya planificada, con episodios de 45 minutos de duración cada uno.

Para CADA episodio de la lista que se te entrega, desarrolla EXACTAMENTE esta estructura:

## Episodio [número]: [título]
**Pasaje:** [pasaje bíblico]

**Lucha humana:** (1-2 líneas describiendo la necesidad real que aborda el episodio)

**Idea Central Cristocéntrica (desarrollo completo):**
Escribe aquí un desarrollo expositivo real de al menos 3 a 5 párrafos completos, listo para ser leído
o predicado casi textualmente en un podcast de 45 minutos. Explica el pasaje bíblico con su contexto
histórico y literario, profundiza en su significado teológico, conecta directamente con la persona,
la obra, la muerte y la resurrección de Jesucristo, y tiende un puente emocional y práctico hacia la
vida real del oyente. Usa lenguaje cercano y pastoral, evitando clichés religiosos vacíos. No resumas:
desarrolla con profundidad real, como lo harías en una prédica completa de 45 minutos.

**Aplicación práctica:**
1. Con Dios: [acción concreta]
2. Personal: [acción concreta]
3. Con el prójimo: [acción concreta]

**Estructura sugerida de 45 minutos:**
- Introducción y gancho (5 min)
- Contexto bíblico (8 min)
- Desarrollo cristocéntrico (18 min)
- Ilustración o ejemplo (8 min)
- Aplicación práctica (3 min)
- Oración final (3 min)

---

Repite esta estructura para TODOS los episodios de la lista, en orden, separados por '---'.
No omitas ningún episodio. Sé bíblicamente responsable, cristocéntrico y pastoralmente sensible."""

                            prompt_usuario_dev = f"""Temporada: {nombre_temp_rec}
Podcast: Conectados con el Evangelio de Jesús
Duración por episodio: 45 minutos

Episodios a desarrollar:
{lista_episodios_texto}

Desarrolla el contenido completo de todos estos episodios siguiendo la estructura indicada."""

                            respuesta_dev = client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[
                                    {"role": "system", "content": prompt_sistema_dev},
                                    {"role": "user", "content": prompt_usuario_dev}
                                ]
                            ).choices[0].message.content

                            contenido_temporadas_generado[nombre_temp_rec] = respuesta_dev
                            guardar_datos_json(CONTENIDO_TEMPORADAS_FILE, contenido_temporadas_generado)
                            st.rerun()

    with tab_historial:
        st.subheader("Episodios Guardados")
        if podcasts:
            for ep in reversed(podcasts):
                t_nombre = ep.get("titulo", ep.get("tema", "Episodio"))
                with st.expander(f"🎙️ {t_nombre} — {ep.get('creado_en', '')}"):
                    st.caption(f"Ruta: {ep.get('ruta', 'General')} | Pasaje: {ep.get('pasaje', 'N/A')} | Duración: {ep.get('duracion', '')}")
                    st.markdown(ep["guion"])

                    col_h1, col_h2, col_h3 = st.columns(3)
                    col_h1.download_button(
                        "⬇️ TXT",
                        data=ep["guion"],
                        file_name=f"podcast_{ep['id']}.txt",
                        mime="text/plain",
                        use_container_width=True,
                        key="dl_txt_" + ep["id"]
                    )
                    col_h2.download_button(
                        "📄 PDF",
                        data=crear_pdf_podcast(t_nombre, ep["guion"]),
                        file_name=f"podcast_{ep['id']}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key="dl_pdf_" + ep["id"]
                    )
                    if col_h3.button("🗑️ Eliminar", key="del_pod_" + ep["id"], use_container_width=True):
                        podcasts = [p for p in podcasts if p["id"] != ep["id"]]
                        guardar_datos_json(PODCAST_FILE, podcasts)
                        st.rerun()
        else:
            st.info("Aún no tienes episodios guardados en el historial.")

    st.stop()

for i, message in enumerate(st.session_state.messages):
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant":
                mensaje_id = message.get("id", f"mensaje_{i}")
                acciones_respuesta(message["content"], mensaje_id)

prompt = st.chat_input("Escribe tu pregunta o pide ayuda...")

if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages,
        )
        answer = response.choices[0].message.content
        st.markdown(answer)

        if st.session_state.get("guardar_sesion_pendiente"):
            datos = st.session_state.guardar_sesion_pendiente
            guardar_sesion(datos["nombre"], datos["categoria"], datos["situacion"], answer)
            st.session_state.guardar_sesion_pendiente = None

        if st.session_state.get("serie_sermon_pendiente_meta"):
            meta_serie = st.session_state.serie_sermon_pendiente_meta
            series_guardadas = cargar_datos_json(SERIES_SERMONES_FILE)
            series_guardadas.append({
                "id": str(uuid.uuid4()),
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "nombre": meta_serie.get("nombre", ""),
                "libro_o_tema": meta_serie.get("libro_o_tema", ""),
                "cantidad_sermones": meta_serie.get("cantidad_sermones", ""),
                "tipo": meta_serie.get("tipo", ""),
                "publico": meta_serie.get("publico", ""),
                "duracion": meta_serie.get("duracion", ""),
                "nivel": meta_serie.get("nivel", ""),
                "objetivo": meta_serie.get("objetivo", ""),
                "contenido": answer,
            })
            guardar_datos_json(SERIES_SERMONES_FILE, series_guardadas)
            st.session_state.serie_sermon_pendiente_meta = None

        if st.session_state.get("sermon_pendiente_meta"):
            meta_sermon = st.session_state.sermon_pendiente_meta
            sermones_guardados = cargar_datos_json(SERMONES_FILE)
            sermones_guardados.append({
                "id": str(uuid.uuid4()),
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "tema": meta_sermon.get("tema", ""),
                "texto_biblico": meta_sermon.get("texto_biblico", ""),
                "tipo": meta_sermon.get("tipo", ""),
                "publico": meta_sermon.get("publico", ""),
                "duracion": meta_sermon.get("duracion", ""),
                "nivel": meta_sermon.get("nivel", ""),
                "objetivo": meta_sermon.get("objetivo", ""),
                "contenido": answer,
            })
            guardar_datos_json(SERMONES_FILE, sermones_guardados)
            st.session_state.sermon_pendiente_meta = None

        mensaje_id = str(uuid.uuid4())

        st.session_state.messages.append({
            "id": mensaje_id,
            "role": "assistant",
            "content": answer
        })

        acciones_respuesta(answer, mensaje_id)
