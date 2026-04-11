"""
Script de seed: popula o banco de dados SQLite com os dados dos arquivos CSV.

Uso:
    python seed.py                          # procura CSVs na pasta atual
    python seed.py --csv-dir /caminho/csvs  # pasta personalizada
"""

import argparse
import csv
import os
import sys
from datetime import datetime, date
from pathlib import Path

# Garante que o módulo app seja importado corretamente
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal, engine
from app.models import (  # noqa: F401 – registra todos os modelos no metadata
    AvaliacaoPedido,
    Consumidor,
    ItemPedido,
    Pedido,
    Produto,
    Vendedor,
)
from app.database import Base

# ── Utilitários ───────────────────────────────────────────────────────────────

def parse_float(val: str):
    try:
        return float(val) if val and val.strip() else None
    except ValueError:
        return None


def parse_datetime(val: str):
    if not val or not val.strip():
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(val.strip(), fmt)
        except ValueError:
            pass
    return None


def parse_date(val: str):
    if not val or not val.strip():
        return None
    try:
        return date.fromisoformat(val.strip()[:10])
    except ValueError:
        return None


def clean_str(value: str) -> str:
    """Remove aspas extras que o CSV deixa em nomes com caracteres especiais.
    Ex: '"Monitor 24"" Prata"' → 'Monitor 24" Prata'
    """
    v = value.strip()
    # Remove aspas que envolvem o valor inteiro
    if len(v) >= 2 and v.startswith('"') and v.endswith('"'):
        v = v[1:-1]
    # Normaliza aspas duplas internas ("") para aspas simples (")
    v = v.replace('""', '"')
    return v.strip()


def load_csv(path: str):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def bulk_insert(session, model, rows: list[dict], key_field: str, transform_fn):
    """Insere ou ignora registros já existentes."""
    existing = {r[0] for r in session.query(getattr(model, key_field)).all()}
    objs = []
    for row in rows:
        pk = row.get(key_field)
        if pk and pk not in existing:
            obj = transform_fn(row)
            if obj:
                objs.append(obj)
                existing.add(pk)
    if objs:
        session.bulk_save_objects(objs)
        session.commit()
    return len(objs)


# ── Transformadores ───────────────────────────────────────────────────────────

def to_consumidor(r: dict):
    return Consumidor(
        id_consumidor=r["id_consumidor"],
        prefixo_cep=r.get("prefixo_cep", ""),
        nome_consumidor=r.get("nome_consumidor", ""),
        cidade=r.get("cidade", ""),
        estado=r.get("estado", ""),
    )


def to_produto(r: dict):
    return Produto(
        id_produto=r["id_produto"],
        nome_produto=clean_str(r.get("nome_produto", "Sem nome")),
        categoria_produto=clean_str(r.get("categoria_produto", "outros")) or "outros",
        peso_produto_gramas=parse_float(r.get("peso_produto_gramas", "")),
        comprimento_centimetros=parse_float(r.get("comprimento_centimetros", "")),
        altura_centimetros=parse_float(r.get("altura_centimetros", "")),
        largura_centimetros=parse_float(r.get("largura_centimetros", "")),
    )


def to_vendedor(r: dict):
    return Vendedor(
        id_vendedor=r["id_vendedor"],
        nome_vendedor=r.get("nome_vendedor", ""),
        prefixo_cep=r.get("prefixo_cep", ""),
        cidade=r.get("cidade", ""),
        estado=r.get("estado", ""),
    )


def to_pedido(r: dict):
    return Pedido(
        id_pedido=r["id_pedido"],
        id_consumidor=r["id_consumidor"],
        status=r.get("status", ""),
        pedido_compra_timestamp=parse_datetime(r.get("pedido_compra_timestamp", "")),
        pedido_entregue_timestamp=parse_datetime(r.get("pedido_entregue_timestamp", "")),
        data_estimada_entrega=parse_date(r.get("data_estimada_entrega", "")),
        tempo_entrega_dias=parse_float(r.get("tempo_entrega_dias", "")),
        tempo_entrega_estimado_dias=parse_float(r.get("tempo_entrega_estimado_dias", "")),
        diferenca_entrega_dias=parse_float(r.get("diferenca_entrega_dias", "")),
        entrega_no_prazo=r.get("entrega_no_prazo", None),
    )


def to_avaliacao(r: dict):
    try:
        avaliacao_val = int(r["avaliacao"]) if r.get("avaliacao") else 1
    except ValueError:
        avaliacao_val = 1
    return AvaliacaoPedido(
        id_avaliacao=r["id_avaliacao"],
        id_pedido=r["id_pedido"],
        avaliacao=avaliacao_val,
        titulo_comentario=r.get("titulo_comentario") or None,
        comentario=r.get("comentario") or None,
        data_comentario=parse_datetime(r.get("data_comentario", "")),
        data_resposta=parse_datetime(r.get("data_resposta", "")),
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def seed(csv_dir: str):
    print("🌱  Iniciando seed do banco de dados...")
    Base.metadata.create_all(bind=engine)

    csv_dir = Path(csv_dir)

    files = {
        "consumidores": csv_dir / "dim_consumidores.csv",
        "produtos": csv_dir / "dim_produtos.csv",
        "vendedores": csv_dir / "dim_vendedores.csv",
        "pedidos": csv_dir / "fat_pedidos.csv",
        "itens": csv_dir / "fat_itens_pedidos.csv",
        "avaliacoes": csv_dir / "fat_avaliacoes_pedidos.csv",
    }

    for key, path in files.items():
        if not path.exists():
            print(f"  ⚠️  Arquivo não encontrado: {path}")

    session = SessionLocal()
    try:
        # Ordem importa por FK
        tasks = [
            ("consumidores", "dim_consumidores.csv", Consumidor, "id_consumidor", to_consumidor),
            ("produtos", "dim_produtos.csv", Produto, "id_produto", to_produto),
            ("vendedores", "dim_vendedores.csv", Vendedor, "id_vendedor", to_vendedor),
            ("pedidos", "fat_pedidos.csv", Pedido, "id_pedido", to_pedido),
            ("avaliacoes", "fat_avaliacoes_pedidos.csv", AvaliacaoPedido, "id_avaliacao", to_avaliacao),
        ]

        for label, filename, model, key, fn in tasks:
            path = csv_dir / filename
            if not path.exists():
                print(f"  ⏭️  {label}: arquivo não encontrado, pulando.")
                continue
            rows = load_csv(str(path))
            count = bulk_insert(session, model, rows, key, fn)
            print(f"  ✅  {label}: {count} registros inseridos ({len(rows)} no CSV)")

        # Itens de pedido têm PK composta — tratamento especial
        itens_path = csv_dir / "fat_itens_pedidos.csv"
        if itens_path.exists():
            rows = load_csv(str(itens_path))
            pedidos_ids = {r[0] for r in session.query(Pedido.id_pedido).all()}
            produtos_ids = {r[0] for r in session.query(Produto.id_produto).all()}
            vendedores_ids = {r[0] for r in session.query(Vendedor.id_vendedor).all()}

            objs = []
            inserted = 0
            for r in rows:
                if (
                    r["id_pedido"] not in pedidos_ids
                    or r["id_produto"] not in produtos_ids
                    or r["id_vendedor"] not in vendedores_ids
                ):
                    continue
                try:
                    item = ItemPedido(
                        id_pedido=r["id_pedido"],
                        id_item=int(r["id_item"]),
                        id_produto=r["id_produto"],
                        id_vendedor=r["id_vendedor"],
                        preco_BRL=float(r["preco_BRL"]),
                        preco_frete=float(r["preco_frete"]),
                    )
                    objs.append(item)
                    inserted += 1
                    if len(objs) >= 5000:
                        session.bulk_save_objects(objs)
                        session.commit()
                        objs = []
                except Exception:
                    pass
            if objs:
                session.bulk_save_objects(objs)
                session.commit()
            print(f"  ✅  itens_pedidos: {inserted} registros inseridos ({len(rows)} no CSV)")

        print("\n🎉  Seed concluído com sucesso!")
    except Exception as e:
        session.rollback()
        print(f"\n❌  Erro durante o seed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Popula o banco de dados com dados CSV.")
    parser.add_argument(
        "--csv-dir",
        default=".",
        help="Caminho para a pasta com os arquivos CSV (padrão: pasta atual)",
    )
    args = parser.parse_args()
    seed(args.csv_dir)
