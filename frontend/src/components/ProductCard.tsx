import { Link } from 'react-router-dom'
import { TrendingUp, MessageSquare, Tag, Weight, Ruler } from 'lucide-react'
import type { Produto } from '../types'
import { getCategoryImage, formatCategoria } from '../utils/categoryImages'
import StarRating from './StarRating'

interface ProductCardProps {
  produto: Produto
  mediaAvaliacao?: number | null
  totalAvaliacoes?: number
  totalVendas?: number
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

export default function ProductCard({
  produto,
  mediaAvaliacao,
  totalAvaliacoes,
  totalVendas,
}: ProductCardProps) {
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
      className="card group hover:border-brand-600 transition-all hover:shadow-lg hover:shadow-brand-900/30 overflow-hidden flex flex-col"
    >
      {/* Image */}
      <div className="relative h-40 overflow-hidden bg-gray-800 flex-shrink-0">
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
        <div className="absolute inset-0 bg-gradient-to-t from-gray-900/80 to-transparent" />
        <span className="absolute bottom-2 left-2 badge bg-gray-900/80 text-gray-300 border border-gray-700 text-[10px]">
          <Tag className="w-2.5 h-2.5 mr-1" />
          {formatCategoria(produto.categoria_produto)}
        </span>
      </div>

      {/* Content */}
      <div className="p-4 flex flex-col gap-2 flex-1">
        {/* Nome */}
        <h3 className="font-semibold text-white leading-snug line-clamp-2 group-hover:text-brand-400 transition-colors text-sm">
          {produto.nome_produto}
        </h3>

        {/* Legenda: dimensões físicas — principal diferenciador entre SKUs */}
        {(peso || dims) && (
          <div className="flex flex-wrap gap-x-3 gap-y-1">
            {peso && (
              <span className="flex items-center gap-1 text-[11px] text-gray-400">
                <Weight className="w-3 h-3 text-gray-600 flex-shrink-0" />
                {peso}
              </span>
            )}
            {dims && (
              <span className="flex items-center gap-1 text-[11px] text-gray-400">
                <Ruler className="w-3 h-3 text-gray-600 flex-shrink-0" />
                {dims}
              </span>
            )}
          </div>
        )}

        {/* Avaliação por estrelas */}
        {mediaAvaliacao !== undefined && mediaAvaliacao !== null && (
          <StarRating rating={mediaAvaliacao} size="sm" />
        )}

        {/* Rodapé: vendas e avaliações */}
        <div className="mt-auto flex items-center justify-between pt-2 border-t border-gray-800">
          <div className="flex items-center gap-1 text-[11px] text-gray-500">
            <TrendingUp className="w-3 h-3 text-green-500" />
            <span>
              {totalVendas !== undefined
                ? `${totalVendas.toLocaleString('pt-BR')} vendas`
                : '– vendas'}
            </span>
          </div>

          <div className="flex items-center gap-1 text-[11px] text-gray-500">
            <MessageSquare className="w-3 h-3 text-blue-500" />
            <span>
              {totalAvaliacoes !== undefined
                ? `${totalAvaliacoes.toLocaleString('pt-BR')} aval.`
                : '–'}
            </span>
          </div>
        </div>
      </div>
    </Link>
  )
}
