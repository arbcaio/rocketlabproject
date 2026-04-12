import { useState, useCallback, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search, Filter, X, Package, AlertCircle, Loader2, ArrowUpDown, Star, TrendingUp, ArrowUp, ArrowDown } from 'lucide-react'
import { listProdutos, getCategorias, type OrdenarPor } from '../api/produtos'
import ProductCard from '../components/ProductCard'
import Pagination from '../components/Pagination'
import { formatCategoria } from '../utils/categoryImages'

const PAGE_SIZE = 20

const SORT_OPTIONS: { value: OrdenarPor; label: string; icon: React.ElementType }[] = [
  { value: 'nome',       label: 'Nome',          icon: ArrowUpDown },
  { value: 'avaliacao',  label: 'Avaliação',      icon: Star },
  { value: 'vendas',     label: 'Vendas',         icon: TrendingUp },
  { value: 'preco_asc',  label: 'Menor preço',    icon: ArrowUp },
  { value: 'preco_desc', label: 'Maior preço',    icon: ArrowDown },
]

export default function CatalogPage() {
  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [categoria, setCategoria] = useState('')
  const [ordenar, setOrdenar] = useState<OrdenarPor>('nome')
  const [page, setPage] = useState(1)
  const [showFilters, setShowFilters] = useState(false)
  const debounceRef = useRef<ReturnType<typeof setTimeout>>()

  // Debounce search
  const handleSearchChange = useCallback((value: string) => {
    setSearch(value)
    setPage(1)
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => setDebouncedSearch(value), 350)
  }, [])

  const { data, isLoading, isError } = useQuery({
    queryKey: ['produtos', debouncedSearch, categoria, ordenar, page],
    queryFn: () =>
      listProdutos({ search: debouncedSearch, categoria, ordenar, page, page_size: PAGE_SIZE }),
  })

  const { data: categorias } = useQuery({
    queryKey: ['categorias'],
    queryFn: getCategorias,
    staleTime: Infinity,
  })

  const handleCategoryChange = (cat: string) => {
    setCategoria(cat)
    setPage(1)
    setShowFilters(false)
  }

  const clearFilters = () => {
    setSearch('')
    setDebouncedSearch('')
    setCategoria('')
    setOrdenar('nome')
    setPage(1)
  }

  const hasFilters = debouncedSearch || categoria || ordenar !== 'nome'

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Catálogo de Produtos</h1>
        <p className="text-gray-500 mt-1">
          {data ? (
            <>
              <span className="text-gray-900 font-medium">{data.total}</span> produtos encontrados
            </>
          ) : (
            'Gerenciamento completo do seu estoque'
          )}
        </p>
      </div>

      {/* Search & Filter bar */}
      <div className="flex gap-3 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar produtos..."
            value={search}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="input pl-10 pr-10"
          />
          {search && (
            <button
              onClick={() => handleSearchChange('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-700"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`btn-secondary relative ${categoria ? 'bg-gray-900 text-white' : ''}`}
        >
          <Filter className="w-4 h-4" />
          <span className="hidden sm:inline">Categoria</span>
          {categoria && (
            <span className="absolute -top-1 -right-1 w-2 h-2 bg-black rounded-full" />
          )}
        </button>

        {hasFilters && (
          <button onClick={clearFilters} className="btn-secondary text-red-600">
            <X className="w-4 h-4" />
            <span className="hidden sm:inline">Limpar</span>
          </button>
        )}
      </div>

      {/* Sort bar */}
      <div className="flex items-center gap-2 mb-4">
        <span className="text-sm text-gray-500 flex items-center gap-1.5">
          <ArrowUpDown className="w-3.5 h-3.5" />
          Ordenar:
        </span>
        {SORT_OPTIONS.map(({ value, label, icon: Icon }) => (
          <button
            key={value}
            onClick={() => { setOrdenar(value); setPage(1) }}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium border transition-colors ${
              ordenar === value
                ? 'bg-gray-900 text-white border-black'
                : 'bg-white text-gray-600 border-black hover:bg-champagne-100'
            }`}
          >
            <Icon className="w-3.5 h-3.5" />
            {label}
          </button>
        ))}
      </div>

      {/* Active category badge */}
      {categoria && (
        <div className="flex items-center gap-2 mb-4">
          <span className="text-sm text-gray-500">Filtrando por:</span>
          <span className="badge bg-gray-900 text-white border border-black">
            {formatCategoria(categoria)}
            <button onClick={() => setCategoria('')} className="ml-1.5 hover:text-gray-300">
              <X className="w-3 h-3" />
            </button>
          </span>
        </div>
      )}

      {/* Category panel */}
      {showFilters && (
        <div className="card p-4 mb-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Selecionar Categoria</h3>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => handleCategoryChange('')}
              className={`badge cursor-pointer border transition-colors ${
                !categoria
                  ? 'bg-gray-900 text-white border-black'
                  : 'bg-white text-gray-600 border-black hover:bg-gray-900 hover:text-white'
              }`}
            >
              Todas
            </button>
            {categorias?.map((c) => (
              <button
                key={c.categoria}
                onClick={() => handleCategoryChange(c.categoria)}
                className={`badge cursor-pointer border transition-colors ${
                  categoria === c.categoria
                    ? 'bg-gray-900 text-white border-black'
                    : 'bg-white text-gray-600 border-black hover:bg-gray-900 hover:text-white'
                }`}
              >
                {formatCategoria(c.categoria)}
                <span className="ml-1.5 opacity-50">({c.total_produtos})</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Loading */}
      {isLoading && (
        <div className="flex items-center justify-center py-24">
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="w-8 h-8 text-gray-700 animate-spin" />
            <p className="text-gray-500">Carregando produtos...</p>
          </div>
        </div>
      )}

      {/* Error */}
      {isError && (
        <div className="card p-8 text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-gray-900 mb-1">Erro ao carregar produtos</h3>
          <p className="text-gray-500 text-sm">Verifique se o backend está rodando na porta 8000.</p>
        </div>
      )}

      {/* Empty state */}
      {!isLoading && !isError && data?.items.length === 0 && (
        <div className="card p-12 text-center">
          <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-500 mb-2">Nenhum produto encontrado</h3>
          <p className="text-gray-400 text-sm">
            {hasFilters ? 'Tente ajustar os filtros de busca.' : 'Comece adicionando produtos ao catálogo.'}
          </p>
        </div>
      )}

      {/* Grid */}
      {!isLoading && !isError && data && data.items.length > 0 && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {data.items.map((produto) => (
              <ProductCard key={produto.id_produto} produto={produto} />
            ))}
          </div>

          <Pagination
            page={data.page}
            pages={data.pages}
            total={data.total}
            pageSize={data.page_size}
            onPageChange={setPage}
          />
        </>
      )}
    </div>
  )
}
