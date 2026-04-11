"""
Diagnóstico da base de dados: conta registros e verifica duplicatas.

Uso (dentro do backend com .venv ativo):
    python check_data.py
    python check_data.py --csv-dir "C:\caminho\para\csvs"
"""
import argparse
import csv
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))


def check_csv(path: Path, id_col: str, label: str):
    if not path.exists():
        print(f"  ⚠️  {label}: arquivo não encontrado")
        return
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    ids = [r[id_col] for r in rows if r.get(id_col)]
    unique = len(set(ids))
    dups = {k: v for k, v in Counter(ids).items() if v > 1}
    status = "✅" if not dups else "❌ DUPLICATAS ENCONTRADAS"
    print(f"  {status}  {label}: {len(rows)} linhas | {unique} IDs únicos | {len(dups)} IDs duplicados")
    if dups:
        for dup_id, count in list(dups.items())[:5]:
            print(f"          ID '{dup_id}' aparece {count}×")

    return len(rows), unique


def check_db():
    try:
        from app.database import SessionLocal
        from app.models import Produto, Pedido, ItemPedido, AvaliacaoPedido, Consumidor, Vendedor
        from sqlalchemy import func, select

        db = SessionLocal()
        print("\n📊  Banco de Dados (SQLite):")
        tables = [
            ("Produtos",      Produto,         "id_produto"),
            ("Consumidores",  Consumidor,       "id_consumidor"),
            ("Vendedores",    Vendedor,         "id_vendedor"),
            ("Pedidos",       Pedido,           "id_pedido"),
            ("Itens Pedidos", ItemPedido,       None),
            ("Avaliações",    AvaliacaoPedido,  "id_avaliacao"),
        ]
        for label, model, pk in tables:
            count = db.scalar(select(func.count()).select_from(model))
            print(f"  {label:<18}: {count:>8,} registros")
        db.close()
    except Exception as e:
        print(f"  ⚠️  Erro ao conectar ao banco: {e}")
        print("      (execute 'alembic upgrade head' e depois 'python seed.py' primeiro)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv-dir", default=".")
    args = parser.parse_args()
    csv_dir = Path(args.csv_dir)

    print(f"\n🔍  Analisando CSVs em: {csv_dir.resolve()}\n")
    print("📁  Arquivos CSV:")

    check_csv(csv_dir / "dim_produtos.csv",          "id_produto",    "Produtos")
    check_csv(csv_dir / "dim_consumidores.csv",      "id_consumidor", "Consumidores")
    check_csv(csv_dir / "dim_vendedores.csv",        "id_vendedor",   "Vendedores")
    check_csv(csv_dir / "fat_pedidos.csv",           "id_pedido",     "Pedidos")
    check_csv(csv_dir / "fat_itens_pedidos.csv",     "id_pedido",     "Itens (por pedido)")
    check_csv(csv_dir / "fat_avaliacoes_pedidos.csv","id_avaliacao",  "Avaliações")

    # Nomes de produto duplicados (esperado no dataset sintético)
    produtos_path = csv_dir / "dim_produtos.csv"
    if produtos_path.exists():
        with open(produtos_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        nomes = [r["nome_produto"] for r in rows]
        nomes_dup = {k: v for k, v in Counter(nomes).items() if v > 1}
        print(f"\n  ℹ️   Nomes de produto repetidos (IDs diferentes): {len(nomes_dup)}")
        print(f"       → Normal no dataset sintético — são SKUs distintos do mesmo produto")
        if nomes_dup:
            top5 = sorted(nomes_dup.items(), key=lambda x: -x[1])[:5]
            for nome, count in top5:
                print(f"         '{nome}' aparece {count}× (IDs únicos)")

    check_db()
    print()


if __name__ == "__main__":
    main()
