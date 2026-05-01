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
        "login_title": "Entrar no Sistema"
    },
    "en": {
        "welcome": "Welcome to Unitrans Connect",
        "menu_profile": "My Profile",
        "menu_leave": "Leave & Absences",
        "menu_comms": "Announcements",
        "menu_rh": "Contact HR",
        "menu_logout": "Logout",
        "login_error": "Worker number not found",
        "login_title": "System Login"
    }
}


# ===============================
# CARREGAR DADOS (SEGURO)
# ===============================
def carregar_dados():
    try:
        df = pd.read_csv(ARQUIVO, encoding="utf-8-sig")

        obj_cols = df.select_dtypes(include=["object"]).columns
        df[obj_cols] = df[obj_cols].fillna("")

        return df

    except Exception as e:
        print("Erro ao carregar CSV:", e)
        return pd.DataFrame()


# ===============================
# BUSCAR TRABALHADOR
# ===============================
def buscar(numero):
    df = carregar_dados()

    if df.empty:
        return None

    if "Numero do trabalhador" not in df.columns:
        print("Coluna não encontrada no CSV")
        return None

    trabalhador = df[
        df["Numero do trabalhador"].astype(str) == str(numero)
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
# FERIAS
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
    return render_template("comunicados.html")


# ===============================
# RH
# ===============================
@app.route("/rh")
def rh():
    return render_template("rh.html")


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
