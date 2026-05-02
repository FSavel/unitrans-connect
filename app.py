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

        # Geral
        "welcome": "Bem-vindo à Unitrans Connect",
        "login_title": "Entrar no Sistema",
        "login_error": "Número não encontrado",
        "worker_number": "Número do trabalhador",
        "enter": "Entrar",

        # Menu
        "menu_profile": "Meu Perfil",
        "menu_leave": "Férias e Faltas",
        "menu_comms": "Comunicados",
        "menu_rh": "Contactar RH",
        "menu_logout": "Sair",

        # Perfil
        "profile_title": "Meu Perfil",
        "name": "Nome",
        "employee_number": "Número do trabalhador",
        "absences": "Faltas",
        "leave_balance": "Férias",
        "id_number": "Número de BI",
        "license": "Carta de Condução",
        "contract_start": "Início de Contrato",
        "contract_end": "Fim de contrato",

        # Férias
        "leave_title": "Férias e Faltas",
        "request_leave": "Solicitar Férias",
        "start_date": "Data de Início",
        "end_date": "Data de Fim",
        "submit_request": "Enviar Pedido",

        # Comunicados
        "comms_title": "Comunicados",
        "comms_general_title": "Geral",
        "comms_general_text": "Caros trabalhadores, os payslips já estão disponíveis junto aos line managers.",
        "comms_safety_title": "Segurança",
        "comms_safety_text": "Reforçar medidas de segurança após incidente recente com equipamento.",

        # RH
        "rh_title": "Contactar RH",
        "rh_text": "Estamos disponíveis para apoiar.",
        "suggestion_type": "Tipo de Mensagem",
        "suggestion_option1": "Sugestão",
        "suggestion_option2": "Reclamação",
        "suggestion_option3": "Pedido RH",
        "suggestion_option4": "Problema Técnico",
        "message": "Mensagem",
        "send": "Enviar",

        # Sobre
        "about": "Sobre Nós"
    },

    "en": {

        # General
        "welcome": "Welcome to Unitrans Connect",
        "login_title": "System Login",
        "login_error": "Worker number not found",
        "worker_number": "Employee Number",
        "enter": "Login",

        # Menu
        "menu_profile": "My Profile",
        "menu_leave": "Leave & Absences",
        "menu_comms": "Announcements",
        "menu_rh": "Contact HR",
        "menu_logout": "Logout",

        # Profile
        "profile_title": "My Profile",
        "name": "Name",
        "employee_number": "Employee Number",
        "absences": "Absences",
        "leave_balance": "Leave Balance",
        "id_number": "ID Number",
        "license": "Driver License",
        "contract_start": "Contract Start",
        "contract_end": "Contract End",

        # Leave
        "leave_title": "Leave & Absences",
        "request_leave": "Request Leave",
        "start_date": "Start Date",
        "end_date": "End Date",
        "submit_request": "Submit Request",

        # Announcements
        "comms_title": "Announcements",
        "comms_general_title": "General",
        "comms_general_text": "Dear workers, payslips are now available with line managers.",
        "comms_safety_title": "Safety",
        "comms_safety_text": "Strengthen safety measures after a recent equipment incident.",

        # HR
        "rh_title": "Contact HR",
        "rh_text": "We are available to assist.",
        "suggestion_type": "Message Type",
        "suggestion_option1": "Suggestion",
        "suggestion_option2": "Complaint",
        "suggestion_option3": "HR Request",
        "suggestion_option4": "Technical Issue",
        "message": "Message",
        "send": "Submit",

        # About
        "about": "About Us"
    }
}

# ===============================
# CARREGAR CSV
# ===============================
def carregar_dados():
    try:
        df = pd.read_csv(
            ARQUIVO,
            encoding="utf-8-sig",
            sep=None,
            engine="python"
        )

        df.columns = df.columns.str.strip()
        df.columns = df.columns.str.replace("\ufeff", "", regex=True)

        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].astype(str).str.strip()

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

    col_numero = None

    for col in df.columns:
        if "trabalhador" in col.lower():
            col_numero = col
            break

    if not col_numero:
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

    lang = session.get("lang", "pt")
    t = LANG[lang]

    user = buscar(session["numero"])

    return render_template("perfil.html", user=user, t=t)

# ===============================
# FÉRIAS
# ===============================
@app.route("/ferias")
def ferias():

    if "numero" not in session:
        return redirect(url_for("login"))

    lang = session.get("lang", "pt")
    t = LANG[lang]

    user = buscar(session["numero"])

    return render_template("ferias.html", user=user, t=t)

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

    lang = session.get("lang", "pt")
    t = LANG[lang]

    return render_template("rh.html", t=t)

# ===============================
# SOBRE
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
# START
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
