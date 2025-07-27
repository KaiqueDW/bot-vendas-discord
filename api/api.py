from fastapi import FastAPI, Request
import mercadopago
import json
from Utils.utils import inserir_codigo, registrar_pagamento, registrar_venda_aprovada
from BOT.bot import bot
from produtos.produtos import produtos

with open("config.json") as f:
    config = json.load(f)

sdk = mercadopago.SDK(config["mercadopago_token"])
app = FastAPI()

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    if data.get("type") == "payment":
        payment_id = data["data"]["id"]

        payment_info = sdk.payment().get(payment_id)["response"]
        status = payment_info["status"]
        metadata = payment_info.get("metadata", {})

        discord_id = metadata.get("discord_id")
        produto_id = metadata.get("produto_id")

        produto = produtos.get(produto_id)
        nome_produto = produto["nome"] if produto else "Desconhecido"
        valor = produto["preco"]
        forma_pagamento = payment_info.get("payment_method_id", "Desconhecido")

        try:
            user = await bot.fetch_user(int(discord_id))
            nome_usuario = f"{user.name}#{user.discriminator}"
        except Exception as e:
            print(f"[Webhook] Erro ao buscar usuário: {e}")
            nome_usuario = "Desconhecido"

        registrar_pagamento(
            payment_id,
            discord_id,
            nome_usuario,
            nome_produto,
            valor,
            status,
            forma_pagamento
        )
        try:
            await user.send(
                f"✅ Um link de pagamento foi gerado e assinado pela sua conta, ele expira em 23 horas. Você tem 23 horas para pagar até o link se expirar"
            )
        except Exception as e:
            print(f"[Webhook] Erro ao enviar mensagem: {e}")

        if status == "approved" and produto:
            codigo = inserir_codigo(discord_id, produto["tipo"], produto["qtd"], True)
            registrar_venda_aprovada(
                payment_id,
                discord_id,
                nome_usuario,
                nome_produto,
                valor,
                forma_pagamento,
                codigo
            )

            try:
                await user.send(
                    f"✅ Pagamento aprovado!\nSeu código: `{codigo}`\nUse-o no servidor."
                )
            except Exception as e:
                print(f"[Webhook] Erro ao enviar mensagem: {e}")

    return {"ok": True}
