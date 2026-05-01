from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "unitrans2026"

# ===============================
# FICHEIRO DE DADOS
# ===============================
ARQUIVO = "Unitrans.csv"

# ===============================
# TRADUÇÕES
# ===============================
LANG = {
    "pt": {
        "welcome": "Bem-vindo à Unitrans Connect",
        "menu_profile": "Meu Perfil",
        "menu_leave": "Férias e Faltas",
        "menu_comms": "Comunicados",
        "menu_rh": "Contactar RH",
        "menu_logout": "Sair",
        "login_error": "Número não encontrado",
        "login_title": "Entrar no Sistema",

        "comms_general_title": "Geral",
        "comms_general_text": "Caros trabalhadores, os payslips já estão disponíveis junto aos line managers.",

        "comms_safety_title": "Segurança",
        "comms_safety_text": "Reforçar medidas de segurança após incidente recente com equipamento."
    },

    "en": {
        "welcome": "Welcome to Unitrans Connect",
        "menu_profile": "My Profile",
        "menu_leave": "Leave & Absences",
        "menu_comms": "Announcements",
        "menu_rh": "Contact HR",
        "menu_logout": "Logout",
        "login_error": "Worker number not found",
        "login_title": "System Login",

        "comms_general_title": "General",
        "comms_general_text": "Dear workers, payslips are now available with line managers.",

        "comms_safety_title": "Safety",
        "comms_safety_text": "Strengthen safety measures after a recent equipment incident."
    }
}

# ===============================
# CARREGAR DADOS (ULTRA ROBUSTO)
# ===============================
def carregar_dados():
    try:
        df = pd.read_csv(
            ARQUIVO,
            encoding="utf-8-sig",
            sep=None,
            engine="python"
        )

        # limpar colunas
        df.columns = df.columns.str.strip()
        df.columns = df.columns.str.replace("\ufeff", "", regex=True)

        # limpar valores string
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        return df

    except Exception as e:
        print("Erro ao carregar CSV:", e)
        return pd.DataFrame()


# ===============================
# BUSCAR TRABALHADOR (INTELIGENTE)
# ===============================
def buscar(numero):
    df = carregar_dados()

    if df.empty:
        print("CSV vazio")
        return None

    print("COLUNAS DETECTADAS:", df.columns.tolist())

    # localizar coluna automaticamente
    col_numero = None
    for col in df.columns:
        if "trabalhador" in col.lower():
            col_numero = col
            break

    if not col_numero:
        print("Coluna de trabalhador não encontrada")
        return None

    trabalhador = df[
        df[col_numero].astype(str).str.strip() == str(numero).strip()
    ]

    if trabalhador.empty:
        return None

    return trabalhador.iloc[0].to_dict()


# ===============================
# HOME
# ===============================
@app.route("/")
def home():
    return render_template("idioma.html")


# ===============================
# IDIOMA
# ===============================
@app.route("/idioma/<lang>")
def idioma(lang):

    if lang not in ["pt", "en"]:
        lang = "pt"

    session["lang"] = lang
    return redirect(url_for("login"))


# ===============================
# LOGIN
# ===============================
@app.route("/login", methods=["GET", "POST"])
def login():

    lang = session.get("lang", "pt")
    t = LANG[lang]

    erro = ""

    if request.method == "POST":
        numero = request.form.get("numero")
        user = buscar(numero)

        if user:
            session["numero"] = numero
            return redirect(url_for("menu"))
        else:
            erro = t["login_error"]

    return render_template("login.html", erro=erro, t=t)


# ===============================
# MENU
# ===============================
@app.route("/menu")
def menu():

    if "numero" not in session:
        return redirect(url_for("login"))

    lang = session.get("lang", "pt")
    t = LANG[lang]

    user = buscar(session["numero"])

    return render_template("menu.html", user=user, t=t)


# ===============================
# PERFIL
# ===============================
@app.route("/perfil")
def perfil():
    if "numero" not in session:
        return redirect(url_for("login"))

    user = buscar(session["numero"])
    return render_template("perfil.html", user=user)


# ===============================
# FÉRIAS
# ===============================
@app.route("/ferias")
def ferias():
    if "numero" not in session:
        return redirect(url_for("login"))

    user = buscar(session["numero"])
    return render_template("ferias.html", user=user)


# ===============================
# COMUNICADOS
# ===============================
@app.route("/comunicados")
def comunicados():

    lang = session.get("lang", "pt")
    t = LANG[lang]

    return render_template("comunicados.html", t=t)


# ===============================
# RH
# ===============================
@app.route("/rh")
def rh():
    return render_template("rh.html")


# ===============================
# SOBRE NÓS
# ===============================
@app.route("/sobre")
def sobre():
    return render_template("sobre.html")


# ===============================
# LOGOUT
# ===============================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ===============================
# ERRO 500
# ===============================
@app.errorhandler(500)
def erro_500(e):
    return "Erro interno no servidor. Verifique os logs no Render.", 500


# ===============================
# START
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
