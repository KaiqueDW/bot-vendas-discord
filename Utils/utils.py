import pymysql
from datetime import datetime
import random
import json
from produtos.produtos import produtos

with open("config.json") as f:
    config = json.load(f)

MYSQL_CONF = config.get("mysql", {})


def get_connection():
    return pymysql.connect(
        host=MYSQL_CONF["host"],
        user=MYSQL_CONF["user"],
        password=MYSQL_CONF["password"],
        database=MYSQL_CONF["database"],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )


def init_db():
    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS codigos (
            Codigo VARCHAR(255) PRIMARY KEY,
            Tipo INT,
            Quantidade INT,
            CodigoUnico BOOLEAN,
            DiscordID VARCHAR(255)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pagamentos (
            PagamentoID VARCHAR(255) PRIMARY KEY,
            DiscordID VARCHAR(255),
            NomeUsuario VARCHAR(255),
            Produto VARCHAR(255),
            Valor FLOAT,
            Status VARCHAR(50),
            FormaPagamento VARCHAR(50)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            PagamentoID VARCHAR(255),
            DiscordID VARCHAR(255),
            Usuario VARCHAR(255),
            Produto VARCHAR(255),
            Valor FLOAT,
            FormaPagamento VARCHAR(50),
            DataHora DATETIME,
            Codigo VARCHAR(255)
        )
    """)
    con.close()


def gerar_codigo():
    agora = datetime.now()
    base = agora.strftime("%d%m%Y%H%M%S")
    extra = int((random.randint(0, 100) * agora.hour - agora.minute + agora.second) / (agora.day or 1)) \
        + random.randint(0, 5) + random.randint(100, 500) - random.randint(0, 5)
    return f"{base}{extra}"


def inserir_codigo(discord_id, tipo, qtd, unico):
    codigo = gerar_codigo()
    con = get_connection()
    cur = con.cursor()

    query = "INSERT INTO codigos (Codigo, Tipo, Quantidade, CodigoUnico, DiscordID) VALUES (%s, %s, %s, %s, %s)"
    cur.execute(query, (codigo, tipo, qtd, int(unico), str(discord_id)))

    con.close()
    return codigo


def registrar_pagamento(payment_id, discord_id, nome_usuario, produto, valor, status, forma_pagamento):
    con = get_connection()
    cur = con.cursor()

    query = """
        REPLACE INTO pagamentos (
            PagamentoID, DiscordID, NomeUsuario, Produto, Valor, Status, FormaPagamento
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cur.execute(query, (
        payment_id,
        str(discord_id),
        nome_usuario,
        produto,
        valor,
        status,
        forma_pagamento
    ))

    con.close()


def registrar_venda_aprovada(payment_id, discord_id, usuario_nome, produto, valor, forma_pagamento, codigo):
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    con = get_connection()
    cur = con.cursor()

    query = """
        INSERT INTO vendas (
            PagamentoID, DiscordID, Usuario, Produto, Valor, FormaPagamento, DataHora, Codigo
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cur.execute(query, (
        payment_id,
        str(discord_id),
        usuario_nome,
        produto,
        valor,
        forma_pagamento,
        data_hora,
        codigo
    ))

    con.close()
