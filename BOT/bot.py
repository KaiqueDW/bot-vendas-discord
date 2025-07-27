import discord
from discord.ext import commands
from discord.ui import Button, View
from Utils.pagamento import criar_preferencia
from Utils.utils import init_db
import json
from produtos.produtos import produtos

init_db()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

class ProdutoButton(Button):
    def __init__(self, produto):
        super().__init__(
            label="🛒 Comprar agora",
            style=discord.ButtonStyle.green,
            custom_id=f"comprar_{produto['id']}"
        )
        self.produto = produto

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            link = criar_preferencia(self.produto, interaction.user.id)
            await interaction.followup.send(
                f"🔗 Pague com Mercado Pago: {link}\n\nVocê receberá o código automaticamente após o pagamento.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Erro ao criar o link: {e}", ephemeral=True)

class ProdutoView(View):
    def __init__(self, produto):
        super().__init__(timeout=None)
        self.add_item(ProdutoButton(produto))

@bot.command()
@commands.has_permissions(administrator=True)
async def publicar(ctx, produto_id: int):
    produto = produtos.get(produto_id)
    if not produto:
        await ctx.send("❌ Produto não encontrado.")
        return

    canal = bot.get_channel(produto["canal_id"])
    if not canal:
        await ctx.send("❌ Canal do produto não encontrado.")
        return

    embed = discord.Embed(
        title=produto["nome"],
        description=f"{produto['descricao']}\n\n💰 **Preço:** R${produto['preco']:.2f}",
        color=discord.Color.blurple()
    )
    embed.set_image(url=produto["imagem"])

    await canal.send(embed=embed, view=ProdutoView(produto))
    await ctx.send("✅ Produto publicado com sucesso.")


async def start():
    for produto in produtos.values():
        canal = bot.get_channel(produto["canal_id"])
        print(f"🔍 Processando produto: {produto['nome']} em {produto["canal_id"]}")
        if not canal:
            print(f"❌ Canal com ID {produto['canal_id']} não encontrado.")
            continue

        print(f"🧹 Limpando mensagens do canal {canal.name}")
        try:
            async for msg in canal.history(limit=50):
                if msg.author == bot.user:
                    await msg.delete()
        except Exception as e:
            print(f"⚠️ Erro ao apagar mensagens no canal {canal.name}: {e}")
            continue

        embed = discord.Embed(
            title=f"🛒 {produto['nome']}",
            description=produto["descricao"],
            color=discord.Color.green()
        )
        embed.add_field(name="💵 Preço", value=f"R${produto['preco']:.2f}", inline=False)
        if produto["imagem"]:
            embed.set_thumbnail(url=produto["imagem"])

        view = View()
        view.add_item(ProdutoButton(produto))
        bot.add_view(ProdutoView(produto))
        print(f"📤 Enviando mensagem para {canal.name}")
        await canal.send(embed=embed, view=view)
    