import streamlit as st
import requests
import random
import os
import base64
import json
import time
from io import BytesIO
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import urllib.parse
import datetime

# ==========================================
# ⚙️ CONFIGURATION DE LA PAGE
# ==========================================
st.set_page_config(page_title="Poké-Hub Web", page_icon="🎮", layout="wide")

# ==========================================
# 🎨 INJECTION DU DESIGN CSS "NEXT-GEN"
# ==========================================
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* header {visibility: hidden;}
    */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e293b 0%, #020617 100%) !important;
        color: #f8fafc;
    }

    /* Animations existantes */
    @keyframes pulse-egg {
        0% { transform: scale(1) translateY(0px); }
        50% { transform: scale(1.05) translateY(-5px); }
        100% { transform: scale(1) translateY(0px); }
    }
    .egg-anim {
        text-align: center; margin: 15px 0; animation: pulse-egg 2.5s infinite ease-in-out; filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.4));
    }

    /* Cartes des modes Qui est-ce */
    .game-card {
        background: rgba(30, 41, 59, 0.5); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3); transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        text-align: center; margin-bottom: 15px;
    }
    .game-card:hover { transform: translateY(-7px) scale(1.02); border-color: rgba(255, 75, 75, 0.8); box-shadow: 0 10px 25px rgba(255, 75, 75, 0.4); }
    .game-card-smash:hover { border-color: rgba(56, 189, 248, 0.8); box-shadow: 0 10px 25px rgba(56, 189, 248, 0.4); }
    .game-card-zelda:hover { border-color: rgba(250, 204, 21, 0.8); box-shadow: 0 10px 25px rgba(250, 204, 21, 0.4); }
    .game-card-hk:hover { border-color: rgba(148, 163, 184, 0.8); box-shadow: 0 10px 25px rgba(148, 163, 184, 0.4); }
    .game-card-eliminated {
        background: rgba(15, 23, 42, 0.4); border-radius: 16px; padding: 15px; text-align: center;
        opacity: 0.25; filter: grayscale(100%) contrast(1.2); margin-bottom: 15px; border: 1px solid rgba(255, 255, 255, 0.05); transition: all 0.3s ease;
    }
    
    div.stButton > button { border-radius: 12px; font-weight: 600; letter-spacing: 0.5px; transition: all 0.3s ease !important; }
    div.stButton > button:hover { transform: scale(1.03); box-shadow: 0px 5px 20px rgba(255, 255, 255, 0.15); }
    
    /* Styles pour modes Blind Starters */
    .microscope-lens {
        width: 140px; height: 140px; overflow: hidden; margin: 0 auto 20px auto; border: 6px solid #334155; 
        border-radius: 50%; display: flex; align-items: center; justify-content: center; background-color: #0f172a; 
        box-shadow: inset 0px 0px 20px rgba(0,0,0,0.9), 0px 10px 20px rgba(0,0,0,0.5);
    }
    .adn-container {
        display: flex; height: 130px; width: 100%; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px 12px 0 0;
        overflow: hidden; box-shadow: inset 0px 5px 15px rgba(0,0,0,0.6);
    }
    .lab-label {
        background-color: rgba(15, 23, 42, 0.8); text-align: center; font-weight: bold; font-size: 13px; 
        padding: 8px; font-family: 'Courier New', Courier, monospace; border: 1px solid rgba(255,255,255,0.1); 
        border-top: none; border-radius: 0 0 12px 12px; margin-bottom: 15px; letter-spacing: 2px;
    }
    .w-box {
        padding: 10px; border-radius: 8px; text-align: center; font-weight: 700; color: white; margin-bottom: 6px; 
        font-size: 14px; text-shadow: 1px 1px 3px rgba(0,0,0,0.6); box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .w-green { background: linear-gradient(135deg, #16a34a, #22c55e); border: 1px solid #15803d; }
    .w-yellow { background: linear-gradient(135deg, #ca8a04, #eab308); border: 1px solid #a16207; }
    .w-red { background: linear-gradient(135deg, #dc2626, #ef4444); border: 1px solid #b91c1c; }

    /* ==========================================
       🃏 STYLES DES CARTES GACHA
       ========================================== */
    .gacha-card {
        width: 260px;
        height: 380px;
        border-radius: 15px;
        padding: 15px;
        margin: 20px auto;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        background-color: #0f172a;
        box-shadow: 0 15px 35px rgba(0,0,0,0.6);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .gacha-card:hover {
        transform: translateY(-10px) scale(1.05);
    }
    .gacha-img-container {
        width: 100%;
        height: 200px;
        background-color: rgba(0,0,0,0.3);
        border-radius: 10px;
        display: flex;
        justify-content: center;
        align-items: center;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .gacha-img-container img {
        max-width: 90%;
        max-height: 90%;
        object-fit: contain;
        filter: drop-shadow(0px 8px 12px rgba(0,0,0,0.6));
    }
    .gacha-title { font-size: 22px; font-weight: 900; text-align: center; margin-top: 10px; text-transform: uppercase; letter-spacing: 1px; }
    .gacha-universe { font-size: 12px; font-weight: bold; opacity: 0.8; text-transform: uppercase; letter-spacing: 3px; margin-bottom: 5px;}
    .gacha-stars { font-size: 18px; margin-bottom: 5px; text-shadow: 0 0 5px rgba(255, 255, 255, 0.5); }
    
    .rarity-C { border: 5px solid #94a3b8; color: #f8fafc; } 
    .rarity-UC { border: 5px solid #22c55e; color: #22c55e; box-shadow: 0 0 20px rgba(34, 197, 94, 0.3); } 
    .rarity-R { border: 5px solid #3b82f6; color: #3b82f6; box-shadow: 0 0 20px rgba(59, 130, 246, 0.4); } 
    .rarity-SR { border: 5px solid #a855f7; color: #c084fc; box-shadow: 0 0 25px rgba(168, 85, 247, 0.5); } 
    .rarity-UR { border: 5px solid #ef4444; color: #f87171; box-shadow: 0 0 30px rgba(239, 68, 68, 0.6); } 
    .rarity-L { 
        border: 5px solid #fbbf24; 
        color: #fbbf24; 
        background: linear-gradient(135deg, #0f172a 0%, #451a03 100%);
        box-shadow: 0 0 40px rgba(251, 191, 36, 0.8), inset 0 0 20px rgba(251, 191, 36, 0.2); 
    }
    .mem-card {
        aspect-ratio: 1/1; 
        display: flex; 
        align-items: center; 
        justify-content: center;
        background: rgba(30, 41, 59, 0.8);
        border: 2px solid #334155;
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 10px;
    }
    [data-testid="stVerticalBlock"] > div {
        display: flex;
        flex-direction: column;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 📂 AUTO-DÉTECTION DES DOSSIERS
# ==========================================
DOSSIER_DU_JEU = os.path.dirname(os.path.abspath(__file__))
DOSSIER_PORTRAITS = os.path.join(DOSSIER_DU_JEU, "portraits")
DOSSIER_PORTRAITS_ZELDA = os.path.join(DOSSIER_DU_JEU, "portraits_zelda")
DOSSIER_PORTRAITS_HK = os.path.join(DOSSIER_DU_JEU, "portraits_hk")

if not os.path.exists("sauvegardes"):
    os.makedirs("sauvegardes")
    
if "joueur" not in st.session_state:
    st.session_state.joueur = None

if st.session_state.joueur is None:
    st.title("🎮 Connexion au Poké-Hub")
    pseudo = st.text_input("Entre ton pseudo pour jouer :")
    
    if st.button("Entrer dans le jeu"):
        if pseudo.strip():
            st.session_state.joueur = pseudo.strip()
            st.rerun()
            
    st.stop()

# ==========================================
# 📦 ASPIRATION DES BASES DE DONNÉES JSON
# ==========================================
@st.cache_data
def charger_donnees_externes():
    # Chargement de Zelda
    chemin_zelda = os.path.join(DOSSIER_DU_JEU, "zelda_data.json")
    if os.path.exists(chemin_zelda):
        with open(chemin_zelda, "r", encoding="utf-8") as f:
            zelda = json.load(f)
    else:
        zelda = {"Link": {"race": "Hylien", "role": "Héros", "jeu": "The Legend of Zelda", "annee": 1986, "rarete": "Légendaire"}}
        
    # Chargement de Hollow Knight
    chemin_hk = os.path.join(DOSSIER_DU_JEU, "hk_data.json")
    if os.path.exists(chemin_hk):
        with open(chemin_hk, "r", encoding="utf-8") as f:
            hk = json.load(f)
    else:
        hk = {"Le Chevalier": {"rarete": "Ultra Rare"}, "Hornet": {"rarete": "Ultra Rare"}}
        
    return zelda, hk

# Variables globales (Dictionnaires)
ZELDA_DATA, HOLLOW_KNIGHT_PERSOS = charger_donnees_externes()

# --- DICTIONNAIRES POKÉMON ---
TRAD_OEUFS = {"monster": "🦖 Monstre", "water1": "💧 Eau 1", "bug": "🐛 Insectoïde", "flying": "🌪️ Aérien", "ground": "🐾 Terrestre", "fairy": "✨ Féérique", "plant": "🌿 Végétal", "humanshape": "👤 Humanoïde", "water3": "🦑 Eau 3", "mineral": "🪨 Minéral", "indeterminate": "👻 Amorphe", "water2": "🐟 Eau 2", "ditto": "🟣 Métamorph", "dragon": "🐲 Draconique", "no-eggs": "🚫 Aucun"}
TRAD_STATS = {"hp": "❤️ PV", "attack": "⚔️ Attaque", "defense": "🛡️ Défense", "special-attack": "🔮 Att. Spé", "special-defense": "🔰 Déf. Spé", "speed": "⚡ Vitesse"}
TRAD_TYPES = {"normal": "Normal", "fire": "Feu", "water": "Eau", "electric": "Électrik", "grass": "Plante", "ice": "Glace", "fighting": "Combat", "poison": "Poison", "ground": "Sol", "flying": "Vol", "psychic": "Psy", "bug": "Insecte", "rock": "Roche", "ghost": "Spectre", "dragon": "Dragon", "dark": "Ténèbres", "steel": "Acier", "fairy": "Fée"}
GEN_RANGES = {"1G (Kanto)": (1, 151), "2G (Johto)": (152, 251), "3G (Hoenn)": (252, 386), "4G (Sinnoh)": (387, 493), "5G (Unys)": (494, 649), "6G (Kalos)": (650, 721), "7G (Alola)": (722, 809), "8G (Galar)": (810, 905), "9G (Paldea)": (906, 1025)}

# --- FONCTIONS TECHNIQUES ---
def get_base64_image(img_path):
    with open(img_path, "rb") as file:
        return base64.b64encode(file.read()).decode()
    
def get_base64_background(chemin_image):
    """Convertit une image locale en base64 avec un chemin absolu sécurisé."""
    # 1. Trouve le dossier exact où se trouve ton script Python
    dossier_courant = os.path.dirname(os.path.abspath(__file__))
    # 2. Colle ce dossier avec "bannieres/ton_image.jpg"
    chemin_complet = os.path.join(dossier_courant, chemin_image)
    
    if os.path.exists(chemin_complet):
        with open(chemin_complet, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    else:
        # 3. Va afficher une erreur sur ton site avec le chemin exact recherché !
        st.error(f"⚠️ Image introuvable au chemin exact : {chemin_complet}")
        return ""

def get_image_src_for_card(nom, univers):
    """Récupère l'image au format src pour l'injecter dans la carte HTML"""
    nom_u = urllib.parse.quote(nom)
    if univers == "Zelda":
        dossier = DOSSIER_PORTRAITS_ZELDA
        color = "facc15"
    else:
        dossier = DOSSIER_PORTRAITS_HK
        color = "94a3b8"
        
    if os.path.exists(dossier):
        for ext in ['.png', '.jpg', '.jpeg', '.webp', '.PNG', '.JPG', '.JPEG']:
            chemin = os.path.join(dossier, f"{nom}{ext}")
            if os.path.exists(chemin):
                return f"data:image/{ext.lower().replace('.', '')};base64,{get_base64_image(chemin)}"
    # Avatar par défaut si image manquante
    return f"https://ui-avatars.com/api/?name={nom_u}&background=0f172a&color={color}&rounded=true&bold=true&size=150"

def get_zelda_image(nom, size=60, center=False):
    margin_style = "margin: 0 auto 5px auto; display: block;" if center else "margin-right: 12px;"
    src = get_image_src_for_card(nom, "Zelda")
    return f"<img src='{src}' style='width:{size}px; height:{size}px; object-fit:contain; background-color:rgba(15, 23, 42, 0.8); border-radius:50%; border:2px solid #38bdf8; padding:4px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); {margin_style}'>"

def get_hk_image(nom, size=60, center=False):
    margin_style = "margin: 0 auto 5px auto; display: block;" if center else "margin-right: 12px;"
    src = get_image_src_for_card(nom, "Hollow Knight")
    return f"<img src='{src}' style='width:{size}px; height:{size}px; object-fit:contain; background-color:rgba(15, 23, 42, 0.8); border-radius:50%; border:2px solid #94a3b8; padding:4px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); {margin_style}'>"

def generer_carte_html(nom, image_src, rarete, univers):
    """Usine de création de la carte au format HTML"""
    config_rarete = {
        "Commun": {"classe": "rarity-C", "etoiles": "⭐"},
        "Peu Commun": {"classe": "rarity-UC", "etoiles": "⭐⭐"},
        "Rare": {"classe": "rarity-R", "etoiles": "⭐⭐⭐"},
        "Super Rare": {"classe": "rarity-SR", "etoiles": "⭐⭐⭐⭐"},
        "Ultra Rare": {"classe": "rarity-UR", "etoiles": "⭐⭐⭐⭐⭐"},
        "Légendaire": {"classe": "rarity-L", "etoiles": "🌟🌟🌟🌟🌟🌟"}
    }
    
    style = config_rarete.get(rarete, config_rarete["Commun"])
    
    carte_html = f"""
    <div class="gacha-card {style['classe']}">
        <div class="gacha-universe">{univers}</div>
        <div class="gacha-img-container">
            <img src="{image_src}">
        </div>
        <div style="width: 100%;">
            <div class="gacha-stars">{style['etoiles']}</div>
            <div class="gacha-title">{nom}</div>
            <div style="font-size: 11px; color: inherit; opacity: 0.8; text-transform: uppercase; text-align: center; margin-top: 5px; font-weight: bold;">{rarete}</div>
        </div>
    </div>
    """
    return carte_html

@st.cache_data
def charger_noms_fr():
    try:
        query = """query { pokemon_v2_pokemonspeciesname(where: {language_id: {_eq: 5}}) { name pokemon_species_id } }"""
        response = requests.post("https://beta.pokeapi.co/graphql/v1beta", json={"query": query}, timeout=5).json()
        noms = response['data']['pokemon_v2_pokemonspeciesname']
        dict_noms = {f"{item['name']} (#{item['pokemon_species_id']})": item['pokemon_species_id'] for item in noms if item['pokemon_species_id'] <= 1025}
        return dict(sorted(dict_noms.items(), key=lambda item: item[1]))
    except:
        return {"Pikachu (#25)": 25}

def charger_un_pokemon(p_id):
    try:
        data = requests.get(f"https://pokeapi.co/api/v2/pokemon/{p_id}", timeout=3).json()
        species = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{p_id}", timeout=3).json()
        nom_fr = next(entry["name"] for entry in species["names"] if entry["language"]["name"] == "fr")
        return {"nom": nom_fr, "image": data["sprites"]["front_default"]}
    except:
        return None

def get_pokemon_wordle_data(p_id):
    try:
        data = requests.get(f"https://pokeapi.co/api/v2/pokemon/{p_id}", timeout=3).json()
        species = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{p_id}", timeout=3).json()
        nom_fr = next(entry["name"] for entry in species["names"] if entry["language"]["name"] == "fr")
        types = [t["type"]["name"] for t in data["types"]]
        type1 = TRAD_TYPES.get(types[0], types[0].capitalize())
        type2 = TRAD_TYPES.get(types[1], types[1].capitalize()) if len(types) > 1 else "Aucun"
        gen_name = species["generation"]["name"]
        gen_dict = {"generation-i": 1, "generation-ii": 2, "generation-iii": 3, "generation-iv": 4, "generation-v": 5, "generation-vi": 6, "generation-vii": 7, "generation-viii": 8, "generation-ix": 9}
        return {"id": p_id, "nom": nom_fr, "image": data["sprites"]["front_default"], "gen": gen_dict.get(gen_name, 1), "type1": type1, "type2": type2, "taille": data["height"] / 10, "poids": data["weight"] / 10}
    except:
        return None

def extraire_adn_couleurs(image_url):
    try:
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        couleurs = img.getcolors(img.size[0] * img.size[1])
        couleurs_valides = [c for c in couleurs if c[1][3] > 10]
        couleurs_valides.sort(reverse=True, key=lambda x: x[0])
        top_5 = [f"rgb({c[1][0]},{c[1][1]},{c[1][2]})" for c in couleurs_valides[:5]]
        while len(top_5) < 5: top_5.append("rgb(0,0,0)")
        return top_5
    except:
        return ["#ccc", "#999", "#666", "#333", "#000"]
    
    # --- SYSTÈME DE COLLECTION ---
FICHIER_COLLECTION = os.path.join(DOSSIER_DU_JEU, "collection.json")

def get_chemin_joueur(nom_joueur):
    # Génère un chemin propre du type : sauvegardes/link.json
    return os.path.join("sauvegardes", f"{nom_joueur.lower()}.json")

def charger_collection(nom_joueur):
    chemin = get_chemin_joueur(nom_joueur)
    if os.path.exists(chemin):
        try:
            with open(chemin, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Sécurité : si le joueur n'a pas de jetons, on lui en donne 500
                if "jetons" not in data:
                    data["jetons"] = 500
                return data
        except Exception:
            pass # Si le fichier a un bug, on l'ignore et on charge par défaut
            
    # Nouveau joueur : profil par défaut
    return {"jetons": 500, "Zelda": {}, "Hollow Knight": {}, "Pokémon": {}}

def sauvegarder_collection(nom_joueur, collection):
    chemin = get_chemin_joueur(nom_joueur)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(collection, f, indent=4, ensure_ascii=False)

def ajouter_jetons(nom_joueur, montant):
    collec = charger_collection(nom_joueur)
    collec["jetons"] = collec.get("jetons", 500) + montant
    sauvegarder_collection(nom_joueur, collec)
        
def preparer_deck_memory(taille=12):
    """Récupère des images aléatoires dans les dossiers pour faire des paires."""
    chemins_images = []
    # On scanne les dossiers pour trouver des images
    for dossier in [DOSSIER_PORTRAITS_ZELDA, DOSSIER_PORTRAITS_HK]:
        if os.path.exists(dossier):
            for f in os.listdir(dossier):
                if f.endswith(('.png', '.jpg', '.webp')):
                    chemins_images.append(os.path.join(dossier, f))
    
    # On en choisit la moitié (pour faire les paires)
    choix = random.sample(chemins_images, taille // 2)
    deck = choix * 2
    random.shuffle(deck)
    return deck

# ==========================================
# 📊 BARRE LATÉRALE DE NAVIGATION
# ==========================================
collec = charger_collection(st.session_state.joueur)
st.sidebar.markdown("## 🔴 Poké-Hub Web")
st.sidebar.markdown(f"👤 Connecté : **{st.session_state.joueur}**")
st.sidebar.markdown(f"### 🪙 Solde : `{collec.get('jetons', 500)} 🪙`")
st.sidebar.markdown("---")
mode_choisi = st.sidebar.radio(
    "🕹️ SÉLECTION DU MODE",
    [
        "🏠 Accueil", 
        "🎰 Portail d'Invocation (Gacha)",
        "🗂️ Mon Classeur (Collection)",
        "🎫 Ticket à Gratter (Casino)",
        "🃏 Memory des Héros (Jeu de Paires)",
        "👁️ Détecteur Sheikah (Zelda Wordle)",
        "🟩 Poké-Wordle (Déduction)",
        "🎒 Blind Starter (Audio)", 
        "🔢 Blind Starter (Pokédex)",
        "📊 Blind Starter (Meilleure Stat)",
        "🥚 Blind Starter (Incubateur)", 
        "🔎 Blind Starter (Zoom)", 
        "🧬 Blind Starter (Labo Scanners)", 
        "🕵️‍♂️ Qui est-ce ? (Pokémon)", 
        "⚔️ Qui est-ce ? (Smash Bros)",
        "🧝‍♂️ Qui est-ce ? (Zelda)",
        "🪲 Qui est-ce ? (Hollow Knight)"
    ]
)
st.sidebar.markdown("---")
st.sidebar.caption("© Poké-Hub 2026 - Propulsé par la Magie du Code")

# ==========================================
# 🏠 MODE : ACCUEIL
# ==========================================
if mode_choisi == "🏠 Accueil":
    st.title("🎮 Bienvenue sur le Poké-Hub")
    st.markdown("### La borne d'arcade multijoueur ultime.")
    st.write("Sélectionne un mode de jeu dans le menu à gauche pour défier tes amis !")
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**🎰 Le Gacha Multivers**\n\nInvoque des cartes légendaires de tes licences préférées !")
        st.info("**👁️ Détecteur Sheikah (Zelda)**\n\nIdentifie le personnage ou monstre culte de la saga Zelda !")
        st.info("**🟩 Poké-Wordle**\n\nDéduis le Pokémon secret grâce aux indices.")
        st.success("**🕵️‍♂️ 4x Modes Qui est-ce ?**\n\nGrilles aléatoires sur Zelda, Hollow Knight, Pokémon et Smash Bros.")
    with col2:
        st.warning("**🎒 Les 6 Modes Blind Starter**\n\nDevine ton compagnon de route avec différentes mécaniques :\n* **Audio :** Reconnais son cri\n* **Pokédex :** À l'aide de son numéro national\n* **Statistiques :** Via sa meilleure stat de base\n* **Incubateur :** Selon son groupe d'œuf\n* **Zoom :** Son sprite grossi 9 fois\n* **Labo Scanners :** Analyse son ADN et sa silhouette")

# ==========================================
# 🎰 MODE : GACHA (PORTAIL D'INVOCATION)
# ==========================================
elif mode_choisi == "🎰 Portail d'Invocation (Gacha)":
    collec = charger_collection(st.session_state.joueur)
    
    # --- CALCUL DU PORTAIL BOOSTÉ DU JOUR (Rotation automatique toutes les 24h) ---
    univers_dispos = ["Zelda", "Hollow Knight", "Pokémon"]
    jour_de_l_an = datetime.date.today().timetuple().tm_yday
    univers_booste = univers_dispos[jour_de_l_an % len(univers_dispos)]
    
    # --- 1. SÉLECTION DU PORTAIL (Avec indicateur visuel de boost) ---
    label_zelda = "Portail Zelda 🧝‍♂️" + (" 🔥 BOOSTÉ !" if univers_booste == "Zelda" else "")
    label_hk = "Portail Hollow Knight 🪲" + (" 🔥 BOOSTÉ !" if univers_booste == "Hollow Knight" else "")
    label_pkmn = "Portail Pokémon 🔴" + (" 🔥 BOOSTÉ !" if univers_booste == "Pokémon" else "")
    
    univers_choisi = st.selectbox(
        "Choisissez votre portail :", 
        ["Mélange Multivers 🌌", label_zelda, label_hk, label_pkmn]
    )
    
    # --- 2. DÉTERMINATION DU PORTAIL SÉLECTIONNÉ ---
    if "Zelda" in univers_choisi:
        est_booste = (univers_booste == "Zelda")
        titre = "🌿 PORTAIL D'HYRULE 🗡️" + (" 🔥 BOOSTÉ 🔥" if est_booste else "")
        desc = "Invoquez les héros et créatures du royaume d'Hyrule !"
        chemin_bg = "bannieres/zelda_bg.jpg"
        bord = "#22c55e" if not est_booste else "#facc15" # Bordure dorée si boosté
    elif "Hollow Knight" in univers_choisi:
        est_booste = (univers_booste == "Hollow Knight")
        titre = "🕸️ PORTAIL D'HALLOWNEST 🪲" + (" 🔥 BOOSTÉ 🔥" if est_booste else "")
        desc = "Réveillez les insectes et les ombres du royaume déchu !"
        chemin_bg = "bannieres/hk_bg.jpg"
        bord = "#64748b" if not est_booste else "#facc15"
    elif "Pokémon" in univers_choisi:
        est_booste = (univers_booste == "Pokémon")
        titre = "🔴 PORTAIL POKÉMON ⚪" + (" 🔥 BOOSTÉ 🔥" if est_booste else "")
        desc = "Attrapez-les tous ! Invoquez des créatures de toutes générations."
        chemin_bg = "bannieres/pokemon_bg.jpg"
        bord = "#f87171" if not est_booste else "#facc15"
    else:
        est_booste = False
        titre = "🌌 PORTAIL DU MULTIVERS 🌌"
        desc = "Invoquez les héros les plus puissants des mondes oubliés !"
        chemin_bg = "bannieres/multivers_bg.jpg"
        bord = "#a855f7"

    # Affichage des taux dynamiques dans la bannière
    taux_txt = "✨ Légendaire : 2% | Ultra Rare : 12% (🔥 TAUX DOUBLÉS !)" if est_booste else "✨ Légendaire : 1% | Ultra Rare : 6% | Super Rare : 15%"

    # Conversion et affichage de la bannière
    bg_b64 = get_base64_background(chemin_bg)
    fond_css = f"url('data:image/jpeg;base64,{bg_b64}')" if bg_b64 else "#0f172a"

    st.markdown(f"""
        <div style="background-image: linear-gradient(rgba(0, 0, 0, 0.65), rgba(0, 0, 0, 0.75)), {fond_css}; 
                    background-size: cover; background-position: center;
                    padding: 30px; border-radius: 20px; text-align: center; color: white; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.5); border: 3px solid {bord}; margin-bottom: 25px;">
            <h1 style="margin:0; font-size: 35px; text-shadow: 0 0 15px {bord};">{titre}</h1>
            <p style="color: #f1f5f9; font-size: 18px; margin-top: 10px;">{desc}</p>
            <div style="margin-top: 15px; font-size: 14px; background: rgba(0,0,0,0.6); display: inline-block; padding: 6px 20px; border-radius: 30px; border: 1px solid {bord}; font-weight: bold;">
                {taux_txt}
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.write(f"🪙 **Solde actuel :** `{collec.get('jetons', 0)} Jetons`")
    
    # --- 3. BOUTONS ---
    c1, c2 = st.columns(2)
    with c1:
        btn_1 = st.button("🌟 TIRAGE UNIQUE (100 🪙)", use_container_width=True)
    with c2:
        btn_5 = st.button("💫 MULTI-TIRAGE x5 (500 🪙)", use_container_width=True, type="primary")

    zone_resultats = st.empty()

    # --- 4. LOGIQUE DES TIRAGES ---
    if btn_1 or btn_5:
        nb_tirages = 5 if btn_5 else 1
        cout = nb_tirages * 100
        
        if collec.get('jetons', 0) < cout:
            st.error(f"❌ Fonds insuffisants ! Il vous faut {cout} 🪙.")
        else:
            ajouter_jetons(st.session_state.joueur,-cout)
            collec = charger_collection(st.session_state.joueur)
            
            with zone_resultats.container():
                with st.spinner("Invocation en cours..."):
                    cols_resultat = st.columns(nb_tirages)
                    il_y_a_du_lourd = False

                    for i in range(nb_tirages):
                        # Détermination de l'univers pour ce tirage précis
                        if "Mélange Multivers" in univers_choisi:
                            univers_tire = random.choice(["Zelda", "Hollow Knight", "Pokémon"])
                            # Le mélange profite du boost si l'univers choisi au hasard est celui du jour !
                            tirage_est_booste = (univers_tire == univers_booste)
                        else:
                            univers_tire = univers_booste if est_booste else univers_choisi.replace("Portail ", "").replace(" 🧝‍♂️", "").replace(" 🪲", "").replace(" 🔴", "")
                            tirage_est_booste = est_booste

                        if univers_tire in ["Zelda", "Hollow Knight"]:
                            jet = random.randint(1, 100)
                            
                            # ⚖️ APPLICATION DES TAUX (Doublés si boosté)
                            if tirage_est_booste:
                                if jet <= 2: rarete_cible = "Légendaire"       # 2% au lieu de 1%
                                elif jet <= 12: rarete_cible = "Ultra Rare"    # 10% de + (total 12%)
                                elif jet <= 25: rarete_cible = "Super Rare"
                                elif jet <= 45: rarete_cible = "Rare"
                                elif jet <= 70: rarete_cible = "Peu Commun"
                                else: rarete_cible = "Commun"
                            else:
                                if jet <= 1: rarete_cible = "Légendaire"
                                elif jet <= 6: rarete_cible = "Ultra Rare"
                                elif jet <= 15: rarete_cible = "Super Rare"
                                elif jet <= 30: rarete_cible = "Rare"
                                elif jet <= 60: rarete_cible = "Peu Commun"
                                else: rarete_cible = "Commun"

                            bdd = ZELDA_DATA if univers_tire == "Zelda" else HOLLOW_KNIGHT_PERSOS
                            candidats = [n for n, d in bdd.items() if d.get("rarete", "Commun") == rarete_cible]
                            if not candidats: candidats = list(bdd.keys())
                            nom_tire = random.choice(candidats)
                            rarete_finale = bdd[nom_tire].get("rarete", "Commun")
                            img_src = get_image_src_for_card(nom_tire, univers_tire)
                        else:
                            # Tirage Pokémon
                            p_id = random.randint(1, 1025)
                            try:
                                d_pkmn = requests.get(f"https://pokeapi.co/api/v2/pokemon/{p_id}").json()
                                s_pkmn = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{p_id}").json()
                                nom_tire = next(e["name"] for e in s_pkmn["names"] if e["language"]["name"] == "fr")
                                img_src = d_pkmn["sprites"]["other"]["official-artwork"]["front_default"] or d_pkmn["sprites"]["front_default"]
                                
                                is_leg = s_pkmn.get("is_legendary", False) or s_pkmn.get("is_mythical", False)
                                bst = sum([s["base_stat"] for s in d_pkmn["stats"]])
                                
                                # Si le portail Pokémon est boosté, on baisse les requis de statistiques !
                                if tirage_est_booste:
                                    if is_leg or random.randint(1, 50) == 1: rarete_finale = "Légendaire" # Chance brute en plus
                                    elif bst >= 550: rarete_finale = "Ultra Rare"
                                    elif bst >= 450: rarete_finale = "Super Rare"
                                    elif bst >= 350: rarete_finale = "Rare"
                                    else: rarete_finale = "Commun"
                                else:
                                    if is_leg: rarete_finale = "Légendaire"
                                    elif bst >= 600: rarete_finale = "Ultra Rare"
                                    elif bst >= 500: rarete_finale = "Super Rare"
                                    elif bst >= 400: rarete_finale = "Rare"
                                    elif bst >= 300: rarete_finale = "Peu Commun"
                                    else: rarete_finale = "Commun"
                            except:
                                nom_tire = "Erreur Pokémon"; img_src = ""; rarete_finale = "Commun"

                        # Enregistrement
                        if univers_tire not in collec: collec[univers_tire] = {}
                        if nom_tire in collec[univers_tire]:
                            collec[univers_tire][nom_tire]["quantite"] += 1
                        else:
                            collec[univers_tire][nom_tire] = {"rarete": rarete_finale, "image": img_src, "quantite": 1}
                        
                        if rarete_finale in ["Ultra Rare", "Légendaire"]: il_y_a_du_lourd = True

                        # Affichage des cartes invoquées
                        with cols_resultat[i]:
                            carte_html = generer_carte_html(nom_tire, img_src, rarete_finale, univers_tire)
                            st.markdown(f"<div style='transform: scale(0.85); margin: -20px 0;'>{carte_html}</div>", unsafe_allow_html=True)
                            st.caption(f"**{nom_tire}** ({rarete_finale})")

                    sauvegarder_collection(st.session_state.joueur, collec)
                    
                    if il_y_a_du_lourd: st.balloons()
                    st.success(f"🎉 Invocation terminée ! Nouveau solde : {collec['jetons']} 🪙")
            
# ==========================================
# 🗂️ MODE : MON CLASSEUR (COLLECTION)
# ==========================================
elif mode_choisi == "🗂️ Mon Classeur (Collection)":
    st.title("🗂️ Classeur Multivers")
    collec = charger_collection(st.session_state.joueur)
    
    # Statistiques
    cartes_uniques = 0
    for u, p in collec.items():
        if isinstance(p, dict): cartes_uniques += len(p)
    
    st.write(f"Vous possédez **{cartes_uniques}** cartes uniques différentes.")
    st.divider()
    
    f_univ = st.radio("Afficher l'univers :", ["Tous", "Zelda", "Hollow Knight", "Pokémon"], horizontal=True)
    
    # Extraction sécurisée
    cartes = []
    for u, p in collec.items():
        if u != "jetons" and isinstance(p, dict):
            if f_univ == "Tous" or f_univ == u:
                for n, i in p.items():
                    # i doit être un dictionnaire. Si ce n'est pas le cas, on ignore
                    if isinstance(i, dict):
                        cartes.append((u, n, i))
    
    ordre = {"Légendaire": 1, "Ultra Rare": 2, "Super Rare": 3, "Rare": 4, "Peu Commun": 5, "Commun": 6}
    cartes.sort(key=lambda x: (ordre.get(x[2].get("rarete", "Commun"), 7), x[1]))
    
    if not cartes:
        st.warning("📭 Classeur vide ! Allez invoquer des cartes.")
    else:
        cols = st.columns(4)
        for idx, (u, n, i) in enumerate(cartes):
            with cols[idx % 4]:
                # Extraction sécurisée des données de la carte
                img_src = i.get("image", "")
                rarete = i.get("rarete", "Commun")
                qte = i.get("quantite", 1)
                
                # Génération HTML avec fallback si image manquante
                html = generer_carte_html(n, img_src, rarete, u)
                badge = f"<div style='background-color:#ef4444; color:white; border-radius:50%; width:30px; height:30px; display:flex; justify-content:center; align-items:center; font-weight:bold; position:absolute; z-index:10; right:10px; top:10px; box-shadow:0 4px 6px rgba(0,0,0,0.5);'>x{qte}</div>"
                st.markdown(f"<div style='position:relative; display:flex; justify-content:center; transform: scale(0.85); margin: -20px;'>{badge}{html}</div>", unsafe_allow_html=True)

# ==========================================
# 🎫 TICKET À GRATTER (CASINO)
# ==========================================
elif mode_choisi == "🎫 Ticket à Gratter (Casino)":
    st.title("🎫 Le Gratte-Gratte du Multivers")
    st.write("Trouvez les 3 💎 pour le Jackpot (+300 🪙) ! La 💣 vous fait perdre 2 coups d'un coup. Vous avez **8 coups maximum**.")
    
    # 🎨 INJECTION CSS
    st.markdown("""
        <style>
        button[kind="secondary"] {
            height: 120px !important;
            font-size: 40px !important;
            border-radius: 16px !important;
            background-color: rgba(30, 41, 59, 0.5) !important;
            border: 2px dashed rgba(255, 255, 255, 0.2) !important;
            transition: all 0.2s ease !important;
        }
        button[kind="secondary"]:hover {
            background-color: rgba(30, 41, 59, 0.8) !important;
            border-color: #facc15 !important;
            transform: scale(1.02) !important;
        }
        .scratch-revealed {
            height: 120px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 50px;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
            margin-bottom: 16px;
        }
        .diamant { background: linear-gradient(135deg, #0284c7, #38bdf8); border: 2px solid #7dd3fc; }
        .piece { background: linear-gradient(135deg, #ca8a04, #facc15); border: 2px solid #fef08a; }
        .bombe { background: linear-gradient(135deg, #991b1b, #ef4444); border: 2px solid #fca5a5; }
        div[data-testid="stMarkdownContainer"] p { margin-bottom: 0 !important; }
        </style>
    """, unsafe_allow_html=True)

    collec = charger_collection(st.session_state.joueur)
    PRIX_TICKET = 50
    
    st.markdown(f"**Solde actuel :** `{collec.get('jetons', 0)} 🪙`")
    st.divider()

    if "scratch_grid" not in st.session_state:
        # Grille 12 cases : 3 Diamants, 1 Bombe, 8 Pièces.
        st.session_state.scratch_grid = ["💎", "💎", "💎", "💣", "🪙", "🪙", "🪙", "🪙", "🪙", "🪙", "🪙", "🪙"]
        random.shuffle(st.session_state.scratch_grid)
        st.session_state.scratch_rev = [False] * 12
        st.session_state.scratch_coups_restants = 8  # <-- Changé ici à 8
        st.session_state.scratch_diamants = 0
        st.session_state.scratch_over = False
        st.session_state.scratch_bombe_hit = False

    grid = st.session_state.scratch_grid
    rev = st.session_state.scratch_rev
    coups = st.session_state.scratch_coups_restants
    diams = st.session_state.scratch_diamants

    # Zone de statut au-dessus de la grille
    if not st.session_state.scratch_over:
        c1, c2 = st.columns(2)
        c1.info(f"👉 Coups restants : **{max(0, coups)}** / 8")  # <-- Changé ici à 8
        c2.warning(f"💎 Diamants trouvés : **{diams}** / 3")
    else:
        if diams == 3:
            st.success("🎉 JACKPOT ! Vous avez trouvé les 3 Diamants ! (+300 🪙)")
            st.balloons()
        elif st.session_state.scratch_bombe_hit:
            st.warning("💥 Ticket terminé ! La bombe a soufflé vos derniers coups, mais vous gardez vos pièces.")
        else:
            st.info("Ticket terminé ! Plus de coups disponibles. Vous conservez vos pièces grattées.")
            
        if st.button(f"Acheter un nouveau ticket ({PRIX_TICKET} 🪙) 🔄", type="primary"):
            if collec.get("jetons", 0) >= PRIX_TICKET:
                ajouter_jetons(st.session_state.joueur, -PRIX_TICKET) 
                del st.session_state.scratch_grid
                st.rerun()
            else:
                st.error("Fonds insuffisants pour racheter un ticket.")

    # Affichage de la grille 3x4
    for row in range(3):
        cols = st.columns(4)
        for col in range(4):
            idx = row * 4 + col
            with cols[col]:
                if rev[idx] or st.session_state.scratch_over:
                    opacity = "1" if rev[idx] else "0.3"
                    if grid[idx] == "💎":
                        st.markdown(f"<div class='scratch-revealed diamant' style='opacity:{opacity};'>💎</div>", unsafe_allow_html=True)
                    elif grid[idx] == "💣":
                        st.markdown(f"<div class='scratch-revealed bombe' style='opacity:{opacity};'>💣</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='scratch-revealed piece' style='opacity:{opacity};'>🪙</div>", unsafe_allow_html=True)
                else:
                    if st.button("❓", key=f"scr_{idx}", use_container_width=True, disabled=st.session_state.scratch_over):
                        st.session_state.scratch_rev[idx] = True
                        st.session_state.scratch_coups_restants -= 1
                        
                        # Logique des cases
                        if grid[idx] == "💣":
                            st.session_state.scratch_bombe_hit = True
                            st.session_state.scratch_coups_restants -= 2
                            st.toast("💥 Aïe ! La bombe vous fait perdre 2 coups supplémentaires !")
                        elif grid[idx] == "💎":
                            st.session_state.scratch_diamants += 1
                            if st.session_state.scratch_diamants == 3:
                                ajouter_jetons(st.session_state.joueur, 300)
                                st.session_state.scratch_over = True
                        elif grid[idx] == "🪙":
                            ajouter_jetons(st.session_state.joueur, 10)
                            
                        # Vérification de fin de jeu
                        if st.session_state.scratch_coups_restants <= 0:
                            st.session_state.scratch_coups_restants = 0
                            st.session_state.scratch_over = True
                            
                        st.rerun()
                        
# ==========================================
# 🃏 MEMORY DES HÉROS (JEU DE PAIRES)
# ==========================================
elif mode_choisi == "🃏 Memory des Héros (Jeu de Paires)":
    st.title("🃏 Memory des Héros")
    
    # 🎨 INJECTION CSS 
    st.markdown("""
        <style>
        /* Force la taille de TOUS les boutons des cartes (dos) */
        button[kind="secondary"] {
            height: 140px !important;
            width: 100% !important;
            border-radius: 16px !important;
            background-color: rgba(30, 41, 59, 0.5) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            font-size: 50px !important;
            box-shadow: 0 8px 32px 0 rgba(0,0,0,0.3) !important;
            transition: all 0.2s ease !important;
        }
        button[kind="secondary"]:hover {
            border-color: #38bdf8 !important;
            transform: scale(1.02) !important;
            background-color: rgba(30, 41, 59, 0.8) !important;
        }
        /* Supprime les marges parasites de Streamlit sous le HTML */
        div[data-testid="stMarkdownContainer"] p {
            margin-bottom: 0 !important;
        }
        /* Classe CSS pour la carte retournée (face) */
        .mem-card-face {
            height: 140px; 
            width: 100%; 
            border-radius: 16px; 
            background: rgba(30, 41, 59, 0.5); 
            border: 1px solid rgba(255, 255, 255, 0.1); 
            box-shadow: 0 8px 32px 0 rgba(0,0,0,0.3); 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            overflow: hidden;
            box-sizing: border-box;
            margin-bottom: 16px; /* <-- LA CORRECTION : Ajoute l'espacement entre les lignes ! */
        }
        </style>
    """, unsafe_allow_html=True)

    collec = charger_collection(st.session_state.joueur)
    
    if "mem_grid" not in st.session_state:
        st.session_state.mem_grid = preparer_deck_memory(taille=16)
        st.session_state.mem_rev = [False] * 16
        st.session_state.mem_picks = []

    grid, rev, picks = st.session_state.mem_grid, st.session_state.mem_rev, st.session_state.mem_picks

    cols = st.columns(4)
    
    for i in range(16):
        with cols[i % 4]:
            if rev[i]:
                img_b64 = get_base64_image(grid[i])
                # La face de la carte
                st.markdown(f"""
                    <div class='mem-card-face'>
                        <img src='data:image/png;base64,{img_b64}' style='max-width: 90%; max-height: 90%; object-fit: contain; filter: drop-shadow(0px 5px 10px rgba(0,0,0,0.5));'>
                    </div>
                """, unsafe_allow_html=True)
            else:
                # Le dos de la carte
                if st.button("🎴", key=f"mem_{i}", use_container_width=True, disabled=(len(picks) >= 2)):
                    st.session_state.mem_rev[i] = True
                    st.session_state.mem_picks.append(i)
                    st.rerun()

    # Logique de vérification
    if len(picks) == 2:
        time.sleep(1.5) 
        idx1, idx2 = picks[0], picks[1]
        if grid[idx1] == grid[idx2]:
            st.toast("✅ Paire trouvée ! (+20 🪙)")
            ajouter_jetons(st.session_state.joueur, 20)
        else:
            st.toast("❌ Ce n'est pas une paire...")
            st.session_state.mem_rev[idx1] = False
            st.session_state.mem_rev[idx2] = False
            
        st.session_state.mem_picks = []
        st.rerun()

    st.divider()
    # Le bouton "Relancer" reste normal car il a l'attribut type="primary"
    if st.button("Relancer la partie 🔄", type="primary"):
        del st.session_state.mem_grid
        del st.session_state.mem_rev
        del st.session_state.mem_picks
        st.rerun()

# ==========================================
# 👁️ MODE : DÉTECTEUR SHEIKAH (ZELDA WORDLE)
# ==========================================
elif mode_choisi == "👁️ Détecteur Sheikah (Zelda Wordle)":
    st.title("👁️ Détecteur Sheikah : Archive d'Hyrule")
    st.write("Déduisez l'identité secrète de l'archive (Personnages et Monstres) issue de la chronologie complète de Zelda !")
    st.caption("Flèches : 🔼 La première apparition du secret est plus RÉCENTE | 🔽 Le secret est plus ANCIEN.")
    
    if not os.path.exists(DOSSIER_PORTRAITS_ZELDA):
        st.info("💡 Astuce : Créez un dossier 'portraits_zelda' contenant les images de vos personnages pour remplacer les avatars !")

    tous_les_zelda = list(ZELDA_DATA.keys()) if isinstance(ZELDA_DATA, dict) else []

    if "z_secret_name" not in st.session_state:
        st.session_state.z_secret_name = random.choice(tous_les_zelda)
        st.session_state.z_essais = []
        st.session_state.z_gagne = False
        
    secret_item = ZELDA_DATA[st.session_state.z_secret_name]
    
    if not st.session_state.z_gagne:
        c_in, c_bt = st.columns([3, 1])
        with c_in:
            guess_z = st.selectbox("Sélectionnez un personnage ou monstre :", ["-- Analyse requise --"] + sorted(tous_les_zelda))
        with c_bt:
            st.write("")
            if st.button("Scanner l'Archive 🕵️‍♂️", use_container_width=True, type="primary"):
                if guess_z != "-- Analyse requise --":
                    guess_data = ZELDA_DATA[guess_z].copy()
                    guess_data['nom'] = guess_z
                    if not any(e['nom'] == guess_z for e in st.session_state.z_essais):
                        st.session_state.z_essais.append(guess_data)
                    if guess_z == st.session_state.z_secret_name:
                        st.session_state.z_gagne = True
                    st.rerun()

        with st.expander("💡 Besoin d'un indice ?"):
            if len(st.session_state.z_essais) >= 5:
                st.write(f"La première lettre de l'entité est : **{st.session_state.z_secret_name[0].upper()}**")
                st.write(f"La toute dernière lettre est : **{st.session_state.z_secret_name[-1].upper()}**")
            elif len(st.session_state.z_essais) >= 3:
                st.write(f"La première lettre de l'entité est : **{st.session_state.z_secret_name[0].upper()}**")
                st.write("*(Faites 5 essais pour débloquer le prochain indice)*")
            else:
                st.write("Faites au moins 3 analyses pour débloquer le premier indice !")

    if st.session_state.z_gagne:
        st.balloons()
        st.success(f"🏆 IDENTIFICATION RÉUSSIE ! C'était bien : **{st.session_state.z_secret_name}** !")
        img_victoire_html = get_zelda_image(st.session_state.z_secret_name, size=200, center=True)
        st.markdown(f"<div>{img_victoire_html}</div>", unsafe_allow_html=True)
        st.write("")
        if st.button("Recharger un nouveau fichier Sheikah 🔄"):
            del st.session_state.z_secret_name
            st.rerun()
            
    st.divider()
    
    if st.session_state.z_essais:
        col_h1, col_h2, col_h3, col_h4, col_h5 = st.columns([2, 1.5, 1.5, 2, 1.5])
        with col_h1: st.write("**Entité**")
        with col_h2: st.write("**Espèce**")
        with col_h3: st.write("**Rôle**")
        with col_h4: st.write("**Premier Jeu**")
        with col_h5: st.write("**Année**")
        
        for essai in reversed(st.session_state.z_essais):
            if essai['race'] == secret_item['race']: race_html = f"<div class='w-box w-green'>{essai['race']}</div>"
            else: race_html = f"<div class='w-box w-red'>{essai['race']}</div>"
            
            role_essai = essai['role']
            role_secret = secret_item['role']
            est_allie = lambda r: r in ["Allié", "Alliée"]
            
            if role_essai == role_secret or (est_allie(role_essai) and est_allie(role_secret)):
                role_html = f"<div class='w-box w-green'>{essai['role']}</div>"
            else:
                role_html = f"<div class='w-box w-red'>{essai['role']}</div>"
            
            if essai['jeu'] == secret_item['jeu']: jeu_html = f"<div class='w-box w-green'>{essai['jeu']}</div>"
            else: jeu_html = f"<div class='w-box w-red'>{essai['jeu']}</div>"

            if essai['annee'] == secret_item['annee']: annee_html = f"<div class='w-box w-green'>{essai['annee']} ✅</div>"
            elif essai['annee'] < secret_item['annee']: annee_html = f"<div class='w-box w-red'>{essai['annee']} 🔼</div>"
            else: annee_html = f"<div class='w-box w-red'>{essai['annee']} 🔽</div>"
            
            avatar_html = get_zelda_image(essai['nom'], size=50)

            c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1.5, 2, 1.5])
            with c1: st.markdown(f"<div style='display:flex; align-items:center; background-color: rgba(0,0,0,0.2); border-radius:10px; padding:5px;'>{avatar_html} <b>{essai['nom']}</b></div>", unsafe_allow_html=True)
            with c2: st.markdown(race_html, unsafe_allow_html=True)
            with c3: st.markdown(role_html, unsafe_allow_html=True)
            with c4: st.markdown(jeu_html, unsafe_allow_html=True)
            with c5: st.markdown(annee_html, unsafe_allow_html=True)

# ==========================================
# 🟩 MODE : POKÉ-WORDLE
# ==========================================
elif mode_choisi == "🟩 Poké-Wordle (Déduction)":
    st.title("🟩 Le Poké-Wordle")
    st.write("Trouvez le Pokémon secret ! Tapez un nom, et des indices colorés vous guideront.")
    st.caption("Couleurs : 🟩 = Parfait | 🟨 = Mauvaise position (Type) | 🟥 = Incorrect.")

    gens_choisies = st.multiselect("Sélectionnez les générations à inclure :", list(GEN_RANGES.keys()), default=["1G (Kanto)"])

    if not gens_choisies:
        st.warning("⚠️ Veuillez sélectionner au moins une génération pour jouer.")
    else:
        ids_disponibles = []
        for g in gens_choisies:
            debut, fin = GEN_RANGES[g]
            ids_disponibles.extend(range(debut, fin + 1))

        if "wordle_secret" not in st.session_state or st.session_state.get("wordle_gens") != gens_choisies:
            st.session_state.wordle_secret = random.choice(ids_disponibles)
            st.session_state.wordle_gens = gens_choisies
            st.session_state.wordle_essais = []
            st.session_state.wordle_gagne = False
            with st.spinner("Analyse du Pokémon secret en cours..."):
                st.session_state.wordle_secret_data = get_pokemon_wordle_data(st.session_state.wordle_secret)

        secret = st.session_state.wordle_secret_data
        
        if not st.session_state.wordle_gagne:
            dict_noms = charger_noms_fr()
            noms_disponibles = [nom for nom, p_id in dict_noms.items() if p_id in ids_disponibles]
            
            c_input, c_btn = st.columns([3, 1])
            with c_input:
                guess_nom = st.selectbox("Tapez ou cherchez le nom d'un Pokémon :", ["-- Sélectionner un Pokémon --"] + noms_disponibles)
            with c_btn:
                st.write("") 
                if st.button("Deviner 🔍", use_container_width=True, type="primary"):
                    if guess_nom != "-- Sélectionner un Pokémon --":
                        guess_id = dict_noms[guess_nom]
                        with st.spinner("Vérification..."):
                            guess_data = get_pokemon_wordle_data(guess_id)
                            if guess_data:
                                st.session_state.wordle_essais.append(guess_data)
                                if guess_id == st.session_state.wordle_secret:
                                    st.session_state.wordle_gagne = True
                        st.rerun()

        if st.session_state.wordle_gagne:
            st.balloons()
            st.success(f"🏆 INCROYABLE ! Vous avez trouvé **{secret['nom']}** !")
            if st.button("Relancer une partie avec ces filtres 🔄"):
                del st.session_state.wordle_secret
                st.rerun()

        st.divider()
        if st.session_state.wordle_essais:
            h1, h2, h3, h4, h5 = st.columns([2, 1, 2, 1.5, 1.5])
            with h1: st.write("**Pokémon**");
            with h2: st.write("**Génération**");
            with h3: st.write("**Types**");
            with h4: st.write("**Taille**");
            with h5: st.write("**Poids**")
            
            for essai in reversed(st.session_state.wordle_essais):
                if essai['gen'] == secret['gen']: gen_html = f"<div class='w-box w-green'>Gen {essai['gen']} ✅</div>"
                elif essai['gen'] < secret['gen']: gen_html = f"<div class='w-box w-red'>Gen {essai['gen']} 🔼</div>"
                else: gen_html = f"<div class='w-box w-red'>Gen {essai['gen']} 🔽</div>"

                sec_types = [secret['type1'], secret['type2']]
                if essai['type1'] == secret['type1']: t1_html = f"<div class='w-box w-green'>{essai['type1']}</div>"
                elif essai['type1'] in sec_types: t1_html = f"<div class='w-box w-yellow'>{essai['type1']}</div>"
                else: t1_html = f"<div class='w-box w-red'>{essai['type1']}</div>"
                
                if essai['type2'] == secret['type2']: t2_html = f"<div class='w-box w-green'>{essai['type2']}</div>"
                elif essai['type2'] in sec_types and essai['type2'] != "Aucun": t2_html = f"<div class='w-box w-yellow'>{essai['type2']}</div>"
                else: t2_html = f"<div class='w-box w-red'>{essai['type2']}</div>"

                if essai['taille'] == secret['taille']: taille_html = f"<div class='w-box w-green'>{essai['taille']}m ✅</div>"
                elif essai['taille'] < secret['taille']: taille_html = f"<div class='w-box w-red'>{essai['taille']}m 🔼</div>"
                else: taille_html = f"<div class='w-box w-red'>{essai['taille']}m 🔽</div>"

                if essai['poids'] == secret['poids']: poids_html = f"<div class='w-box w-green'>{essai['poids']}kg ✅</div>"
                elif essai['poids'] < secret['poids']: poids_html = f"<div class='w-box w-red'>{essai['poids']}kg 🔼</div>"
                else: poids_html = f"<div class='w-box w-red'>{essai['poids']}kg 🔽</div>"

                c1, c2, c3, c4, c5 = st.columns([2, 1, 2, 1.5, 1.5])
                with c1: st.markdown(f"<div style='display:flex; align-items:center; background-color: rgba(0,0,0,0.2); border-radius:10px; padding:5px;'><img src='{essai['image']}' width='50' style='margin-right:10px;'> <b>{essai['nom']}</b></div>", unsafe_allow_html=True)
                with c2: st.markdown(gen_html, unsafe_allow_html=True)
                with c3: st.markdown(t1_html + t2_html, unsafe_allow_html=True)
                with c4: st.markdown(taille_html, unsafe_allow_html=True)
                with c5: st.markdown(poids_html, unsafe_allow_html=True)

# ==========================================
# 🎒 MODE : BLIND STARTER (AUDIO)
# ==========================================
elif mode_choisi == "🎒 Blind Starter (Audio)":
    st.title("🎒 Choisissez votre Starter à l'aveugle !")
    st.write("Écoutez les 3 cris mystères et cliquez pour choisir votre compagnon de route.")

    if "starters_audio" not in st.session_state:
        starters_charges = []
        ids_aleatoires = random.sample(range(1, 1026), 3)
        for p_id in ids_aleatoires:
            try:
                data = requests.get(f"https://pokeapi.co/api/v2/pokemon/{p_id}").json()
                species = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{p_id}").json()
                nom_fr = next(entry["name"] for entry in species["names"] if entry["language"]["name"] == "fr")
                cry_url = data.get("cries", {}).get("latest", data.get("cries", {}).get("legacy", ""))
                image_url = data["sprites"]["front_default"]
            except:
                nom_fr = "Inconnu"; cry_url = ""; image_url = ""
            starters_charges.append({"nom": nom_fr, "cry": cry_url, "image": image_url})
        st.session_state.starters_audio = starters_charges
        st.session_state.choix_audio = None

    starters = st.session_state.starters_audio
    choix = st.session_state.choix_audio
    colonnes = st.columns(3)

    for i in range(3):
        with colonnes[i]:
            st.markdown(f"### Dossier {i+1}")
            if choix is None:
                st.info("🔴 Poké Ball ???")
                if starters[i]["cry"]: st.audio(starters[i]["cry"])
                if st.button(f"👉 Choisir le {i+1}", key=f"btn_aud_{i}", use_container_width=True):
                    st.session_state.choix_audio = i
                    st.rerun()
            else:
                if i == choix: st.success(f"🌟 VOTRE CHOIX\n\n**{starters[i]['nom']}**")
                else: st.error(f"❌ Non choisi\n\n{starters[i]['nom']}")
                st.image(starters[i]["image"], use_container_width=True)

    if choix is not None:
        st.divider(); st.balloons()
        st.header(f"Félicitations ! Vous partez avec **{starters[choix]['nom']}** ! 🎉")
        if st.button("Recommencer un tirage 🔄", type="primary"):
            del st.session_state.starters_audio
            st.session_state.choix_audio = None
            st.rerun()

# ==========================================
# 🔢 MODE : BLIND STARTER (POKÉDEX)
# ==========================================
elif mode_choisi == "🔢 Blind Starter (Pokédex)":
    st.title("🔢 Registre Pokédex")
    st.write("Faites appel à votre mémoire ! Choisissez un Pokémon uniquement à partir de son numéro d'identification national.")

    if "starters_dex" not in st.session_state:
        with st.spinner("Recherche dans les archives du Pokédex..."):
            starters_charges = []
            ids_aleatoires = random.sample(range(1, 1026), 3)
            for p_id in ids_aleatoires:
                try:
                    data = requests.get(f"https://pokeapi.co/api/v2/pokemon/{p_id}").json()
                    species = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{p_id}").json()
                    nom_fr = next(entry["name"] for entry in species["names"] if entry["language"]["name"] == "fr")
                    image_url = data["sprites"]["front_default"]
                except:
                    nom_fr = "Inconnu"; image_url = ""
                starters_charges.append({"nom": nom_fr, "image": image_url, "p_id": p_id})
            st.session_state.starters_dex = starters_charges
            st.session_state.choix_dex = None

    starters = st.session_state.starters_dex
    choix = st.session_state.choix_dex
    colonnes = st.columns(3)

    for i in range(3):
        with colonnes[i]:
            st.markdown(f"### Fiche {i+1}")
            if choix is None:
                num_formate = f"#{starters[i]['p_id']:03d}"
                st.info(f"📚 **Entrée Pokédex :**\n\n# {num_formate}")
                st.markdown("<div style='font-size: 60px; text-align: center; margin: 20px 0;'>📖</div>", unsafe_allow_html=True)
                if st.button(f"👉 Choisir le {i+1}", key=f"btn_dex_{i}", use_container_width=True, type="primary"):
                    st.session_state.choix_dex = i; st.rerun()
            else:
                if i == choix:
                    st.success(f"🌟 VOTRE CHOIX\n\n**{starters[i]['nom']}**")
                    st.markdown(f'<div style="text-align: center;"><img src="{starters[i]["image"]}" style="width: 150px;"></div>', unsafe_allow_html=True)
                else:
                    st.error(f"❌ Ignoré\n\n{starters[i]['nom']}")
                    st.markdown(f'<div style="text-align: center;"><img src="{starters[i]["image"]}" style="width: 100px; opacity: 0.5;"></div>', unsafe_allow_html=True)

    if choix is not None:
        st.divider(); st.balloons()
        st.header(f"Mémoire infaillible ! C'était bien **{starters[choix]['nom']}** ! 🎉")
        if st.button("Recommencer un tirage 🔄", type="primary"):
            del st.session_state.starters_dex
            st.session_state.choix_dex = None
            st.rerun()

# ==========================================
# 📊 MODE : BLIND STARTER (STATISTIQUES)
# ==========================================
elif mode_choisi == "📊 Blind Starter (Meilleure Stat)":
    st.title("📊 Analyseur de Potentiel")
    st.write("Choisissez votre futur champion en vous basant uniquement sur sa statistique de base la plus élevée !")

    if "starters_stat" not in st.session_state:
        with st.spinner("Calcul des potentiels de combat..."):
            starters_charges = []
            ids_aleatoires = random.sample(range(1, 1026), 3)
            for p_id in ids_aleatoires:
                try:
                    data = requests.get(f"https://pokeapi.co/api/v2/pokemon/{p_id}").json()
                    species = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{p_id}").json()
                    nom_fr = next(entry["name"] for entry in species["names"] if entry["language"]["name"] == "fr")
                    image_url = data["sprites"]["front_default"]
                    stats = data["stats"]
                    meilleure_stat = max(stats, key=lambda x: x["base_stat"])
                    nom_stat_fr = TRAD_STATS.get(meilleure_stat["stat"]["name"], meilleure_stat["stat"]["name"].capitalize())
                    valeur_stat = meilleure_stat["base_stat"]
                except:
                    nom_fr = "Inconnu"; image_url = ""; nom_stat_fr = "Inconnue"; valeur_stat = 0
                starters_charges.append({"nom": nom_fr, "image": image_url, "stat_name": nom_stat_fr, "stat_val": valeur_stat})
            st.session_state.starters_stat = starters_charges
            st.session_state.choix_stat = None

    starters = st.session_state.starters_stat
    choix = st.session_state.choix_stat
    colonnes = st.columns(3)

    for i in range(3):
        with colonnes[i]:
            st.markdown(f"### Combattant {i+1}")
            if choix is None:
                st.info(f"📈 **Meilleure Stat :**\n\n{starters[i]['stat_name']} ({starters[i]['stat_val']} BS)")
                st.markdown("<div style='font-size: 60px; text-align: center; margin: 20px 0;'>🥊</div>", unsafe_allow_html=True)
                if st.button(f"👉 Recruter le {i+1}", key=f"btn_stat_{i}", use_container_width=True, type="primary"):
                    st.session_state.choix_stat = i; st.rerun()
            else:
                if i == choix:
                    st.success(f"🌟 RECRUTÉ !\n\n**{starters[i]['nom']}**")
                    st.markdown(f'<div style="text-align: center;"><img src="{starters[i]["image"]}" style="width: 150px;"></div>', unsafe_allow_html=True)
                else:
                    st.error(f"❌ Recalé\n\n{starters[i]['nom']}")
                    st.markdown(f'<div style="text-align: center;"><img src="{starters[i]["image"]}" style="width: 100px; opacity: 0.5;"></div>', unsafe_allow_html=True)

    if choix is not None:
        st.divider(); st.balloons()
        st.header(f"Un choix tactique ! Vous partez avec **{starters[choix]['nom']}** ! 🎉")
        if st.button("Rechercher de nouveaux talents 🔄", type="primary"):
            del st.session_state.starters_stat
            st.session_state.choix_stat = None
            st.rerun()

# ==========================================
# 🥚 MODE : BLIND STARTER (INCUBATEUR)
# ==========================================
elif mode_choisi == "🥚 Blind Starter (Incubateur)":
    st.title("🥚 L'Incubateur Mystère")
    st.write("Bienvenue à la Pension Pokémon ! Choisissez un de ces 3 œufs en vous basant uniquement sur son (ou ses) groupe(s) d'œuf(s).")

    if "starters_oeuf" not in st.session_state:
        with st.spinner("Recherche d'œufs abandonnés à la pension..."):
            starters_charges = []
            ids_aleatoires = random.sample(range(1, 1026), 3)
            for p_id in ids_aleatoires:
                try:
                    data = requests.get(f"https://pokeapi.co/api/v2/pokemon/{p_id}").json()
                    species = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{p_id}").json()
                    nom_fr = next(entry["name"] for entry in species["names"] if entry["language"]["name"] == "fr")
                    groupes_anglais = [g["name"] for g in species.get("egg_groups", [])]
                    groupes_fr = " / ".join([TRAD_OEUFS.get(g, g.capitalize()) for g in groupes_anglais])
                    image_url = data["sprites"]["front_default"]
                except:
                    nom_fr = "Inconnu"; image_url = ""; groupes_fr = "Inconnu"
                starters_charges.append({"nom": nom_fr, "image": image_url, "oeufs": groupes_fr})
            st.session_state.starters_oeuf = starters_charges
            st.session_state.choix_oeuf = None

    starters = st.session_state.starters_oeuf
    choix = st.session_state.choix_oeuf
    colonnes = st.columns(3)

    for i in range(3):
        with colonnes[i]:
            st.markdown(f"### Incubateur {i+1}")
            if choix is None:
                st.info(f"🧬 **Groupe d'Œuf :**\n\n{starters[i]['oeufs']}")
                try:
                    img_oeuf = get_base64_image(os.path.join(DOSSIER_DU_JEU, "oeuf.png"))
                    egg_html = f'<img src="data:image/png;base64,{img_oeuf}" style="width: 120px; filter: drop-shadow(0px 5px 5px rgba(0,0,0,0.3));">'
                except:
                    egg_html = '<div style="font-size: 100px; text-align:center;">🥚</div>'
                st.markdown(f"<div class='egg-anim'>{egg_html}</div>", unsafe_allow_html=True)
                if st.button(f"🔥 Faire éclore le {i+1}", key=f"btn_oeuf_{i}", use_container_width=True, type="primary"):
                    st.session_state.choix_oeuf = i; st.rerun()
            else:
                if i == choix:
                    st.success(f"🌟 IL ÉCLOT !\n\n**{starters[i]['nom']}**")
                    st.markdown(f'<div style="text-align: center;"><img src="{starters[i]["image"]}" style="width: 150px;"></div>', unsafe_allow_html=True)
                else:
                    st.error(f"❌ Laissé à la pension\n\n{starters[i]['nom']}")
                    st.markdown(f'<div style="text-align: center;"><img src="{starters[i]["image"]}" style="width: 100px; opacity: 0.5;"></div>', unsafe_allow_html=True)

    if choix is not None:
        st.divider(); st.balloons()
        st.header(f"Oh ? Un **{starters[choix]['nom']}** sort de l'œuf ! 🎉")
        if st.button("Adopter un nouvel œuf 🔄", type="primary"):
            del st.session_state.starters_oeuf
            st.session_state.choix_oeuf = None
            st.rerun()

# ==========================================
# 🔎 MODE : BLIND STARTER (ZOOM)
# ==========================================
elif mode_choisi == "🔎 Blind Starter (Zoom)":
    st.title("🔎 Starter au Microscope")
    st.write("Observez ces fragments de sprites zoomés à l'extrême pour deviner quel Pokémon se cache derrière !")

    if "starters_zoom" not in st.session_state:
        with st.spinner("Zoom numérique en cours..."):
            starters_charges = []
            ids_aleatoires = random.sample(range(1, 1026), 3)
            for p_id in ids_aleatoires:
                try:
                    data = requests.get(f"https://pokeapi.co/api/v2/pokemon/{p_id}").json()
                    species = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{p_id}").json()
                    nom_fr = next(entry["name"] for entry in species["names"] if entry["language"]["name"] == "fr")
                    image_url = data["sprites"]["front_default"]
                except:
                    nom_fr = "Inconnu"; image_url = ""
                starters_charges.append({"nom": nom_fr, "image": image_url})
            st.session_state.starters_zoom = starters_charges
            st.session_state.choix_zoom = None

    starters = st.session_state.starters_zoom
    choix = st.session_state.choix_zoom
    colonnes = st.columns(3)

    for i in range(3):
        with colonnes[i]:
            st.markdown(f"### Échantillon {i+1}")
            if choix is None:
                st.markdown(f"""
                <div class="microscope-lens">
                    <img src="{starters[i]["image"]}" style="transform: scale(9.0); image-rendering: pixelated; width: 96px;">
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🔬 Sélectionner le {i+1}", key=f"btn_zoom_{i}", use_container_width=True, type="primary"):
                    st.session_state.choix_zoom = i; st.rerun()
            else:
                if i == choix:
                    st.success(f"🌟 VOTRE CHOIX\n\n**{starters[i]['nom']}**")
                    st.markdown(f'<div style="text-align: center;"><img src="{starters[i]["image"]}" style="width: 150px;"></div>', unsafe_allow_html=True)
                else:
                    st.error(f"❌ Écarté\n\n{starters[i]['nom']}")
                    st.markdown(f'<div style="text-align: center;"><img src="{starters[i]["image"]}" style="width: 100px; opacity: 0.5;"></div>', unsafe_allow_html=True)

    if choix is not None:
        st.divider(); st.balloons()
        st.header(f"Excellente observation ! C'est bien un **{starters[choix]['nom']}** ! 🎉")
        if st.button("Nouveaux échantillons 🔄", type="primary"):
            del st.session_state.starters_zoom
            st.session_state.choix_zoom = None
            st.rerun()

# ==========================================
# 🧬 MODE : BLIND STARTER (LABO SCANNERS)
# ==========================================
elif mode_choisi == "🧬 Blind Starter (Labo Scanners)":
    st.title("🔬 Fichiers isolés. Testez les scanners.")
    st.write("Le laboratoire a censuré les images. Utilisez les trois outils d'analyse ci-dessous pour identifier et choisir votre Pokémon.")

    if "starters_labo" not in st.session_state:
        with st.spinner("Analyse chromatique en cours..."):
            starters_charges = []
            ids_aleatoires = random.sample(range(1, 1026), 3)
            for p_id in ids_aleatoires:
                try:
                    data = requests.get(f"https://pokeapi.co/api/v2/pokemon/{p_id}").json()
                    species = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{p_id}").json()
                    nom_fr = next(entry["name"] for entry in species["names"] if entry["language"]["name"] == "fr")
                    image_url = data["sprites"]["front_default"]
                    adn_couleurs = extraire_adn_couleurs(image_url)
                except:
                    nom_fr = "Inconnu"; image_url = ""; adn_couleurs = ["#000"]*5
                starters_charges.append({"nom": nom_fr, "image": image_url, "adn": adn_couleurs})
            st.session_state.starters_labo = starters_charges
            st.session_state.choix_labo = None
            st.session_state.vues_labo = {0: "adn", 1: "adn", 2: "adn"}

    starters = st.session_state.starters_labo
    choix = st.session_state.choix_labo
    vues = st.session_state.vues_labo
    colonnes = st.columns(3)

    for i in range(3):
        with colonnes[i]:
            if choix is None:
                vue_actuelle = vues[i]
                if vue_actuelle == "adn":
                    c = starters[i]["adn"]
                    st.markdown(f"""<div class="adn-container"><div style="flex: 1; background-color: {c[0]};"></div><div style="flex: 1; background-color: {c[1]};"></div><div style="flex: 1; background-color: {c[2]};"></div><div style="flex: 1; background-color: {c[3]};"></div><div style="flex: 1; background-color: {c[4]};"></div></div><div class="lab-label" style="color: #ff4b4b;">ADN CHROMATIQUE</div>""", unsafe_allow_html=True)
                elif vue_actuelle == "mosaique":
                    st.markdown(f"""<div class="adn-container" style="background-color: #f0f2f6; display: flex; justify-content: center; align-items: center;"><img src="{starters[i]["image"]}" style="filter: blur(12px) contrast(1.5); width: 100px;"></div><div class="lab-label" style="color: #a855f7;">SCANNER MOSAÏQUE</div>""", unsafe_allow_html=True)
                elif vue_actuelle == "censure":
                    st.markdown(f"""<div class="adn-container" style="background-color: #f0f2f6; display: flex; justify-content: center; align-items: center;"><img src="{starters[i]["image"]}" style="filter: brightness(0); width: 100px;"></div><div class="lab-label" style="color: #38bdf8;">SILHOUETTE</div>""", unsafe_allow_html=True)

                if st.button("🧬 ADN Chromatique", key=f"btn_v_adn_{i}", use_container_width=True): st.session_state.vues_labo[i] = "adn"; st.rerun()
                if st.button("👾 Scanner Mosaïque", key=f"btn_v_mos_{i}", use_container_width=True): st.session_state.vues_labo[i] = "mosaique"; st.rerun()
                if st.button("👤 Silhouette", key=f"btn_v_cen_{i}", use_container_width=True): st.session_state.vues_labo[i] = "censure"; st.rerun()
                st.write("") 
                if st.button(f"🔴 Capturer le {i+1}", key=f"btn_choix_{i}", use_container_width=True, type="primary"): st.session_state.choix_labo = i; st.rerun()
            else:
                if i == choix:
                    st.success(f"🌟 SÉLECTION\n\n**{starters[i]['nom']}**")
                    st.markdown(f'<div style="text-align: center;"><img src="{starters[i]["image"]}" style="width: 150px;"></div>', unsafe_allow_html=True)
                else:
                    st.error(f"❌ Rejeté\n\n{starters[i]['nom']}")
                    st.markdown(f'<div style="text-align: center;"><img src="{starters[i]["image"]}" style="width: 100px; opacity: 0.5;"></div>', unsafe_allow_html=True)

    if choix is not None:
        st.divider(); st.balloons()
        st.header(f"Félicitations ! Vous partez à l'aventure avec **{starters[choix]['nom']}** ! 🎉")
        if st.button("Vider la machine et recommencer 🔄", type="primary"):
            del st.session_state.starters_labo
            st.session_state.choix_labo = None
            st.session_state.vues_labo = {0: "adn", 1: "adn", 2: "adn"}
            st.rerun()

# ==========================================
# 🕵️‍♂️ MODES : QUI EST-CE ? (POKEMON & SMASH BROS)
# ==========================================
elif mode_choisi == "🕵️‍♂️ Qui est-ce ? (Pokémon)":
    st.title("🕵️‍♂️ Le Plateau Qui est-ce ? (Pokémon)")
    st.write("Un Pokémon secret a été tiré au sort parmi les 9 générations. Éliminez les suspects et portez votre accusation !")
    
    if "pokemon_secret" not in st.session_state:
        with st.spinner("🔮 Invocation de 24 Pokémon aléatoires..."):
            ids_aleatoires = random.sample(range(1, 1026), 35)
            with ThreadPoolExecutor(max_workers=15) as executor: resultats = list(executor.map(charger_un_pokemon, ids_aleatoires))
            liste_24 = [p for p in resultats if p is not None][:24]
            st.session_state.pokemon_liste = liste_24
            st.session_state.pokemon_secret = random.choice(liste_24)
            st.session_state.pokemon_elimines = []
            st.session_state.pokemon_gagne = False

    secret_poke = st.session_state.pokemon_secret
    nom_secret = secret_poke["nom"] if secret_poke else "Inconnu"

    if st.session_state.pokemon_gagne:
        st.balloons(); st.success(f"🏆 BIEN JOUÉ ! Le Pokémon mystère était bien **{nom_secret}** !")
        if secret_poke: st.markdown(f'<div style="text-align: center;"><img src="{secret_poke["image"]}" style="width: 200px; filter: drop-shadow(0px 10px 15px rgba(16, 185, 129, 0.4));"></div>', unsafe_allow_html=True)
        st.write("")
        if st.button("Recommencer une partie Pokémon 🔄", type="primary"):
            del st.session_state.pokemon_secret; st.rerun()
    else:
        noms_pour_selection = ["-- Qui est-ce ? --"] + [p["nom"] for p in st.session_state.pokemon_liste]
        accusation_poke = st.selectbox("🎯 PORTER UNE ACCUSATION FINALE :", noms_pour_selection)
        if accusation_poke != "-- Qui est-ce ? --":
            if accusation_poke.lower() == nom_secret.lower(): st.session_state.pokemon_gagne = True; st.rerun()
            else: st.error(f"❌ Ce n'est pas {accusation_poke} !")
            
        st.divider()
        with st.expander("👀 Voir le secret"): st.write(f"Pokémon : **{nom_secret}**")
        cols = st.columns(4)
        for idx, p in enumerate(st.session_state.pokemon_liste):
            est_elimine = p["nom"] in st.session_state.pokemon_elimines
            with cols[idx % 4]:
                if est_elimine:
                    st.markdown(f"""<div class="game-card-eliminated"><img src="{p["image"]}" width="90"><p>{p["nom"]}</p></div>""", unsafe_allow_html=True)
                    if st.button("🔄 Annuler", key=f"ret_{idx}", use_container_width=True): st.session_state.pokemon_elimines.remove(p["nom"]); st.rerun()
                else:
                    st.markdown(f"""<div class="game-card"><img src="{p["image"]}" width="90"><p style="color: #ff4b4b; margin-bottom: 0;">{p["nom"]}</p></div>""", unsafe_allow_html=True)
                    if st.button("❌ Éliminer", key=f"elim_{idx}", use_container_width=True): st.session_state.pokemon_elimines.append(p["nom"]); st.rerun()

elif mode_choisi == "⚔️ Qui est-ce ? (Smash Bros)":
    st.title("⚔️ Le Plateau Qui est-ce ? (Smash Bros)")
    if os.path.exists(DOSSIER_PORTRAITS):
        tous_les_persos = [f for f in os.listdir(DOSSIER_PORTRAITS) if f.endswith(('.png', '.jpg'))]
        if "smash_secret" not in st.session_state:
            st.session_state.smash_liste = random.sample(tous_les_persos, min(len(tous_les_persos), 24))
            st.session_state.smash_secret = random.choice(st.session_state.smash_liste)
            st.session_state.smash_elimines = []
            st.session_state.smash_gagne = False

        nom_secret = os.path.splitext(st.session_state.smash_secret)[0]
        
        if st.session_state.smash_gagne:
            st.balloons(); st.success(f"🏆 BIEN JOUÉ ! Le personnage mystère était bien **{nom_secret}** !")
            img_encoded = get_base64_image(os.path.join(DOSSIER_PORTRAITS, st.session_state.smash_secret))
            st.markdown(f'<div style="text-align: center;"><img src="data:image/png;base64,{img_encoded}" style="width: 250px; filter: drop-shadow(0px 10px 15px rgba(56, 189, 248, 0.4));"></div>', unsafe_allow_html=True)
            st.write("")
            if st.button("Recommencer une partie Smash 🔄", type="primary", use_container_width=True):
                del st.session_state.smash_secret; del st.session_state.smash_liste; del st.session_state.smash_elimines
                st.session_state.smash_gagne = False; st.rerun()
        else:
            noms_pour_selection = ["-- Qui est-ce ? --"] + sorted([os.path.splitext(f)[0] for f in st.session_state.smash_liste])
            accusation = st.selectbox("🎯 PORTER UNE ACCUSATION FINALE :", noms_pour_selection, key="acc_smash")
            if accusation != "-- Qui est-ce ? --":
                if accusation.lower() == nom_secret.lower(): st.session_state.smash_gagne = True; st.rerun()
                else: st.error(f"❌ Ce n'est pas {accusation} ! Retentez votre chance.")
            st.divider(); st.subheader("📋 Votre plateau de jeu (24 personnages)")
            with st.expander("👀 Voir le secret"): st.write(f"Personnage : **{nom_secret}**")
            cols = st.columns(4)
            for idx, fichier in enumerate(st.session_state.smash_liste):
                nom_perso = os.path.splitext(fichier)[0]
                img_encoded = get_base64_image(os.path.join(DOSSIER_PORTRAITS, fichier))
                est_elimine = fichier in st.session_state.smash_elimines
                with cols[idx % 4]:
                    if est_elimine:
                        st.markdown(f"""<div class="game-card-eliminated"><img src="data:image/png;base64,{img_encoded}" style="width: 90px; border-radius: 5px; margin-bottom: 5px;"><p style="margin: 0; font-size: 13px; font-weight: bold; text-decoration: line-through;">{nom_perso}</p></div>""", unsafe_allow_html=True)
                        if st.button("🔄", key=f"ret_smash_{idx}", use_container_width=True): st.session_state.smash_elimines.remove(fichier); st.rerun()
                    else:
                        st.markdown(f"""<div class="game-card game-card-smash"><img src="data:image/png;base64,{img_encoded}" style="width: 90px; border-radius: 5px; margin-bottom: 5px; filter: drop-shadow(0px 5px 5px rgba(0,0,0,0.3));"><p style="margin: 0; font-size: 13px; font-weight: bold; color: #38bdf8;">{nom_perso}</p></div>""", unsafe_allow_html=True)
                        if st.button("❌ Éliminer", key=f"elim_smash_{idx}", use_container_width=True): st.session_state.smash_elimines.append(fichier); st.rerun()
    else:
        st.warning("Dossier portraits introuvable.")

# ==========================================
# 🧝‍♂️ MODE : QUI EST-CE ? (ZELDA)
# ==========================================
elif mode_choisi == "🧝‍♂️ Qui est-ce ? (Zelda)":
    st.title("🧝‍♂️ Le Plateau Qui est-ce ? (Zelda)")
    tous_les_persos_zelda = list(ZELDA_DATA.keys()) if isinstance(ZELDA_DATA, dict) else []
    
    if "zelda_qe_secret" not in st.session_state:
        st.session_state.zelda_qe_liste = random.sample(tous_les_persos_zelda, min(len(tous_les_persos_zelda), 24))
        st.session_state.zelda_qe_secret = random.choice(st.session_state.zelda_qe_liste)
        st.session_state.zelda_qe_elimines = []
        st.session_state.zelda_qe_gagne = False

    nom_secret = st.session_state.zelda_qe_secret
    if st.session_state.zelda_qe_gagne:
        st.balloons(); st.success(f"🏆 BIEN JOUÉ ! L'entité mystère était bien **{nom_secret}** !")
        img_html = get_zelda_image(nom_secret, size=250, center=True)
        st.markdown(f'<div>{img_html}</div>', unsafe_allow_html=True)
        st.write("")
        if st.button("Recommencer une partie Zelda 🔄", type="primary"): del st.session_state.zelda_qe_secret; st.rerun()
    else:
        noms_pour_selection = ["-- Qui est-ce ? --"] + sorted(st.session_state.zelda_qe_liste)
        accusation = st.selectbox("🎯 PORTER UNE ACCUSATION FINALE :", noms_pour_selection)
        if accusation != "-- Qui est-ce ? --":
            if accusation.lower() == nom_secret.lower(): st.session_state.zelda_qe_gagne = True; st.rerun()
            else: st.error(f"❌ Ce n'est pas {accusation} !")
            
        st.divider()
        with st.expander("👀 Voir le secret"): st.write(f"Personnage : **{nom_secret}**")
        cols = st.columns(4)
        for idx, nom_perso in enumerate(st.session_state.zelda_qe_liste):
            img_html = get_zelda_image(nom_perso, size=100, center=True)
            est_elimine = nom_perso in st.session_state.zelda_qe_elimines
            with cols[idx % 4]:
                if est_elimine:
                    st.markdown(f"<div class='game-card-eliminated'>{img_html}<p style='text-decoration: line-through;'>{nom_perso}</p></div>", unsafe_allow_html=True)
                    if st.button("🔄 Annuler", key=f"rz_{idx}", use_container_width=True): st.session_state.zelda_qe_elimines.remove(nom_perso); st.rerun()
                else:
                    st.markdown(f"<div class='game-card game-card-zelda'>{img_html}<p style='color: #facc15; margin-bottom: 0;'>{nom_perso}</p></div>", unsafe_allow_html=True)
                    if st.button("❌ Éliminer", key=f"ez_{idx}", use_container_width=True): st.session_state.zelda_qe_elimines.append(nom_perso); st.rerun()

# ==========================================
# 🪲 MODE : QUI EST-CE ? (HOLLOW KNIGHT)
# ==========================================
elif mode_choisi == "🪲 Qui est-ce ? (Hollow Knight)":
    st.title("🪲 Le Plateau Qui est-ce ? (Hollow Knight)")
    st.write("Un insecte d'Hallownest ou de Pharloom a été tiré au sort. Éliminez les suspects et portez votre accusation !")

    if not os.path.exists(DOSSIER_PORTRAITS_HK):
        st.info("💡 Astuce : Créez un dossier 'portraits_hk' contenant les images de vos personnages pour remplacer les avatars !")

    if isinstance(HOLLOW_KNIGHT_PERSOS, dict):
        tous_les_hk = list(HOLLOW_KNIGHT_PERSOS.keys())
    elif isinstance(HOLLOW_KNIGHT_PERSOS, list):
        st.warning("⚠️ Attention: Votre fichier hk_data.json est toujours détecté comme une liste et non un dictionnaire. Les raretés ne seront pas disponibles.")
        tous_les_hk = HOLLOW_KNIGHT_PERSOS
    else:
        tous_les_hk = ["Le Chevalier", "Hornet"]
        
    if "hk_qe_secret" not in st.session_state:
        taille_grille = min(len(tous_les_hk), 24)
        st.session_state.hk_qe_liste = random.sample(tous_les_hk, taille_grille)
        st.session_state.hk_qe_secret = random.choice(st.session_state.hk_qe_liste)
        st.session_state.hk_qe_elimines = []
        st.session_state.hk_qe_gagne = False

    nom_secret = st.session_state.hk_qe_secret

    if st.session_state.hk_qe_gagne:
        st.balloons(); st.success(f"🏆 BIEN JOUÉ ! L'insecte mystère était bien **{nom_secret}** !")
        img_html = get_hk_image(nom_secret, size=250, center=True)
        st.markdown(f'<div>{img_html}</div>', unsafe_allow_html=True)
        st.write("")
        if st.button("Recommencer une partie Hollow Knight 🔄", type="primary", use_container_width=True):
            del st.session_state.hk_qe_secret; del st.session_state.hk_qe_liste; del st.session_state.hk_qe_elimines
            st.session_state.hk_qe_gagne = False; st.rerun()
    else:
        noms_pour_selection = ["-- Qui est-ce ? --"] + sorted(st.session_state.hk_qe_liste)
        accusation = st.selectbox("🎯 PORTER UNE ACCUSATION FINALE :", noms_pour_selection, key="acc_hk")
        if accusation != "-- Qui est-ce ? --":
            if accusation.lower() == nom_secret.lower(): st.session_state.hk_qe_gagne = True; st.rerun()
            else: st.error(f"❌ Ce n'est pas {accusation} ! Retentez votre chance.")
        st.divider(); st.subheader("📋 Votre plateau de jeu (24 suspects)")
        with st.expander("👀 Voir le secret"): st.write(f"Personnage : **{nom_secret}**")
        cols = st.columns(4)
        for idx, nom_perso in enumerate(st.session_state.hk_qe_liste):
            img_html = get_hk_image(nom_perso, size=100, center=True)
            est_elimine = nom_perso in st.session_state.hk_qe_elimines
            with cols[idx % 4]:
                if est_elimine:
                    st.markdown(f"""<div class="game-card-eliminated">{img_html}<p style="margin: 0; font-size: 14px; font-weight: bold; text-decoration: line-through;">{nom_perso}</p></div>""", unsafe_allow_html=True)
                    if st.button("🔄", key=f"ret_hk_{idx}", use_container_width=True): st.session_state.hk_qe_elimines.remove(nom_perso); st.rerun()
                else:
                    st.markdown(f"""<div class="game-card game-card-hk">{img_html}<p style="margin: 0; font-size: 14px; font-weight: bold; color: #94a3b8;">{nom_perso}</p></div>""", unsafe_allow_html=True)
                    if st.button("❌ Éliminer", key=f"elim_hk_{idx}", use_container_width=True): st.session_state.hk_qe_elimines.append(nom_perso); st.rerun()