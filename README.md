<div align="center">

# Price Monitor

**Monitoramento automático de preços em e-commerces com alertas por e-mail**

[![CI](https://github.com/jmello04/price-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/jmello04/price-monitor/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/License-MIT-22c55e)](LICENSE)

<br/>

<img src="https://img.shields.io/badge/Amazon-suportado-FF9900?logo=amazon&logoColor=white"/>
<img src="https://img.shields.io/badge/Mercado%20Livre-suportado-FFE600?logo=mercadolibre&logoColor=black"/>

</div>

---

## Sobre o projeto

O **Price Monitor** é uma API REST completa que rastreia preços de produtos em e-commerces brasileiros, persiste o histórico em banco de dados relacional e dispara alertas por e-mail automaticamente assim que o preço atinge ou cai abaixo da meta configurada.

```
Produto cadastrado → Scraping a cada 6h → Histórico salvo → Preço alvo? → E-mail enviado
```

---

## Funcionalidades

| Recurso | Descrição |
|---------|-----------|
| Cadastro de produtos | URL, nome, preço alvo e e-mail de notificação |
| Scraping automático | Verificação periódica via APScheduler (padrão: 6h) |
| Verificação manual | Endpoint dedicado para checar o preço sob demanda |
| Histórico completo | Menor, maior e preço atual registrados por produto |
| Alertas por e-mail | Template HTML responsivo enviado via SMTP |
| Soft delete | Produtos desativados sem perda de histórico |
| Documentação interativa | Swagger UI em `/docs` e ReDoc em `/redoc` |
| Testes automatizados | 30 testes cobrindo API e scrapers com mocks |
| Docker ready | App + PostgreSQL prontos para subir com um comando |

---

## Stack

| Camada | Tecnologia |
|--------|-----------|
| API REST | FastAPI + Uvicorn |
| Banco de dados | PostgreSQL 15 + SQLAlchemy 2.0 |
| Scraping | BeautifulSoup4 + Requests |
| Agendamento | APScheduler 3.10 |
| Notificações | smtplib (stdlib) |
| Testes | Pytest + pytest-mock + SQLite in-memory |
| Infra | Docker + Docker Compose |
| Qualidade | Ruff |

---

## Estrutura do projeto

```
price-monitor/
├── .github/
│   └── workflows/
│       └── ci.yml              # Pipeline de CI (testes + lint)
├── app/
│   ├── main.py                 # Entry point da aplicação
│   ├── api/
│   │   └── routes/
│   │       └── products.py     # Endpoints REST
│   ├── core/
│   │   ├── config.py           # Configurações via variáveis de ambiente
│   │   └── schemas.py          # Schemas Pydantic (validação e serialização)
│   ├── infra/
│   │   └── database/
│   │       ├── models.py       # Modelos ORM (Product, PriceHistory)
│   │       └── session.py      # Engine, SessionLocal e get_db
│   ├── scraper/
│   │   ├── base.py             # Classe abstrata + limpeza de preço
│   │   └── sites/
│   │       ├── __init__.py     # Registro e seleção de scrapers por URL
│   │       ├── amazon.py       # Scraper Amazon Brasil
│   │       └── mercadolivre.py # Scraper Mercado Livre
│   ├── scheduler/
│   │   └── tasks.py            # Jobs periódicos e verificação individual
│   └── notifications/
│       └── email_sender.py     # Envio de alertas SMTP com template HTML
├── tests/
│   ├── conftest.py             # Fixtures com SQLite in-memory + mocks
│   ├── test_products_api.py    # 14 testes de integração dos endpoints
│   └── test_scraper.py         # 16 testes unitários dos scrapers
├── .env.example                # Modelo de variáveis de ambiente
├── docker-compose.yml          # Orquestração App + PostgreSQL
├── Dockerfile                  # Imagem da aplicação
├── pytest.ini                  # Configuração do Pytest
├── requirements.txt            # Dependências Python
└── ruff.toml                   # Configuração do linter
```

---

## Como executar

### Pré-requisitos

- [Docker](https://www.docker.com/) e [Docker Compose](https://docs.docker.com/compose/) **ou** Python 3.11+ com PostgreSQL

---

### Opção 1 — Docker Compose (recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/jmello04/price-monitor.git
cd price-monitor

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais SMTP

# 3. Suba os serviços
docker compose up --build
```

A API ficará disponível em **http://localhost:8000/docs**

---

### Opção 2 — Execução local

```bash
# 1. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure o ambiente
cp .env.example .env

# 4. Inicie a API (requer PostgreSQL rodando)
uvicorn app.main:app --reload
```

---

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/health` | Status da aplicação |
| `POST` | `/products/` | Cadastrar produto para monitoramento |
| `GET` | `/products/` | Listar produtos monitorados |
| `GET` | `/products/{id}/history` | Histórico de preços do produto |
| `DELETE` | `/products/{id}` | Remover produto do monitoramento |
| `POST` | `/products/{id}/check` | Verificar preço manualmente agora |

---

### Exemplos de uso

**Cadastrar produto:**

```bash
curl -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Notebook Dell XPS 15",
    "url": "https://www.amazon.com.br/dp/B08N5M7S6K",
    "target_price": 3500.00,
    "email": "voce@exemplo.com"
  }'
```

**Histórico de preços:**

```bash
curl http://localhost:8000/products/1/history
```

```json
{
  "product": "Notebook Dell XPS 15",
  "current_price": 3799.90,
  "lowest_price": 3499.00,
  "highest_price": 4299.00,
  "target_price": 3500.00,
  "history": [
    { "price": 3799.90, "checked_at": "2026-03-24T10:00:00Z" },
    { "price": 3499.00, "checked_at": "2026-03-23T10:00:00Z" }
  ]
}
```

**Disparo manual de verificação:**

```bash
curl -X POST http://localhost:8000/products/1/check
```

---

## Configuração de e-mail

O serviço usa SMTP para envio de alertas. Recomendamos o **Gmail com Senha de App**.

**Passo a passo:**

1. Acesse sua conta Google → **Segurança** → **Verificação em duas etapas** (deve estar ativa)
2. Em **Senhas de app**, gere uma nova senha para "Price Monitor"
3. Preencha o `.env`:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
SMTP_FROM=seu-email@gmail.com
```

> Se as credenciais SMTP não forem configuradas, a aplicação continua funcionando normalmente — apenas os alertas não serão enviados, registrando um aviso no log.

---

## Variáveis de ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `DATABASE_URL` | URL de conexão PostgreSQL | `postgresql://postgres:postgres@localhost/pricedb` |
| `SMTP_HOST` | Servidor SMTP | `smtp.gmail.com` |
| `SMTP_PORT` | Porta SMTP | `587` |
| `SMTP_USER` | Usuário SMTP | — |
| `SMTP_PASSWORD` | Senha ou senha de app | — |
| `SMTP_FROM` | E-mail exibido como remetente | igual ao `SMTP_USER` |
| `CHECK_INTERVAL_HOURS` | Intervalo de verificação (horas) | `6` |

---

## Testes

Os testes utilizam **SQLite in-memory com StaticPool** para isolamento total. Scrapers e scheduler são mockados, garantindo execução rápida e sem dependências externas.

```bash
# Rodar todos os testes
pytest

# Com relatório de cobertura
pytest --cov=app --cov-report=term-missing
```

```
30 passed in 1.16s
```

---

## Licença

Distribuído sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
