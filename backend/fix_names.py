"""
Corrige nomes de produtos que foram inseridos com aspas extras no banco de dados.

Ex: '"Monitor 24"" Prata"' → 'Monitor 24" Prata'

Uso (dentro do backend com .venv ativo):
    python fix_names.py          # mostra preview das correções
    python fix_names.py --apply  # aplica as correções no banco
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.models.produto import Produto


def clean_str(value: str) -> str:
    v = value.strip()
    if len(v) >= 2 and v.startswith('"') and v.endswith('"'):
        v = v[1:-1]
    v = v.replace('""', '"')
    return v.strip()


def needs_fix(value: str) -> bool:
    cleaned = clean_str(value)
    return cleaned != value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplica as correções no banco (sem este flag, apenas mostra o preview)",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        produtos = db.query(Produto).all()
        correcoes = [
            (p, clean_str(p.nome_produto))
            for p in produtos
            if needs_fix(p.nome_produto)
        ]

        if not correcoes:
            print("✅  Nenhum nome com aspas extras encontrado. Banco já está limpo!")
            return

        print(f"🔍  {len(correcoes)} produto(s) com aspas para corrigir:\n")
        for produto, nome_limpo in correcoes[:20]:  # mostra até 20 exemplos
            print(f"  Antes:  {produto.nome_produto!r}")
            print(f"  Depois: {nome_limpo!r}")
            print()

        if len(correcoes) > 20:
            print(f"  ... e mais {len(correcoes) - 20} produto(s).\n")

        if not args.apply:
            print("💡  Execute com --apply para salvar as correções no banco:")
            print("    python fix_names.py --apply")
            return

        for produto, nome_limpo in correcoes:
            produto.nome_produto = nome_limpo

        db.commit()
        print(f"✅  {len(correcoes)} nome(s) corrigido(s) com sucesso!")

    except Exception as e:
        db.rollback()
        print(f"❌  Erro: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
