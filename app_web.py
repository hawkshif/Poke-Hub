import streamlit as st
import requests
import random
import os
import base64
from io import BytesIO
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import urllib.parse

# Configuration de la page
st.set_page_config(page_title="Poké-Hub Web", page_icon="🎮", layout="wide")

# ==========================================
# 🎨 INJECTION DU DESIGN CSS "NEXT-GEN"
# ==========================================
st.markdown("""
<style>
    /* Masquer les éléments par défaut de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Fond global du site - Dégradé radial nuit/arcade */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e293b 0%, #020617 100%) !important;
        color: #f8fafc;
    }

    /* Animation de l'oeuf */
    @keyframes pulse-egg {
        0% { transform: scale(1) translateY(0px); }
        50% { transform: scale(1.05) translateY(-5px); }
        100% { transform: scale(1) translateY(0px); }
    }
    .egg-anim {
        text-align: center; 
        margin: 15px 0;
        animation: pulse-egg 2.5s infinite ease-in-out;
        filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.4));
    }

    /* Cartes de jeu avec effet Glassmorphism (Verre) */
    .game-card {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        text-align: center;
        margin-bottom: 15px;
    }
    
    /* Effets de survol Néon par univers */
    .game-card:hover {
        transform: translateY(-7px) scale(1.02);
        border-color: rgba(255, 75, 75, 0.8);
        box-shadow: 0 10px 25px rgba(255, 75, 75, 0.4);
    }
    .game-card-smash:hover {
        border-color: rgba(56, 189, 248, 0.8);
        box-shadow: 0 10px 25px rgba(56, 189, 248, 0.4);
    }
    .game-card-zelda:hover {
        border-color: rgba(250, 204, 21, 0.8); 
        box-shadow: 0 10px 25px rgba(250, 204, 21, 0.4);
    }

    /* Cartes éliminées */
    .game-card-eliminated {
        background: rgba(15, 23, 42, 0.4);
        border-radius: 16px;
        padding: 15px;
        text-align: center;
        opacity: 0.25;
        filter: grayscale(100%) contrast(1.2);
        margin-bottom: 15px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
    }
    
    /* Style des boutons personnalisés */
    div.stButton > button {
        border-radius: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover {
        transform: scale(1.03);
        box-shadow: 0px 5px 20px rgba(255, 255, 255, 0.15);
    }
    
    /* Microscope */
    .microscope-lens {
        width: 140px; height: 140px; 
        overflow: hidden; 
        margin: 0 auto 20px auto; 
        border: 6px solid #334155; 
        border-radius: 50%; 
        display: flex; align-items: center; justify-content: center; 
        background-color: #0f172a; 
        box-shadow: inset 0px 0px 20px rgba(0,0,0,0.9), 0px 10px 20px rgba(0,0,0,0.5);
    }
    
    /* ADN Scanners */
    .adn-container {
        display: flex; height: 130px; width: 100%; 
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px 12px 0 0;
        overflow: hidden;
        box-shadow: inset 0px 5px 15px rgba(0,0,0,0.6);
    }
    .lab-label {
        background-color: rgba(15, 23, 42, 0.8); 
        text-align: center; font-weight: bold; font-size: 13px; 
        padding: 8px; font-family: 'Courier New', Courier, monospace; 
        border: 1px solid rgba(255,255,255,0.1); border-top: none; 
        border-radius: 0 0 12px 12px; margin-bottom: 15px;
        letter-spacing: 2px;
    }

    /* Grille Wordle */
    .w-box {
        padding: 10px; border-radius: 8px; text-align: center;
        font-weight: 700; color: white; margin-bottom: 6px; font-size: 14px;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.6);
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .w-green { background: linear-gradient(135deg, #16a34a, #22c55e); border: 1px solid #15803d; }
    .w-yellow { background: linear-gradient(135deg, #ca8a04, #eab308); border: 1px solid #a16207; }
    .w-red { background: linear-gradient(135deg, #dc2626, #ef4444); border: 1px solid #b91c1c; }
</style>
""", unsafe_allow_html=True)

# --- AUTO-DÉTECTION DES DOSSIERS ---
DOSSIER_DU_JEU = os.path.dirname(os.path.abspath(__file__))
DOSSIER_PORTRAITS = os.path.join(DOSSIER_DU_JEU, "portraits")
DOSSIER_PORTRAITS_ZELDA = os.path.join(DOSSIER_DU_JEU, "portraits_zelda")

# --- BASE DE DONNÉES ZELDA ---
ZELDA_DATA = {
    "Link": {"race": "Hylien", "role": "Héros", "jeu": "The Legend of Zelda", "annee": 1986},
    "Zelda": {"race": "Hylien", "role": "Alliée", "jeu": "The Legend of Zelda", "annee": 1986},
    "Ganon": {"race": "Démon", "role": "Boss", "jeu": "The Legend of Zelda", "annee": 1986},
    "Impa": {"race": "Sheikah", "role": "Alliée", "jeu": "The Legend of Zelda", "annee": 1986},
    "Le Vieil Homme": {"race": "Hylien", "role": "Allié", "jeu": "The Legend of Zelda", "annee": 1986},
    "Moblin": {"race": "Monstre", "role": "Ennemi", "jeu": "The Legend of Zelda", "annee": 1986},
    "Octorok": {"race": "Monstre", "role": "Ennemi", "jeu": "The Legend of Zelda", "annee": 1986},
    "Lynel": {"race": "Monstre", "role": "Ennemi", "jeu": "The Legend of Zelda", "annee": 1986},
    "Gohma": {"race": "Monstre", "role": "Boss", "jeu": "The Legend of Zelda", "annee": 1986},
    "Gleeok": {"race": "Monstre", "role": "Boss", "jeu": "The Legend of Zelda", "annee": 1986},
    "Like Like": {"race": "Monstre", "role": "Ennemi", "jeu": "The Legend of Zelda", "annee": 1986},
    "Dark Link": {"race": "Ombre", "role": "Boss", "jeu": "The Adventure of Link", "annee": 1987},
    "Lézalfos": {"race": "Monstre", "role": "Ennemi", "jeu": "The Adventure of Link", "annee": 1987},
    "Aghanim": {"race": "Sorcier", "role": "Boss", "jeu": "A Link to the Past", "annee": 1991},
    "Hinox": {"race": "Monstre", "role": "Ennemi", "jeu": "A Link to the Past", "annee": 1991},
    "Sahasrahla": {"race": "Hylien", "role": "Allié", "jeu": "A Link to the Past", "annee": 1991},
    "Poule (Cocotte)": {"race": "Animal", "role": "Neutre", "jeu": "A Link to the Past", "annee": 1991},
    "Marine": {"race": "Humaine", "role": "Alliée", "jeu": "Link's Awakening", "annee": 1993},
    "Poisson-Rêve": {"race": "Divinité", "role": "Neutre", "jeu": "Link's Awakening", "annee": 1993},
    "Ganondorf": {"race": "Gerudo", "role": "Boss", "jeu": "Ocarina of Time", "annee": 1998},
    "Navi": {"race": "Fée", "role": "Alliée", "jeu": "Ocarina of Time", "annee": 1998},
    "Epona": {"race": "Animal", "role": "Alliée", "jeu": "Ocarina of Time", "annee": 1998},
    "Skull Kid": {"race": "Stalfos", "role": "Antagoniste", "jeu": "Ocarina of Time", "annee": 1998},
    "Volcania": {"race": "Dragon", "role": "Boss", "jeu": "Ocarina of Time", "annee": 1998},
    "Saria": {"race": "Kokiri", "role": "Alliée", "jeu": "Ocarina of Time", "annee": 1998},
    "Darunia": {"race": "Goron", "role": "Allié", "jeu": "Ocarina of Time", "annee": 1998},
    "Ruto": {"race": "Zora", "role": "Alliée", "jeu": "Ocarina of Time", "annee": 1998},
    "Nabooru": {"race": "Gerudo", "role": "Alliée", "jeu": "Ocarina of Time", "annee": 1998},
    "Sheik": {"race": "Sheikah", "role": "Allié", "jeu": "Ocarina of Time", "annee": 1998},
    "Malon": {"race": "Hylien", "role": "Alliée", "jeu": "Ocarina of Time", "annee": 1998},
    "Kaepora Gaebora": {"race": "Animal", "role": "Allié", "jeu": "Ocarina of Time", "annee": 1998},
    "Twinrova": {"race": "Gerudo", "role": "Boss", "jeu": "Ocarina of Time", "annee": 1998},
    "Effroi": {"race": "Monstre", "role": "Ennemi", "jeu": "Ocarina of Time", "annee": 1998},
    "Tingle": {"race": "Hylien", "role": "Neutre", "jeu": "Majora's Mask", "annee": 2000},
    "Chuchu": {"race": "Monstre", "role": "Ennemi", "jeu": "Majora's Mask", "annee": 2000},
    "Le Vendeur de Masques": {"race": "Hylien", "role": "Neutre", "jeu": "Majora's Mask", "annee": 2000},
    "Taya": {"race": "Fée", "role": "Alliée", "jeu": "Majora's Mask", "annee": 2000},
    "Bokoblin": {"race": "Monstre", "role": "Ennemi", "jeu": "The Wind Waker", "annee": 2002},
    "Lion Rouge": {"race": "Bateau", "role": "Allié", "jeu": "The Wind Waker", "annee": 2002},
    "Dumoria": {"race": "Korogu", "role": "Allié", "jeu": "The Wind Waker", "annee": 2002},
    "Médolie": {"race": "Piaf", "role": "Alliée", "jeu": "The Wind Waker", "annee": 2002},
    "Tetra": {"race": "Hylien", "role": "Alliée", "jeu": "The Wind Waker", "annee": 2002},
    "Terry": {"race": "Hylien", "role": "Neutre", "jeu": "The Wind Waker", "annee": 2002},
    "Valoo": {"race": "Dragon", "role": "Allié", "jeu": "The Wind Waker", "annee": 2002},
    "Vaati": {"race": "Minish", "role": "Boss", "jeu": "The Minish Cap", "annee": 2004},
    "Exelo": {"race": "Minish", "role": "Allié", "jeu": "The Minish Cap", "annee": 2004},
    "Midona": {"race": "Twili", "role": "Alliée", "jeu": "Twilight Princess", "annee": 2006},
    "Xanto": {"race": "Twili", "role": "Boss", "jeu": "Twilight Princess", "annee": 2006},
    "Iria": {"race": "Hylien", "role": "Alliée", "jeu": "Twilight Princess", "annee": 2006},
    "Machaon": {"race": "Hylien", "role": "Neutre", "jeu": "Twilight Princess", "annee": 2006},
    "Link Loup": {"race": "Animal", "role": "Héros", "jeu": "Twilight Princess", "annee": 2006},
    "Ghirahim": {"race": "Démon", "role": "Boss", "jeu": "Skyward Sword", "annee": 2011},
    "Fay": {"race": "Esprit", "role": "Alliée", "jeu": "Skyward Sword", "annee": 2011},
    "Le Banni": {"race": "Démon", "role": "Boss", "jeu": "Skyward Sword", "annee": 2011},
    "Hergo": {"race": "Hylien", "role": "Allié", "jeu": "Skyward Sword", "annee": 2011},
    "Narisha": {"race": "Divinité", "role": "Allié", "jeu": "Skyward Sword", "annee": 2011},
    "Mipha": {"race": "Zora", "role": "Alliée", "jeu": "Breath of the Wild", "annee": 2017},
    "Daruk": {"race": "Goron", "role": "Allié", "jeu": "Breath of the Wild", "annee": 2017},
    "Revali": {"race": "Piaf", "role": "Allié", "jeu": "Breath of the Wild", "annee": 2017},
    "Urbosa": {"race": "Gerudo", "role": "Alliée", "jeu": "Breath of the Wild", "annee": 2017},
    "Sidon": {"race": "Zora", "role": "Allié", "jeu": "Breath of the Wild", "annee": 2017},
    "Riju": {"race": "Gerudo", "role": "Alliée", "jeu": "Breath of the Wild", "annee": 2017},
    "Yunobo": {"race": "Goron", "role": "Allié", "jeu": "Breath of the Wild", "annee": 2017},
    "Gardien": {"race": "Machine", "role": "Ennemi", "jeu": "Breath of the Wild", "annee": 2017},
    "Pru'ha": {"race": "Sheikah", "role": "Alliée", "jeu": "Breath of the Wild", "annee": 2017},
    "Noïa": {"race": "Korogu", "role": "Neutre", "jeu": "Breath of the Wild", "annee": 2017},
    "Le Grand Kohga": {"race": "Sheikah", "role": "Boss", "jeu": "Breath of the Wild", "annee": 2017},
    "Asarim": {"race": "Piaf", "role": "Neutre", "jeu": "Breath of the Wild", "annee": 2017},
    "Faras": {"race": "Sheikah", "role": "Allié", "jeu": "Breath of the Wild", "annee": 2017},
    "Kilton": {"race": "Monstre", "role": "Neutre", "jeu": "Breath of the Wild", "annee": 2017},
    "Teba": {"race": "Piaf", "role": "Allié", "jeu": "Breath of the Wild", "annee": 2017},
    "Rordrac": {"race": "Dragon", "role": "Neutre", "jeu": "Breath of the Wild", "annee": 2017},
    "Ordrac": {"race": "Dragon", "role": "Neutre", "jeu": "Breath of the Wild", "annee": 2017},
    "Nedrac": {"race": "Dragon", "role": "Neutre", "jeu": "Breath of the Wild", "annee": 2017},
    "Babil": {"race": "Piaf", "role": "Allié", "jeu": "Tears of the Kingdom", "annee": 2023},
    "Rauru": {"race": "Soneau", "role": "Allié", "jeu": "Tears of the Kingdom", "annee": 2023},
    "Mineru": {"race": "Soneau", "role": "Alliée", "jeu": "Tears of the Kingdom", "annee": 2023},
    "Terrako": {"race": "Machine", "role": "Allié", "jeu": "Hyrule Warriors : L'Ère du Fléau", "annee": 2020},
    "Daphnès Nohansen Hyrule": {"race": "Hylien", "role": "Allié", "jeu": "The Wind Waker", "annee": 2002},
    "Linebeck": {"race": "Hylien", "role": "Allié", "jeu": "Phantom Hourglass", "annee": 2007},
    "Bellum": {"race": "Démon", "role": "Boss", "jeu": "Phantom Hourglass", "annee": 2007},
    "Traucmahr": {"race": "Locomo", "role": "Antagoniste", "jeu": "Spirit Tracks", "annee": 2009},
    "Yuga": {"race": "Loruléen", "role": "Boss", "jeu": "A Link Between Worlds", "annee": 2013},
    "Lavio": {"race": "Loruléen", "role": "Allié", "jeu": "A Link Between Worlds", "annee": 2013},
    "Princesse Hilda": {"race": "Loruléen", "role": "Alliée", "jeu": "A Link Between Worlds", "annee": 2013},
    "Igor": {"race": "Hylien", "role": "Neutre", "jeu": "Ocarina of Time", "annee": 1998},
    "Arbre Mojo": {"race": "Divinité", "role": "Allié", "jeu": "Ocarina of Time", "annee": 1998},
    "Jabu-Jabu": {"race": "Divinité", "role": "Neutre", "jeu": "Ocarina of Time", "annee": 1998},
    "Roi Dorefah": {"race": "Zora", "role": "Allié", "jeu": "Breath of the Wild", "annee": 2017},
    "Pahya": {"race": "Sheikah", "role": "Alliée", "jeu": "Breath of the Wild", "annee": 2017},
    "Patricia": {"race": "Animal", "role": "Neutre", "jeu": "Breath of the Wild", "annee": 2017},
    "Ombre de l'Eau de Ganon": {"race": "Démon", "role": "Boss", "jeu": "Breath of the Wild", "annee": 2017},
    "Sonia": {"race": "Hylien", "role": "Alliée", "jeu": "Tears of the Kingdom", "annee": 2023},
    "Josha": {"race": "Sheikah", "role": "Alliée", "jeu": "Tears of the Kingdom", "annee": 2023},
    "Tauro": {"race": "Hylien", "role": "Allié", "jeu": "Tears of the Kingdom", "annee": 2023},
    "Golemax": {"race": "Machine", "role": "Boss", "jeu": "Tears of the Kingdom", "annee": 2023},
    "Roi Gleeok": {"race": "Monstre", "role": "Boss", "jeu": "Tears of the Kingdom", "annee": 2023},
    "Tael": {"race": "Fée", "role": "Allié", "jeu": "Majora's Mask", "annee": 2000},
    "Linkle": {"race": "Hylien", "role": "Alliée", "jeu": "Hyrule Warriors", "annee": 2014},
    "Anju": {"race": "Hylien", "role": "Neutre", "jeu": "Majora's Mask", "annee": 2000},
    "Kafei": {"race": "Hylien", "role": "Neutre", "jeu": "Majora's Mask", "annee": 2000},
    "Cremia": {"race": "Hylien", "role": "Neutre", "jeu": "Majora's Mask", "annee": 2000},
    "Romani": {"race": "Hylien", "role": "Neutre", "jeu": "Majora's Mask", "annee": 2000}
}

# --- DICTIONNAIRES POKÉMON ---
TRAD_OEUFS = {
    "monster": "🦖 Monstre", "water1": "💧 Eau 1", "bug": "🐛 Insectoïde",
    "flying": "🌪️ Aérien", "ground": "🐾 Terrestre", "fairy": "✨ Féérique",
    "plant": "🌿 Végétal", "humanshape": "👤 Humanoïde", "water3": "🦑 Eau 3",
    "mineral": "🪨 Minéral", "indeterminate": "👻 Amorphe", "water2": "🐟 Eau 2",
    "ditto": "🟣 Métamorph", "dragon": "🐲 Draconique", "no-eggs": "🚫 Aucun"
}
TRAD_STATS = {
    "hp": "❤️ PV", "attack": "⚔️ Attaque", "defense": "🛡️ Défense",
    "special-attack": "🔮 Att. Spé", "special-defense": "🔰 Déf. Spé", "speed": "⚡ Vitesse"
}
TRAD_TYPES = {
    "normal": "Normal", "fire": "Feu", "water": "Eau", "electric": "Électrik", 
    "grass": "Plante", "ice": "Glace", "fighting": "Combat", "poison": "Poison", 
    "ground": "Sol", "flying": "Vol", "psychic": "Psy", "bug": "Insecte",
    "rock": "Roche", "ghost": "Spectre", "dragon": "Dragon", "dark": "Ténèbres", 
    "steel": "Acier", "fairy": "Fée"
}
GEN_RANGES = {
    "1G (Kanto)": (1, 151), "2G (Johto)": (152, 251), "3G (Hoenn)": (252, 386),
    "4G (Sinnoh)": (387, 493), "5G (Unys)": (494, 649), "6G (Kalos)": (650, 721),
    "7G (Alola)": (722, 809), "8G (Galar)": (810, 905), "9G (Paldea)": (906, 1025)
}

# --- FONCTIONS TECHNIQUES ---
def get_base64_image(img_path):
    with open(img_path, "rb") as file:
        data = file.read()
    return base64.b64encode(data).decode()

def get_zelda_image(nom, size=60, center=False):
    margin_style = "margin: 0 auto 5px auto; display: block;" if center else "margin-right: 12px;"
    if os.path.exists(DOSSIER_PORTRAITS_ZELDA):
        for ext in ['.png', '.jpg', '.jpeg', '.webp']:
            chemin_img = os.path.join(DOSSIER_PORTRAITS_ZELDA, f"{nom}{ext}")
            if os.path.exists(chemin_img):
                img_base64 = get_base64_image(chemin_img)
                return f"<img src='data:image/{ext[1:]};base64,{img_base64}' style='width:{size}px; height:{size}px; object-fit:contain; background-color:rgba(15, 23, 42, 0.8); border-radius:50%; border:2px solid #38bdf8; padding:4px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); {margin_style}'>"
    nom_u = urllib.parse.quote(nom)
    avatar = f"https://ui-avatars.com/api/?name={nom_u}&background=0f172a&color=38bdf8&rounded=true&bold=true&size={size}"
    return f"<img src='{avatar}' style='width:{size}px; border-radius:50%; border:2px solid #38bdf8; box-shadow: 0 4px 10px rgba(0,0,0,0.5); {margin_style}'>"

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
        return {
            "id": p_id, "nom": nom_fr, "image": data["sprites"]["front_default"],
            "gen": gen_dict.get(gen_name, 1), "type1": type1, "type2": type2,
            "taille": data["height"] / 10, "poids": data["weight"] / 10
        }
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

# 1. BARRE LATÉRALE DE NAVIGATION (RÉORGANISÉE)
st.sidebar.markdown("## 🔴 Poké-Hub Web")
st.sidebar.markdown("---")
mode_choisi = st.sidebar.radio(
    "🕹️ SÉLECTION DU MODE",
    [
        "🏠 Accueil", 
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
        "🧝‍♂️ Qui est-ce ? (Zelda)" 
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
        st.info("**👁️ Détecteur Sheikah (Zelda)**\n\nIdentifie le personnage ou monstre culte de la saga Zelda !")
        st.info("**🟩 Poké-Wordle**\n\nDéduis le Pokémon secret grâce aux indices de Génération, Types, Taille et Poids.")
        st.success("**🕵️‍♂️ 3x Modes Qui est-ce ?**\n\nUn véritable jeu de société interactif avec des grilles aléatoires sur Zelda, Pokémon et Smash Bros.")
    with col2:
        st.warning("**🎒 Les 6 Modes Blind Starter**\n\nDevine ton compagnon de route avec différentes mécaniques :\n* **Audio :** Reconnais son cri\n* **Pokédex :** À l'aide de son numéro national\n* **Statistiques :** Via sa meilleure stat de base\n* **Incubateur :** Selon son groupe d'œuf\n* **Zoom :** Son sprite grossi 9 fois\n* **Labo Scanners :** Analyse son ADN et sa silhouette")

# ==========================================
# 👁️ MODE : DÉTECTEUR SHEIKAH (ZELDA WORDLE)
# ==========================================
elif mode_choisi == "👁️ Détecteur Sheikah (Zelda Wordle)":
    st.title("👁️ Détecteur Sheikah : Archive d'Hyrule")
    st.write("Déduisez l'identité secrète de l'archive (Personnages et Monstres) issue de la chronologie complète de Zelda !")
    st.caption("Flèches : 🔼 La première apparition du secret est plus RÉCENTE | 🔽 Le secret est plus ANCIEN.")
    
    if not os.path.exists(DOSSIER_PORTRAITS_ZELDA):
        st.info("💡 Astuce : Créez un dossier 'portraits_zelda' contenant les images de vos personnages (ex: 'Saria.png', 'Ganon.jpg') pour remplacer les avatars !")

    if "z_secret_name" not in st.session_state:
        st.session_state.z_secret_name = random.choice(list(ZELDA_DATA.keys()))
        st.session_state.z_essais = []
        st.session_state.z_gagne = False
        
    secret_item = ZELDA_DATA[st.session_state.z_secret_name]
    
    if not st.session_state.z_gagne:
        c_in, c_bt = st.columns([3, 1])
        with c_in:
            guess_z = st.selectbox("Sélectionnez un personnage ou monstre :", ["-- Analyse requise --"] + sorted(list(ZELDA_DATA.keys())))
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

        # SYSTÈME D'INDICES PROGRESSIFS
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
            
            if essai['role'] == secret_item['role']: role_html = f"<div class='w-box w-green'>{essai['role']}</div>"
            else: role_html = f"<div class='w-box w-red'>{essai['role']}</div>"
            
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
    st.caption("Couleurs : 🟩 = Parfait | 🟨 = Mauvaise position (Type) | 🟥 = Incorrect. Flèches : 🔼 Le secret est plus grand/lourd | 🔽 Le secret est plus petit/léger.")

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
                    else:
                        st.error("Veuillez choisir un Pokémon dans la liste !")

            # SYSTÈME D'INDICES PROGRESSIFS
            with st.expander("💡 Besoin d'un indice ?"):
                if len(st.session_state.wordle_essais) >= 5:
                    st.write(f"La première lettre du Pokémon est : **{secret['nom'][0].upper()}**")
                    st.write(f"La dernière lettre est : **{secret['nom'][-1].upper()}**")
                elif len(st.session_state.wordle_essais) >= 3:
                    st.write(f"La première lettre du Pokémon est : **{secret['nom'][0].upper()}**")
                    st.write("*(Faites 5 essais pour débloquer le prochain indice)*")
                else:
                    st.write("Faites au moins 3 essais pour débloquer le premier indice !")

        if st.session_state.wordle_gagne:
            st.balloons()
            st.success(f"🏆 INCROYABLE ! Vous avez trouvé **{secret['nom']}** en {len(st.session_state.wordle_essais)} essai(s) !")
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
        st.divider()
        st.balloons()
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
                    st.session_state.choix_dex = i
                    st.rerun()
            else:
                if i == choix:
                    st.success(f"🌟 VOTRE CHOIX\n\n**{starters[i]['nom']}**")
                    st.markdown(f'<div style="text-align: center;"><img src="{starters[i]["image"]}" style="width: 150px;"></div>', unsafe_allow_html=True)
                else:
                    st.error(f"❌ Ignoré\n\n{starters[i]['nom']}")
                    st.markdown(f'<div style="text-align: center;"><img src="{starters[i]["image"]}" style="width: 100px; opacity: 0.5;"></div>', unsafe_allow_html=True)

    if choix is not None:
        st.divider()
        st.balloons()
        st.header(f"Mémoire infaillible ! C'était bien **{starters[choix]['nom']}** ! 🎉")
        if st.button("Recommencer un tirage 🔄", type="primary"):
            del st.session_state.starters_dex
            st.session_state.choix_dex = None
            st.rerun()

# ==========================================
# 📊 MODE : BLIND STARTER (MEILLEURE STAT)
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
                    st.session_state.choix_stat = i
                    st.rerun()
            else:
                if i == choix:
                    st.success(f"🌟 RECRUTÉ !\n\n**{starters[i]['nom']}**")
                    st.markdown(f'<div style="text-align: center;"><img src="{starters[i]["image"]}" style="width: 150px;"></div>', unsafe_allow_html=True)
                else:
                    st.error(f"❌ Recalé\n\n{starters[i]['nom']}")
                    st.markdown(f'<div style="text-align: center;"><img src="{starters[i]["image"]}" style="width: 100px; opacity: 0.5;"></div>', unsafe_allow_html=True)

    if choix is not None:
        st.divider()
        st.balloons()
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
                    # OEUFS AGRANDIS À 120px ICI
                    egg_html = f'<img src="data:image/png;base64,{img_oeuf}" style="width: 120px; filter: drop-shadow(0px 5px 5px rgba(0,0,0,0.3));">'
                except:
                    egg_html = '<div style="font-size: 100px; text-align:center;">🥚</div>'
                
                st.markdown(f"<div class='egg-anim'>{egg_html}</div>", unsafe_allow_html=True)
                
                if st.button(f"🔥 Faire éclore le {i+1}", key=f"btn_oeuf_{i}", use_container_width=True, type="primary"):
                    st.session_state.choix_oeuf = i
                    st.rerun()
            else:
                if i == choix:
                    st.success(f"🌟 IL ÉCLOT !\n\n**{starters[i]['nom']}**")
                    st.markdown(f'<div style="text-align: center;"><img src="{starters[i]["image"]}" style="width: 150px;"></div>', unsafe_allow_html=True)
                else:
                    st.error(f"❌ Laissé à la pension\n\n{starters[i]['nom']}")
                    st.markdown(f'<div style="text-align: center;"><img src="{starters[i]["image"]}" style="width: 100px; opacity: 0.5;"></div>', unsafe_allow_html=True)

    if choix is not None:
        st.divider()
        st.balloons()
        st.header(f"Oh ? Un **{starters[choix]['nom']}** sort de l'œuf ! 🎉")
        if st.button("Adopter un nouvel œuf 🔄", type="primary"):
            del st.session_state.starters_oeuf
            st.session_state.choix_oeuf = None
            st.rerun()

# ==========================================
# 🔎 MODE : BLIND STARTER (ZOOM INTENSIF 9.0)
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
                    st.session_state.choix_zoom = i
                    st.rerun()
            else:
                if i == choix:
                    st.success(f"🌟 VOTRE CHOIX\n\n**{starters[i]['nom']}**")
                    st.markdown(f'<div style="text-align: center;"><img src="{starters[i]["image"]}" style="width: 150px;"></div>', unsafe_allow_html=True)
                else:
                    st.error(f"❌ Écarté\n\n{starters[i]['nom']}")
                    st.markdown(f'<div style="text-align: center;"><img src="{starters[i]["image"]}" style="width: 100px; opacity: 0.5;"></div>', unsafe_allow_html=True)

    if choix is not None:
        st.divider()
        st.balloons()
        st.header(f"Excellente observation ! C'est bien un **{starters[choix]['nom']}** ! 🎉")
        if st.button("Nouveaux échantillons 🔄", type="primary"):
            del st.session_state.starters_zoom
            st.session_state.choix_zoom = None
            st.rerun()

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
        st.divider()
        st.balloons()
        st.header(f"Félicitations ! Vous partez à l'aventure avec **{starters[choix]['nom']}** ! 🎉")
        if st.button("Vider la machine et recommencer 🔄", type="primary"):
            del st.session_state.starters_labo
            st.session_state.choix_labo = None
            st.session_state.vues_labo = {0: "adn", 1: "adn", 2: "adn"}
            st.rerun()

elif mode_choisi == "🕵️‍♂️ Qui est-ce ? (Pokémon)":
    st.title("🕵️‍♂️ Le Plateau Qui est-ce ? (Pokémon)")
    st.write("Un Pokémon secret a été tiré au sort parmi les 9 générations (1025 Pokémon). Éliminez les suspects et portez votre accusation !")

    if "pokemon_secret" not in st.session_state:
        with st.spinner("🔮 Invocation de 24 Pokémon aléatoires (1G à 9G)..."):
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
        st.balloons()
        st.success(f"🏆 BIEN JOUÉ ! Le Pokémon mystère était bien **{nom_secret}** !")
        if secret_poke: st.markdown(f'<div style="text-align: center;"><img src="{secret_poke["image"]}" style="width: 200px; filter: drop-shadow(0px 10px 15px rgba(16, 185, 129, 0.4));"></div>', unsafe_allow_html=True)
        st.write("")
        if st.button("Recommencer une partie Pokémon 🔄", type="primary", use_container_width=True):
            del st.session_state.pokemon_secret; del st.session_state.pokemon_liste; del st.session_state.pokemon_elimines
            st.session_state.pokemon_gagne = False; st.rerun()
    else:
        noms_pour_selection = ["-- Qui est-ce ? --"] + [p["nom"] for p in st.session_state.pokemon_liste]
        accusation_poke = st.selectbox("🎯 PORTER UNE ACCUSATION FINALE :", noms_pour_selection, key="acc_poke")
        if accusation_poke != "-- Qui est-ce ? --":
            if accusation_poke.lower() == nom_secret.lower(): st.session_state.pokemon_gagne = True; st.rerun()
            else: st.error(f"❌ Ce n'est pas {accusation_poke} ! Poursuivez vos recherches.")
        st.divider()
        st.subheader("📋 Votre plateau de jeu (24 Pokémon)")
        with st.expander("👀 Voir le secret"): st.write(f"Pokémon : **{nom_secret}**")
        cols = st.columns(4)
        for idx, p in enumerate(st.session_state.pokemon_liste):
            est_elimine = p["nom"] in st.session_state.pokemon_elimines
            with cols[idx % 4]:
                if est_elimine:
                    st.markdown(f"""<div class="game-card-eliminated"><img src="{p["image"]}" style="width: 90px; margin-bottom: 5px;"><p style="margin: 0; font-size: 13px; font-weight: bold; text-decoration: line-through;">{p["nom"]}</p></div>""", unsafe_allow_html=True)
                    if st.button("🔄", key=f"ret_poke_{idx}", use_container_width=True): st.session_state.pokemon_elimines.remove(p["nom"]); st.rerun()
                else:
                    st.markdown(f"""<div class="game-card"><img src="{p["image"]}" style="width: 90px; margin-bottom: 5px; filter: drop-shadow(0px 5px 5px rgba(0,0,0,0.3));"><p style="margin: 0; font-size: 13px; font-weight: bold; color: #ff4b4b;">{p["nom"]}</p></div>""", unsafe_allow_html=True)
                    if st.button("❌", key=f"elim_poke_{idx}", use_container_width=True): st.session_state.pokemon_elimines.append(p["nom"]); st.rerun()

elif mode_choisi == "⚔️ Qui est-ce ? (Smash Bros)":
    st.title("⚔️ Le Plateau Qui est-ce ? (Smash Bros)")
    st.write("Un personnage secret a été tiré au sort. Éliminez les suspects et portez votre accusation !")

    if not os.path.exists(DOSSIER_PORTRAITS):
        st.error(f"📁 Dossier introuvable ! Il devrait être ici : {DOSSIER_PORTRAITS}")
    else:
        tous_les_persos = [f for f in os.listdir(DOSSIER_PORTRAITS) if f.endswith(('.png', '.jpg', '.jpeg'))]
        if len(tous_les_persos) == 0:
            st.warning("⚠️ Le dossier 'portraits' est vide !")
        else:
            if "smash_secret" not in st.session_state:
                taille_grille = min(len(tous_les_persos), 24)
                st.session_state.smash_liste = random.sample(tous_les_persos, taille_grille)
                st.session_state.smash_secret = random.choice(st.session_state.smash_liste)
                st.session_state.smash_elimines = []
                st.session_state.smash_gagne = False

            secret_file = st.session_state.smash_secret
            nom_secret = os.path.splitext(secret_file)[0]

            if st.session_state.smash_gagne:
                st.balloons()
                st.success(f"🏆 BIEN JOUÉ ! Le personnage mystère était bien **{nom_secret}** !")
                img_encoded = get_base64_image(os.path.join(DOSSIER_PORTRAITS, secret_file))
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
                st.divider()
                st.subheader("📋 Votre plateau de jeu (24 personnages)")
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
                            if st.button("❌", key=f"elim_smash_{idx}", use_container_width=True): st.session_state.smash_elimines.append(fichier); st.rerun()

# ==========================================
# 🧝‍♂️ MODE : QUI EST-CE ? (ZELDA) - DÉPLACÉ EN DERNIER
# ==========================================
elif mode_choisi == "🧝‍♂️ Qui est-ce ? (Zelda)":
    st.title("🧝‍♂️ Le Plateau Qui est-ce ? (Zelda)")
    st.write("Un personnage ou monstre d'Hyrule a été tiré au sort. Éliminez les suspects et portez votre accusation !")

    tous_les_persos_zelda = list(ZELDA_DATA.keys())
    
    if "zelda_qe_secret" not in st.session_state:
        taille_grille = min(len(tous_les_persos_zelda), 24)
        st.session_state.zelda_qe_liste = random.sample(tous_les_persos_zelda, taille_grille)
        st.session_state.zelda_qe_secret = random.choice(st.session_state.zelda_qe_liste)
        st.session_state.zelda_qe_elimines = []
        st.session_state.zelda_qe_gagne = False

    nom_secret = st.session_state.zelda_qe_secret

    if st.session_state.zelda_qe_gagne:
        st.balloons()
        st.success(f"🏆 BIEN JOUÉ ! L'entité mystère était bien **{nom_secret}** !")
        img_html = get_zelda_image(nom_secret, size=250, center=True)
        st.markdown(f'<div>{img_html}</div>', unsafe_allow_html=True)
        st.write("")
        if st.button("Recommencer une partie Zelda 🔄", type="primary", use_container_width=True):
            del st.session_state.zelda_qe_secret; del st.session_state.zelda_qe_liste; del st.session_state.zelda_qe_elimines
            st.session_state.zelda_qe_gagne = False; st.rerun()
    else:
        noms_pour_selection = ["-- Qui est-ce ? --"] + sorted(st.session_state.zelda_qe_liste)
        accusation = st.selectbox("🎯 PORTER UNE ACCUSATION FINALE :", noms_pour_selection, key="acc_zelda")
        
        if accusation != "-- Qui est-ce ? --":
            if accusation.lower() == nom_secret.lower(): st.session_state.zelda_qe_gagne = True; st.rerun()
            else: st.error(f"❌ Ce n'est pas {accusation} ! Retentez votre chance.")
            
        st.divider()
        st.subheader("📋 Votre plateau de jeu (24 suspects)")
        with st.expander("👀 Voir le secret"): st.write(f"Personnage : **{nom_secret}**")
        
        cols = st.columns(4)
        for idx, nom_perso in enumerate(st.session_state.zelda_qe_liste):
            img_html = get_zelda_image(nom_perso, size=100, center=True)
            est_elimine = nom_perso in st.session_state.zelda_qe_elimines
            
            with cols[idx % 4]:
                if est_elimine:
                    st.markdown(f"""<div class="game-card-eliminated">{img_html}<p style="margin: 0; font-size: 14px; font-weight: bold; text-decoration: line-through;">{nom_perso}</p></div>""", unsafe_allow_html=True)
                    if st.button("🔄", key=f"ret_z_{idx}", use_container_width=True): st.session_state.zelda_qe_elimines.remove(nom_perso); st.rerun()
                else:
                    st.markdown(f"""<div class="game-card game-card-zelda">{img_html}<p style="margin: 0; font-size: 14px; font-weight: bold; color: #facc15;">{nom_perso}</p></div>""", unsafe_allow_html=True)
                    if st.button("❌", key=f"elim_z_{idx}", use_container_width=True): st.session_state.zelda_qe_elimines.append(nom_perso); st.rerun()