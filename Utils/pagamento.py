import mercadopago
import json

with open("config.json") as f:
    config = json.load(f)

sdk = mercadopago.SDK(config["mercadopago_token"])
def criar_preferencia(produto, user_id):
    data = {
        "items": [{
            "title": produto["nome"],
            "quantity": 1,
            "unit_price": float(produto["preco"]),
            "currency_id": "BRL"
        }],
        "payer": {
            "email": "cliente@botcompras.com"  # Aqui tu coloca o email do BRV ou o seu próprio
        },
        "notification_url": config["webhook_url"],
        "auto_return": "approved",
        "back_urls": {
            "success": "https://discord.com",
            "failure": "https://discord.com",
            "pending": "https://discord.com"
        },
        "metadata": {
            "discord_id": str(user_id),
            "produto_id": produto["id"]
        },
        "external_reference": f"{user_id}-{produto['id']}-{produto['nome']}"
    }

    resposta = sdk.preference().create(data)

    if "response" not in resposta or "init_point" not in resposta["response"]:
        print("[ERRO] Resposta inesperada do Mercado Pago:")
        print(json.dumps(resposta, indent=4))
        raise Exception("Erro ao criar link de pagamento. Verifique o token ou dados enviados.")

    return resposta["response"]["init_point"]
