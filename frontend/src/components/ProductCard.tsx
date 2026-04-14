import { Link } from 'react-router-dom'
import { TrendingUp, MessageSquare, Tag, Weight, Ruler, DollarSign } from 'lucide-react'
import type { Produto } from '../types'
import { getCategoryImage, formatCategoria } from '../utils/categoryImages'
import StarRating from './StarRating'

interface ProductCardProps {
  produto: Produto
}

function formatPeso(gramas: number | null): string | null {
  if (!gramas) return null
  if (gramas >= 1000) return `${(gramas / 1000).toFixed(gramas % 1000 === 0 ? 0 : 1)} kg`
  return `${gramas.toLocaleString('pt-BR')} g`
}

function formatDimensoes(
  c: number | null,
  a: number | null,
  l: number | null
): string | null {
  if (!c || !a || !l) return null
  return `${c}×${a}×${l} cm`
}

export default function ProductCard({ produto }: ProductCardProps) {
  const imgUrl = getCategoryImage(produto.categoria_produto)
  const peso = formatPeso(produto.peso_produto_gramas)
  const dims = formatDimensoes(
    produto.comprimento_centimetros,
    produto.altura_centimetros,
    produto.largura_centimetros
  )

  return (
    <Link
      to={`/produtos/${produto.id_produto}`}
      className="card group hover:shadow-md transition-all overflow-hidden flex flex-col"
    >
      {/* Image */}
      <div className="relative h-40 overflow-hidden bg-champagne-200 dark:bg-gray-700 flex-shrink-0">
        <img
          src={imgUrl}
          alt={produto.nome_produto}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          loading="lazy"
          onError={(e) => {
            ;(e.currentTarget as HTMLImageElement).src =
              'https://upload.wikimedia.org/wikipedia/commons/b/b4/Supermarket_z_flagami_%28ubt%29.JPG'
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
        <span className="absolute bottom-2 left-2 badge bg-white/90 text-gray-800 border border-black text-[10px] font-semibold">
          <Tag className="w-2.5 h-2.5 mr-1" />
          {formatCategoria(produto.categoria_produto)}
        </span>
      </div>

      {/* Content */}
      <div className="p-4 flex flex-col gap-2 flex-1">
        {/* Nome */}
        <h3 className="font-semibold text-gray-900 dark:text-gray-100 leading-snug line-clamp-2 group-hover:text-gray-600 dark:group-hover:text-gray-300 transition-colors text-sm">
          {produto.nome_produto}
        </h3>

        {/* Legenda: dimensões físicas */}
        {(peso || dims) && (
          <div className="flex flex-wrap gap-x-3 gap-y-1">
            {peso && (
              <span className="flex items-center gap-1 text-[11px] text-gray-500 dark:text-gray-400">
                <Weight className="w-3 h-3 text-gray-400 dark:text-gray-500 flex-shrink-0" />
                {peso}
              </span>
            )}
            {dims && (
              <span className="flex items-center gap-1 text-[11px] text-gray-500 dark:text-gray-400">
                <Ruler className="w-3 h-3 text-gray-400 dark:text-gray-500 flex-shrink-0" />
                {dims}
              </span>
            )}
          </div>
        )}

        {/* Preço médio */}
        {produto.preco_medio !== null ? (
          <div className="flex items-center gap-1 text-sm font-semibold text-gray-900 dark:text-gray-100">
            <DollarSign className="w-3.5 h-3.5 text-gray-400" />
            {`R$ ${produto.preco_medio.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          </div>
        ) : (
          <span className="text-[11px] text-gray-400">Sem preço</span>
        )}

        {/* Avaliação por estrelas */}
        {produto.media_avaliacao !== null ? (
          <StarRating rating={produto.media_avaliacao} size="sm" />
        ) : (
          <span className="text-[11px] text-gray-400">Sem avaliações</span>
        )}

        {/* Rodapé: vendas e avaliações */}
        <div className="mt-auto flex items-center justify-between pt-2 border-t border-black/10 dark:border-gray-600">
          <div className="flex items-center gap-1 text-[11px] text-gray-500 dark:text-gray-400">
            <TrendingUp className="w-3 h-3 text-green-600 dark:text-green-500" />
            <span>{produto.total_vendas.toLocaleString('pt-BR')} vendas</span>
          </div>

          <div className="flex items-center gap-1 text-[11px] text-gray-500 dark:text-gray-400">
            <MessageSquare className="w-3 h-3 text-gray-400 dark:text-gray-500" />
            <span>{produto.total_avaliacoes.toLocaleString('pt-BR')} aval.</span>
          </div>
        </div>
      </div>
    </Link>
  )
}
