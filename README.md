# E-Commerce Manager

Sistema de gerenciamento de e-commerce: catálogo de produtos, vendas, consumidores, vendedores e pedidos.

**Stack:** React + TypeScript + Vite (frontend) · FastAPI + SQLite + SQLAlchemy (backend)

---

## Pré-requisitos

- Python 3.11+
- Node.js 18+

---

## Executando o projeto

### Backend

```bash
cd backend

# Dependências
pip install -r requirements.txt

# Banco de dados
alembic upgrade head

# Popular com dados CSV
# Os CSVs devem estar em rocketlab2026/files/ (buscado automaticamente)
python seed.py

# Iniciar
python -m uvicorn app.main:app --reload --port 8000
```

API: `http://localhost:8000` · Swagger: `http://localhost:8000/docs`

**Arquivos CSV esperados** (coloque em `files/` na raiz do repositório):
`dim_consumidores.csv`, `dim_produtos.csv`, `dim_vendedores.csv`, `fat_pedidos.csv`, `fat_itens_pedidos.csv`, `fat_avaliacoes_pedidos.csv`

---

### Frontend

Em um novo terminal:

```bash
cd frontend
npm install
npm run dev
```

App: `http://localhost:5173` (o backend precisa estar rodando na porta 8000)

---

## Login

| Usuário  | Senha            |
|----------|------------------|
| `rocket` | `equipeRocket@1` |

---

## Testes

```bash
# Backend (148 testes)
cd backend
pytest -v

# Frontend (99 testes)
cd frontend
npm test
```

---

## Estrutura do repositório

```
rocketlab2026/
├── files/           # CSVs de dados (dim_consumidores.csv, dim_produtos.csv, ...)
├── backend/
│   ├── app/
│   │   ├── models/      # Modelos SQLAlchemy
│   │   ├── schemas/     # Schemas Pydantic
│   │   ├── routers/     # Rotas FastAPI
│   │   ├── database.py
│   │   └── main.py
│   ├── alembic/         # Migrações do banco
│   ├── tests/           # Testes de integração
│   ├── seed.py          # Importação dos CSVs
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── api/         # Chamadas ao backend
    │   ├── components/  # Componentes reutilizáveis
    │   ├── context/     # AuthContext, ThemeContext
    │   ├── pages/       # CatalogPage, LoginPage, etc.
    │   └── utils/
    ├── package.json
    └── vite.config.ts
```

---