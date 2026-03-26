<div align="center">

# Price Monitor

**Monitoramento automático de preços em e-commerces com alertas por e-mail**

[![CI](https://github.com/jmello04/price-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/jmello04/price-monitor/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/License-MIT-22c55e)](LICENSE)

</div>

---

## Sobre

Price Monitor é uma API REST que rastreia preços de produtos em e-commerces brasileiros, persiste o histórico em banco de dados relacional e envia alertas por e-mail automaticamente quando o preço atinge ou cai abaixo da meta configurada.

```
Produto cadastrado → Scraping a cada N horas → Histórico salvo → Preço alvo? → E-mail enviado
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
| Testes automatizados | Cobertura de API e scrapers com mocks, sem dependências externas |
| Docker ready | App + PostgreSQL com um único comando |

---

## Arquitetura

```
price-monitor/
├── app/
│   ├── api/routes/         # Camada HTTP: recebe requests, chama services, retorna responses
│   ├── services/           # Camada de negócio: toda lógica de domínio isolada aqui
│   ├── infra/database/     # Modelos ORM, engine e sessão
│   ├── scraper/            # Scrapers por site (Amazon, Mercado Livre)
│   ├── scheduler/          # Jobs periódicos via APScheduler
│   ├── notifications/      # Envio de alertas SMTP
│   └── core/               # Configuração e schemas Pydantic
└── tests/                  # Testes de integração e unitários
```

O projeto segue separação estrita entre camadas: as rotas não contêm lógica de negócio — apenas delegam ao `ProductService`, que centraliza criação, listagem, histórico e verificação de preço.

---

## Stack

| Camada | Tecnologia | Motivo |
|--------|-----------|--------|
| API REST | FastAPI + Uvicorn | Performance assíncrona, validação automática via Pydantic, OpenAPI nativo |
| Banco de dados | PostgreSQL 15 + SQLAlchemy 2.0 | Persistência relacional robusta com ORM tipado |
| Scraping | BeautifulSoup4 + Requests | Parsing HTML simples, fácil de estender para novos sites |
| Agendamento | APScheduler 3.x | Scheduling in-process sem dependência de infraestrutura externa |
| Notificações | smtplib (stdlib) | Sem dependência extra; compatível com qualquer provedor SMTP |
| Testes | Pytest + pytest-mock + SQLite in-memory | Execução rápida, isolada e sem banco de dados externo |
| Infra | Docker + Docker Compose | Ambiente reproduzível em qualquer máquina |
| Qualidade | Ruff | Lint e formatação em um único binário ultra-rápido |

---

## Como executar

### Pré-requisitos

- [Docker](https://www.docker.com/) e [Docker Compose](https://docs.docker.com/compose/) **ou** Python 3.11+ com PostgreSQL

---

### Opção 1 — Docker Compose (recomendado)

```bash
git clone https://github.com/jmello04/price-monitor.git
cd price-monitor

cp .env.example .env
# Edite .env com suas credenciais SMTP

docker compose up --build
```

A API ficará disponível em **http://localhost:8000/docs**

---

### Opção 2 — Execução local

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows

pip install -r requirements.txt

cp .env.example .env
# Ajuste DATABASE_URL e credenciais SMTP no .env

uvicorn app.main:app --reload
```

---

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/health` | Status da aplicação |
| `POST` | `/products/` | Cadastrar produto para monitoramento |
| `GET` | `/products/` | Listar produtos monitorados |
| `GET` | `/products/{id}/history` | Histórico de preços |
| `DELETE` | `/products/{id}` | Remover produto do monitoramento |
| `POST` | `/products/{id}/check` | Verificar preço manualmente |

**Exemplo — cadastrar produto:**

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

---

## Variáveis de ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `DATABASE_URL` | URL de conexão PostgreSQL | `postgresql://postgres:postgres@localhost/pricedb` |
| `SMTP_HOST` | Servidor SMTP | `smtp.gmail.com` |
| `SMTP_PORT` | Porta SMTP | `587` |
| `SMTP_USER` | Usuário SMTP | — |
| `SMTP_PASSWORD` | Senha ou senha de aplicativo | — |
| `SMTP_FROM` | E-mail exibido como remetente | igual ao `SMTP_USER` |
| `CHECK_INTERVAL_HOURS` | Intervalo de verificação em horas | `6` |

> Se `SMTP_USER` ou `SMTP_PASSWORD` não estiverem configurados, a aplicação continua funcionando normalmente — apenas os alertas não são enviados.

---

## Testes

Os testes utilizam SQLite in-memory com `StaticPool` para isolamento total. Scrapers e scheduler são mockados.

```bash
pytest tests/ -v
```

---

## Estrutura de pastas

```
price-monitor/
├── .github/workflows/ci.yml     # CI: testes + lint
├── app/
│   ├── main.py                  # Entry point da aplicação
│   ├── api/routes/products.py   # Endpoints REST
│   ├── services/product_service.py  # Lógica de negócio
│   ├── core/
│   │   ├── config.py            # Configurações via variáveis de ambiente
│   │   └── schemas.py           # Schemas Pydantic
│   ├── infra/database/
│   │   ├── models.py            # Modelos ORM
│   │   └── session.py           # Engine e SessionLocal
│   ├── scraper/
│   │   ├── base.py              # Classe abstrata
│   │   └── sites/               # amazon.py, mercadolivre.py
│   ├── scheduler/tasks.py       # Jobs periódicos
│   └── notifications/email_sender.py
├── tests/
│   ├── conftest.py
│   ├── test_products_api.py
│   └── test_scraper.py
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── ruff.toml
```

---

## Licença

Distribuído sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
