import streamlit as st
from google import genai
from google.genai import types
import sys
from io import StringIO

# Načtení AI klienta z terminálu
try:
    client = genai.Client()
except Exception as e:
    client = None

# Nastavení vzhledu stránky
st.set_page_config(page_title="MARCO AI Platform", page_icon="🤖", layout="wide")
st.caption("⚠️ MARCO AI | Upozornění: Umělá inteligence může dělat chyby.")

# LEVÝ PANEL
with st.sidebar:
    st.title("🤖 MARCO PLATFORM")
    st.write("---")
    
    # Výběr země, kde uživatel žije
    st.subheader("📍 Poloha a jazyk")
    zeme = st.selectbox(
        "Kde aktuálně žijete?", 
        ["Česká republika 🇨🇿", "Francie 🇫🇷", "Německo 🇩🇪", "Španělsko 🇪🇸", "Velká Británie 🇬🇧", "USA 🇺🇸"]
    )
    
    # Mapování zemí na hlavní komunikační jazyky
    jazyky_mapovani = {
        "Česká republika 🇨🇿": "češtině",
        "Francie 🇫🇷": "francouzštině",
        "Německo 🇩🇪": "němčině",
        "Španělsko 🇪🇸": "španělštině",
        "Velká Británie 🇬🇧": "angličtině",
        "USA 🇺🇸": "angličtině"
    }
    aktualni_jazyk = jazyky_mapovani[zeme]

    st.write("---")
    mod = st.radio("Vyber si aplikaci:", ["💬 Obecný Chat", "🌍 POLO (Výuka jazyků)", "💻 Kódovací koutek"])
    
    # ⚙️ Nastavení pro POLO
    if mod == "🌍 POLO (Výuka jazyků)":
        st.write("---")
        st.subheader("⚙️ Nastavení trenéra")
        vybrana_uroven = st.select_slider(
            "Tvá skutečná úroveň:", 
            options=["Začátečník (A1)", "Základy (A2)", "Samostatný (B1)", "Pokročilý (B2)"]
        )
    
    st.write("---")
    st.write("v1.5 | Vyrobil PRO")

# Výchozí pozdravy podle zemí (ŽÁDNÉ BRO NA ZAČÁTKU)
pozdravy_chat = {
    "Česká republika 🇨🇿": "Dobrý den! Jsem MARCO AI, vaše osobní platforma. O čem si dnes popovídáme?",
    "Francie 🇫🇷": "Bonjour! Je suis MARCO AI, votre plateforme personnelle. De quoi aimeriez-vous discuter aujourd'hui?",
    "Německo 🇩🇪": "Guten Tag! Ich bin MARCO AI, Ihre persönliche Plattform. Worüber möchten Sie heute sprechen?",
    "Španělsko 🇪🇸": "¡Hola! Soy MARCO AI, tu plataforma personal. ¿De qué te gustaría hablar hoy?",
    "Velká Británie 🇬🇧": "Hello! I am MARCO AI, your personal platform. What would you like to discuss today?",
    "USA 🇺🇸": "Hello! I am MARCO AI, your personal platform. What would you like to discuss today?"
}

pozdravy_polo = {
    "Česká republika 🇨🇿": "Vítejte v POLO trenéru! Jste připraveni na lekci?",
    "Francie 🇫🇷": "Bienvenue dans l'entraîneur POLO ! Êtes-vous prêt pour la leçon ?",
    "Německo 🇩🇪": "Willkommen beim POLO-Trainer! Sind Sie bereit für die Lektion?",
    "Španělsko 🇪🇸": "¡Bienvenido al entrenador POLO! ¿Estás listo para la lección?",
    "Velká Británie 🇬🇧": "Welcome to the POLO trainer! Are you ready for the lesson?",
    "USA 🇺🇸": "Welcome to the POLO trainer! Are you ready for the lesson?"
}

# Inicializace historie v paměti
if "history_chat" not in st.session_state:
    st.session_state.history_chat = {}
if "history_polo" not in st.session_state:
    st.session_state.history_polo = {}

if zeme not in st.session_state.history_chat:
    st.session_state.history_chat[zeme] = [{"role": "assistant", "content": pozdravy_chat[zeme]}]
if zeme not in st.session_state.history_polo:
    st.session_state.history_polo[zeme] = [{"role": "assistant", "content": pozdravy_polo[zeme]}]

# ==========================================
# MOD 1: OBECNÝ CHAT
# ==========================================
if mod == "💬 Obecný Chat":
    st.header(f"💬 Pokec s Marcem ({zeme})")
    
    for msg in st.session_state.history_chat[zeme]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    user_input = st.chat_input("Napište Marcovi cokoliv...")
    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.history_chat[zeme].append({"role": "user", "content": user_input})
        
        if client:
            try:
                # Nastavení identity (PRO je stvořitel) a zákaz oslovení "bro"
                system_instrukce = (
                    f"Jsi MARCO AI, pokročilá platforma, kterou vytvořil talentovaný vývojář PRO. "
                    f"Odpovídej výhradně v {aktualni_jazyk}. Mluv profesionálně, přátelsky, nepoužívej slovo 'bro'. "
                    f"Reaguj na historii chatu."
                )
                
                formatted_contents = []
                for m in st.session_state.history_chat[zeme]:
                    formatted_contents.append(
                        types.Content(
                            role=m["role"],
                            parts=[types.Part.from_text(text=m["content"])]
                        )
                    )
                
                # 🚀 POUŽITÍ MODELU LITE PRO VELKÝ LIMIT A RYCHLOST
                response = client.models.generate_content(
                    model='gemini-3.5-flash-lite', 
                    contents=formatted_contents,
                    config=types.GenerateContentConfig(system_instruction=system_instrukce)
                )
                odpoved = response.text
            except Exception as e:
                odpoved = f"❌ Chyba spojení s AI mozkem: {e}"
        else:
            odpoved = "❌ V terminálu chybí exportovaný klíč!"
        
        with st.chat_message("assistant"):
            st.write(odpoved)
        st.session_state.history_chat[zeme].append({"role": "assistant", "content": odpoved})

# ==========================================
# MOD 2: POLO (VÝUKA JAZYKŮ)
# ==========================================
elif mod == "🌍 POLO (Výuka jazyků)":
    st.header(f"🌍 POLO - Jazykový trenažér")
    st.progress(0.6)
    
    for msg in st.session_state.history_polo[zeme]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Odpovězte Polovi...")
    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.history_polo[zeme].append({"role": "user", "content": user_input})
        
        instrukce = (
            f"Jsi POLO, herní učitel jazyků z platformy MARCO AI (autorem platformy je vývojář PRO). "
            f"Uživatel žije v zemi: {zeme}, takže instrukce a zadání úkolů mu piš v {aktualni_jazyk}. "
            f"Jeho zvolená úroveň obtížnosti je: {vybrana_uroven}. "
            f"Zkoušej ho z cizích jazyků, opravuj jeho chyby, chval ho, přiděluj mu body a XP. "
            f"Nikdy nepoužívej slovo 'bro'. Sleduj kontext předchozí konverzace."
        )
        
        if client:
            try:
                formatted_contents_polo = []
                for m in st.session_state.history_polo[zeme]:
                    formatted_contents_polo.append(
                        types.Content(
                            role=m["role"],
                            parts=[types.Part.from_text(text=m["content"])]
                        )
                    )
                
                # 🚀 POUŽITÍ MODELU LITE PRO VELKÝ LIMIT A RYCHLOST
                response = client.models.generate_content(
                    model='gemini-3.5-flash-lite', 
                    contents=formatted_contents_polo,
                    config=types.GenerateContentConfig(system_instruction=instrukce)
                )
                odpoved_polo = response.text
            except Exception as e:
                odpoved_polo = f"❌ Chyba POLO AI: {e}"
        else:
            odpoved_polo = "❌ V terminálu chybí exportovaný klíč!"
            
        with st.chat_message("assistant"):
            st.write(odpoved_polo)
        st.session_state.history_polo[zeme].append({"role": "assistant", "content": odpoved_polo})

# ==========================================
# MOD 3: KÓDOVACÍ KOUTEK
# ==========================================
elif mod == "💻 Kódovací koutek":
    st.header("💻 Python online editor")
    st.write("Napište svůj Python kód dolů a otestujte ho!")
    
    kod = st.text_area("Tvůj kód:", value='print("Ahoj z Prahy!")\nx = 10\ny = 20\nprint(f"Výsledek: {x * y}")', height=200)
    
    if st.button("▶️ Spustit kód"):
        st.write("---")
        st.subheader("Výstup z programu:")
        
        old_stdout = sys.stdout
        redirected_output = sys.stdout = StringIO()
        try:
            exec(kod)
            st.code(redirected_output.getvalue())
        except Exception as e:
            st.error(f"Chyba v kódu: {e}")
        finally:
            sys.stdout = old_stdout