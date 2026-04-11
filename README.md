# E-Commerce Manager 🛒

Sistema de Gerenciamento de E-Commerce para o Gerente da loja. Permite visualizar o catálogo de produtos, acompanhar desempenho de vendas e avaliações, e gerenciar produtos individualmente.

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Frontend | Vite + React + TypeScript + Tailwind CSS |
| Backend | FastAPI (Python) |
| Banco de Dados | SQLite (via SQLAlchemy + Alembic) |

---

## Pré-requisitos

- **Python 3.11+**
- **Node.js 18+** e **npm**
- **Git**

---

## Como executar

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/rocketlab2026.git
cd rocketlab2026
```

---

### 2. Backend

```bash
cd backend
```

#### 2.1 Crie e ative o ambiente virtual

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python -m venv .venv
source .venv/bin/activate
```

#### 2.2 Instale as dependências

```bash
pip install -r requirements.txt
```

#### 2.3 Configure o arquivo de ambiente

```bash
cp .env.example .env
# O padrão já usa SQLite local, nenhuma alteração necessária
```

#### 2.4 Aplique as migrações do banco de dados

```bash
alembic upgrade head
```

#### 2.5 Popule o banco com os dados CSV

```bash
# Informe o caminho para a pasta com os arquivos CSV
python seed.py --csv-dir "C:\caminho\para\sua\pasta\csvs"

# Exemplo (Windows)
python seed.py --csv-dir "C:\Users\seu-usuario\Downloads\arquivos atividade visagio"

# Exemplo (Linux/macOS)
python seed.py --csv-dir ~/Downloads/csvs
```

Os arquivos CSV esperados são:
- `dim_consumidores.csv`
- `dim_produtos.csv`
- `dim_vendedores.csv`
- `fat_pedidos.csv`
- `fat_itens_pedidos.csv`
- `fat_avaliacoes_pedidos.csv`

#### 2.6 Inicie o servidor

```bash
python -m uvicorn app.main:app --reload --port 8000
```

A API ficará disponível em: http://localhost:8000  
Documentação interativa (Swagger): http://localhost:8000/docs

---

### 3. Frontend

Em um **novo terminal**:

```bash
cd frontend
npm install
npm run dev
```

O frontend ficará disponível em: http://localhost:5173

---

## Funcionalidades

### Catálogo de Produtos
- Listagem em grade com imagens por categoria
- Busca em tempo real por nome ou categoria
- Filtro por categoria com contagem de produtos
- Paginação com 20 itens por página

### Detalhes do Produto
- Informações completas (dimensões, peso)
- **Métricas de desempenho**: total de vendas, receita total, preço médio
- **Avaliações**: média com estrelas, distribuição por nota, lista paginada

### Gerenciamento de Produtos
- **Criar** novos produtos com formulário validado
- **Editar** produtos existentes (campos opcionais)
- **Remover** produto com confirmação modal

---

## Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/produtos` | Lista produtos (busca, categoria, paginação) |
| `GET` | `/produtos/categorias` | Lista todas as categorias |
| `GET` | `/produtos/{id}` | Detalhes com stats de vendas e avaliações |
| `POST` | `/produtos` | Cria novo produto |
| `PUT` | `/produtos/{id}` | Atualiza produto |
| `DELETE` | `/produtos/{id}` | Remove produto |
| `GET` | `/produtos/{id}/avaliacoes` | Lista avaliações paginadas |

---

## Estrutura do Projeto

```
rocketlab2026/
├── backend/
│   ├── alembic/              # Migrações do banco de dados
│   ├── app/
│   │   ├── models/           # Modelos SQLAlchemy
│   │   ├── schemas/          # Schemas Pydantic
│   │   ├── routers/          # Rotas FastAPI
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── seed.py               # Script de população do banco
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── api/              # Camada de comunicação com o backend
    │   ├── components/       # Componentes reutilizáveis
    │   ├── pages/            # Páginas da aplicação
    │   ├── types/            # Tipos TypeScript
    │   └── utils/            # Utilitários (imagens por categoria, etc.)
    ├── package.json
    └── vite.config.ts
```
