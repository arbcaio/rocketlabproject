import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ArrowLeft, Edit, Trash2, Package, Weight, Ruler,
  TrendingUp, MessageSquare, DollarSign, Star, ChevronLeft,
  ChevronRight, Loader2, AlertCircle, Tag
} from 'lucide-react'
import { getProduto, deleteProduto, getAvaliacoes } from '../api/produtos'
import StarRating from '../components/StarRating'
import ConfirmModal from '../components/ConfirmModal'
import { getCategoryImage, formatCategoria } from '../utils/categoryImages'

function StatCard({
  icon: Icon,
  label,
  value,
  color = 'blue',
}: {
  icon: React.ElementType
  label: string
  value: React.ReactNode
  color?: string
}) {
  const colors: Record<string, string> = {
    blue: 'text-blue-400 bg-blue-900/30',
    green: 'text-green-400 bg-green-900/30',
    amber: 'text-amber-400 bg-amber-900/30',
    purple: 'text-purple-400 bg-purple-900/30',
  }
  return (
    <div className="card p-4 flex items-center gap-4">
      <div className={`p-2.5 rounded-xl ${colors[color]}`}>
        <Icon className={`w-5 h-5 ${colors[color].split(' ')[0]}`} />
      </div>
      <div>
        <p className="text-xs text-gray-400">{label}</p>
        <p className="text-lg font-bold text-white">{value}</p>
      </div>
    </div>
  )
}

function RatingBar({ star, count, total }: { star: number; count: number; total: number }) {
  const pct = total > 0 ? (count / total) * 100 : 0
  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="text-gray-400 w-4 text-right">{star}</span>
      <Star className="w-3 h-3 text-amber-400 fill-amber-400 flex-shrink-0" />
      <div className="flex-1 bg-gray-800 rounded-full h-2">
        <div
          className="bg-amber-400 h-2 rounded-full transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-gray-400 w-8 text-right">{count}</span>
    </div>
  )
}

const PAGE_SIZE = 8

export default function ProductDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [avaliacoesPage, setAvaliacoesPage] = useState(1)

  const {
    data: produto,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ['produto', id],
    queryFn: () => getProduto(id!),
    enabled: !!id,
  })

  const { data: avaliacoes, isLoading: loadingAval } = useQuery({
    queryKey: ['avaliacoes', id, avaliacoesPage],
    queryFn: () => getAvaliacoes(id!, { page: avaliacoesPage, page_size: PAGE_SIZE }),
    enabled: !!id,
  })

  const deleteMutation = useMutation({
    mutationFn: () => deleteProduto(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['produtos'] })
      navigate('/produtos')
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-24">
        <Loader2 className="w-8 h-8 text-brand-500 animate-spin" />
      </div>
    )
  }

  if (isError || !produto) {
    return (
      <div className="card p-8 text-center max-w-md mx-auto mt-12">
        <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-3" />
        <h3 className="text-lg font-semibold text-white">Produto não encontrado</h3>
        <Link to="/produtos" className="btn-primary mt-4">
          Voltar ao catálogo
        </Link>
      </div>
    )
  }

  // Compute rating distribution
  const ratingDist = avaliacoes
    ? Array.from({ length: 5 }, (_, i) => {
        const star = 5 - i
        const count = avaliacoes.items.filter((a) => a.avaliacao === star).length
        return { star, count }
      })
    : []

  const imgUrl = getCategoryImage(produto.categoria_produto)

  return (
    <div>
      {/* Back */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-1.5 text-gray-400 hover:text-white mb-6 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Voltar
      </button>

      {/* Hero section */}
      <div className="card overflow-hidden mb-6">
        <div className="flex flex-col md:flex-row">
          {/* Image */}
          <div className="md:w-72 h-56 md:h-auto flex-shrink-0 relative">
            <img
              src={imgUrl}
              alt={produto.nome_produto}
              className="w-full h-full object-cover"
              onError={(e) => {
                ;(e.currentTarget as HTMLImageElement).src =
                  'https://upload.wikimedia.org/wikipedia/commons/b/b4/Supermarket_z_flagami_%28ubt%29.JPG'
              }}
            />
            <div className="absolute inset-0 bg-gradient-to-r from-transparent to-gray-900/40 hidden md:block" />
          </div>

          {/* Info */}
          <div className="p-6 flex-1 flex flex-col justify-between">
            <div>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <span className="badge bg-brand-900/60 text-brand-300 border border-brand-700/50 mb-2">
                    <Tag className="w-3 h-3 mr-1" />
                    {formatCategoria(produto.categoria_produto)}
                  </span>
                  <h1 className="text-2xl font-bold text-white">{produto.nome_produto}</h1>
                  <p className="text-xs text-gray-600 mt-1 font-mono">ID: {produto.id_produto}</p>
                </div>
                <div className="flex gap-2 flex-shrink-0">
                  <Link
                    to={`/produtos/${produto.id_produto}/editar`}
                    className="btn-secondary"
                  >
                    <Edit className="w-4 h-4" />
                    <span className="hidden sm:inline">Editar</span>
                  </Link>
                  <button
                    onClick={() => setShowDeleteModal(true)}
                    className="btn-danger"
                  >
                    <Trash2 className="w-4 h-4" />
                    <span className="hidden sm:inline">Remover</span>
                  </button>
                </div>
              </div>

              {/* Rating */}
              <div className="mt-4">
                <StarRating
                  rating={produto.media_avaliacao}
                  size="lg"
                />
                <p className="text-sm text-gray-500 mt-1">
                  {produto.total_avaliacoes} avaliações
                </p>
              </div>
            </div>

            {/* Dimensions */}
            {(produto.peso_produto_gramas || produto.comprimento_centimetros) && (
              <div className="mt-4 pt-4 border-t border-gray-800">
                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
                  Medidas
                </h3>
                <div className="flex flex-wrap gap-4 text-sm">
                  {produto.peso_produto_gramas && (
                    <div className="flex items-center gap-1.5 text-gray-300">
                      <Weight className="w-3.5 h-3.5 text-gray-500" />
                      <span>{produto.peso_produto_gramas.toLocaleString('pt-BR')} g</span>
                    </div>
                  )}
                  {produto.comprimento_centimetros && (
                    <div className="flex items-center gap-1.5 text-gray-300">
                      <Ruler className="w-3.5 h-3.5 text-gray-500" />
                      <span>
                        {produto.comprimento_centimetros} × {produto.altura_centimetros} × {produto.largura_centimetros} cm
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          icon={TrendingUp}
          label="Total de Vendas"
          value={produto.total_vendas.toLocaleString('pt-BR')}
          color="green"
        />
        <StatCard
          icon={DollarSign}
          label="Receita Total"
          value={`R$ ${produto.receita_total.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`}
          color="blue"
        />
        <StatCard
          icon={DollarSign}
          label="Preço Médio"
          value={
            produto.preco_medio
              ? `R$ ${produto.preco_medio.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`
              : '–'
          }
          color="purple"
        />
        <StatCard
          icon={MessageSquare}
          label="Avaliações"
          value={produto.total_avaliacoes.toLocaleString('pt-BR')}
          color="amber"
        />
      </div>

      {/* Reviews section */}
      <div className="card p-6">
        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-brand-400" />
          Avaliações dos Consumidores
        </h2>

        {loadingAval ? (
          <div className="flex justify-center py-8">
            <Loader2 className="w-6 h-6 text-brand-500 animate-spin" />
          </div>
        ) : avaliacoes && avaliacoes.total > 0 ? (
          <div className="grid md:grid-cols-3 gap-6">
            {/* Summary */}
            <div className="flex flex-col items-center justify-center p-4 bg-gray-800/50 rounded-xl">
              <div className="text-5xl font-bold text-white mb-1">
                {avaliacoes.media_avaliacao?.toFixed(1) ?? '–'}
              </div>
              <StarRating rating={avaliacoes.media_avaliacao ?? null} size="md" showValue={false} />
              <p className="text-gray-400 text-sm mt-2">{avaliacoes.total} avaliações</p>

              {/* Distribution bars */}
              <div className="w-full mt-4 space-y-1.5">
                {ratingDist.map(({ star, count }) => (
                  <RatingBar key={star} star={star} count={count} total={avaliacoes.items.length} />
                ))}
              </div>
            </div>

            {/* List */}
            <div className="md:col-span-2 space-y-3">
              {avaliacoes.items.map((aval) => (
                <div key={aval.id_avaliacao} className="bg-gray-800/40 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <StarRating rating={aval.avaliacao} size="sm" showValue={false} />
                    {aval.data_comentario && (
                      <span className="text-xs text-gray-500">
                        {new Date(aval.data_comentario).toLocaleDateString('pt-BR')}
                      </span>
                    )}
                  </div>
                  {aval.titulo_comentario && aval.titulo_comentario !== 'Sem título' && (
                    <p className="font-medium text-gray-200 text-sm mb-1">{aval.titulo_comentario}</p>
                  )}
                  {aval.comentario && aval.comentario !== 'Sem comentário' && (
                    <p className="text-gray-400 text-sm">{aval.comentario}</p>
                  )}
                </div>
              ))}

              {/* Avaliações pagination */}
              {avaliacoes.pages > 1 && (
                <div className="flex items-center justify-between pt-2">
                  <span className="text-sm text-gray-400">
                    Página {avaliacoes.page} de {avaliacoes.pages}
                  </span>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setAvaliacoesPage((p) => p - 1)}
                      disabled={avaliacoes.page === 1}
                      className="btn-secondary py-1 px-2"
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setAvaliacoesPage((p) => p + 1)}
                      disabled={avaliacoes.page === avaliacoes.pages}
                      className="btn-secondary py-1 px-2"
                    >
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="text-center py-8">
            <Package className="w-10 h-10 text-gray-700 mx-auto mb-2" />
            <p className="text-gray-500">Nenhuma avaliação encontrada para este produto.</p>
          </div>
        )}
      </div>

      {/* Delete modal */}
      {showDeleteModal && (
        <ConfirmModal
          title="Remover Produto"
          message={`Tem certeza que deseja remover "${produto.nome_produto}"? Esta ação não pode ser desfeita.`}
          confirmLabel="Remover Produto"
          onConfirm={() => deleteMutation.mutate()}
          onCancel={() => setShowDeleteModal(false)}
          loading={deleteMutation.isPending}
        />
      )}
    </div>
  )
}
