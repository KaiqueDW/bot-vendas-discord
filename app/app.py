# ======================= [IMPORT] ======================= 
from flask import Flask, render_template, request, redirect, url_for, session, send_file
import pymysql, os, csv, json
from datetime import datetime, timedelta
from collections import Counter
from io import StringIO

# ======================= [FLASK] ======================= 
app2 = Flask(__name__, template_folder='templates', static_folder='static')
app2.secret_key = os.urandom(128)

# ======================= [CONFIG] ======================= 
with open("config.json", "r") as f:
    CONFIG = json.load(f)

MYSQL_CONF = CONFIG.get("mysql", {})
WEB_USERNAME = CONFIG["WEB_LOGIN"]["username"]
WEB_PASSWORD = CONFIG["WEB_LOGIN"]["password"]

# ======================= [MYSQL Connect] ======================= 
def get_data():
    conn = pymysql.connect(
        host=MYSQL_CONF["host"],
        user=MYSQL_CONF["user"],
        password=MYSQL_CONF["password"],
        database=MYSQL_CONF["database"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn.cursor(), conn

@app2.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        if user == WEB_USERNAME and pw == WEB_PASSWORD:
            session['logado'] = True
            return redirect(url_for('dashboard'))
        return "Login inválido"
    return render_template('login.html')

@app2.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app2.route('/')
def dashboard():
    if not session.get('logado'):
        return redirect('/login')

    cursor, conn = get_data()
    cursor.execute("SELECT * FROM vendas")
    vendas = cursor.fetchall()

    hoje = datetime.now().date()
    semana = hoje - timedelta(days=7)
    mes = hoje.replace(day=1)

    vendas_dia = [v for v in vendas if v['DataHora'].date() == hoje]
    vendas_semana = [v for v in vendas if v['DataHora'].date() >= semana]
    vendas_mes = [v for v in vendas if v['DataHora'].date() >= mes]

    valor_dia = sum(v['Valor'] for v in vendas_dia)
    valor_semana = sum(v['Valor'] for v in vendas_semana)
    valor_mes = sum(v['Valor'] for v in vendas_mes)

    formas = Counter(v['FormaPagamento'] for v in vendas)
    forma_mais_usada = formas.most_common(1)[0][0] if formas else "-"
    forma_menos_usada = formas.most_common()[-1][0] if formas else "-"

    produtos = Counter(v['Produto'] for v in vendas)
    produto_mais_vendido = produtos.most_common(1)[0][0] if produtos else "-"
    produto_menos_vendido = produtos.most_common()[-1][0] if produtos else "-"

    cursor.execute("""
        SELECT DATE_FORMAT(DataHora, '%%d/%%m') as dia, SUM(Valor) as total
        FROM vendas
        WHERE DataHora >= CURDATE() - INTERVAL 6 DAY
        GROUP BY dia
    """)
    rows = cursor.fetchall()
    labels = [row['dia'] for row in rows]
    valores = [round(row['total'], 2) for row in rows]

    cursor.execute("SELECT FormaPagamento, COUNT(*) as qtd FROM vendas GROUP BY FormaPagamento")
    pagamento_stats = cursor.fetchall()

    cursor.execute("""
        SELECT DATE_FORMAT(DataHora, '%%d/%%m') as dia, Produto, COUNT(*) as qtd
        FROM vendas
        WHERE DataHora >= CURDATE() - INTERVAL 6 DAY
        GROUP BY dia, Produto
    """)
    produto_data = cursor.fetchall()
    conn.close()

    produtos_unicos = list(set(row['Produto'] for row in produto_data))
    dias = sorted(list(set(row['dia'] for row in produto_data)))

    series = {produto: [0] * len(dias) for produto in produtos_unicos}
    for row in produto_data:
        dia_idx = dias.index(row['dia'])
        series[row['Produto']][dia_idx] = row['qtd']

    return render_template("dashboard.html",
        valor_dia=valor_dia,
        valor_semana=valor_semana,
        valor_mes=valor_mes,
        total_dia=len(vendas_dia),
        total_semana=len(vendas_semana),
        total_mes=len(vendas_mes),
        forma_mais_usada=forma_mais_usada,
        forma_menos_usada=forma_menos_usada,
        produto_mais_vendido=produto_mais_vendido,
        produto_menos_vendido=produto_menos_vendido,
        labels=labels,
        valores=valores,
        pagamento_stats=pagamento_stats,
        dias=dias,
        series=series
    )

@app2.route('/transacoes')
def transacoes():
    if not session.get('logado'):
        return redirect('/login')

    busca = request.args.get('q')
    cursor, conn = get_data()
    if busca:
        cursor.execute("""
            SELECT * FROM vendas
            WHERE Usuario LIKE %s OR DiscordID LIKE %s
        """, (f"%{busca}%", f"%{busca}%"))
    else:
        cursor.execute("SELECT * FROM vendas")
    vendas = cursor.fetchall()
    return render_template("transacoes.html", vendas=vendas, busca=busca or "")

@app2.route('/pagamentos')
def pagamentos():
    if not session.get('logado'):
        return redirect('/login')

    cursor, conn = get_data()
    cursor.execute("SELECT * FROM pagamentos")
    registros = cursor.fetchall()
    return render_template("pagamentos.html", registros=registros)

@app2.route('/exportar_csv')
def exportar_csv():
    if not session.get('logado'):
        return redirect('/login')

    cursor, conn = get_data()
    cursor.execute("SELECT * FROM vendas")
    rows = cursor.fetchall()

    si = StringIO()
    writer = csv.writer(si)
    if rows:
        writer.writerow(rows[0].keys())
        for row in rows:
            writer.writerow(row.values())
    si.seek(0)
    return send_file(
        StringIO(si.read()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='vendas.csv'
    )

if __name__ == "__main__":
    app2.run(debug=True, port=8001)
