import asyncio
import json
import uvicorn
from BOT.bot import bot, start
from api.api import app
from app.app import app2
from threading import Thread

with open("config.json") as f:
    config = json.load(f)

def iniciar_flask():
    app2.run(host="0.0.0.0", port=8001)
    print("✅ Painel web iniciado!")

async def start_fastapi():
    config_uvicorn = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config_uvicorn)
    await server.serve()

@bot.event
async def on_ready():
    print(f"✅ Bot iniciado como {bot.user}")
    await start()
    bot.loop.create_task(start_fastapi())  #  Inicia FastAPI no mesmo loop


if __name__ == "__main__":
    try:
        thread_flask = Thread(target=iniciar_flask, daemon=True)
        thread_flask.start()

        asyncio.run(bot.start(config["discord_token"]))
    except KeyboardInterrupt:
        print("Finalizado pelo usuário.")
