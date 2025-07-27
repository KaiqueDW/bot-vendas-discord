# BOT de Vendas Automáticas com Painel Web (FastAPI + Discord + Flask)

Este projeto é um sistema completo de vendas automáticas que integra um **BOT no Discord** com pagamentos reais via **Mercado Pago** e um **painel administrativo web**. Ele permite que você venda produtos com entrega automática de códigos, de forma rápida, organizada e segura.

---

## ✨ Funcionalidades

- 💬 BOT no Discord com mensagens personalizadas e **botão de compra** por produto.
- ✅ Integração com **Mercado Pago** para receber pagamentos reais.
- 📦 Suporte a múltiplos produtos com código individual ou sistema de quantidade.
- 🔒 Após o pagamento aprovado, o BOT envia o **código no privado** do usuário.
- 🌐 Painel Web (Flask) com:
  - Estatísticas de vendas por **dia, semana e mês**
  - Gráficos por produto e forma de pagamento
  - Filtro por **conta de pagamento**
  - Visualização de transações e detalhes
- 🧑‍💼 Login seguro no painel com **usuário e senha**
- 🛠 Banco de dados compatível com **MySQL**
- ⚙️ Configuração simples via `config.json`

---

## ⚙️ Como configurar

Clone o repositório:

  ```bash
  git clone https://github.com/kaiqueDW/bot-vendas-discord.git
  cd bot-vendas-discord
```
Instale as dependências:
```bash
  pip install -r requirements.txt
```

Configure o arquivo config.json com suas informações:
```bash
  {
  "token": "SEU_TOKEN_DO_DISCORD",
  "mercado_pago": {
    "access_token": "SEU_ACCESS_TOKEN"
  },
  "mysql": {
    "host": "localhost",
    "user": "root",
    "password": "sua_senha",
    "database": "nome_do_banco"
  },
  "painel": {
    "usuario": "admin",
    "senha": "senha123"
  }
}
```

## 🧠 Boas Práticas de uso:

  Nunca compartilhe seu token do Discord ou access_token do Mercado Pago.

  Use códigos únicos por produto, principalmente em itens limitados.

  Teste seus produtos antes de colocar em produção.

  O BOT envia o link de pagamento no mesmo canal após o usuário clicar em "Comprar" (visível apenas para ele).

  O Mercado Pago, ao aprovar o pagamento, chama a API FastAPI, que envia o código final no privado do cliente automaticamente.

## 📜 Licença

Este projeto está licenciado sob a **Licença MIT**. Você pode usar, modificar e distribuir livremente, desde que mantenha os devidos créditos ao autor.

## 👤 Autor

Desenvolvido por: **kaiqueDW**

📧 Contato: **kaiquedwrodrigues@outlook.com**

🔗 **github.com/kaiqueDW**
