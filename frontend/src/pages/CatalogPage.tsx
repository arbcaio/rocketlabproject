import { useState, useCallback, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search, Filter, X, Package, AlertCircle, Loader2 } from 'lucide-react'
import { listProdutos, getCategorias } from '../api/produtos'
import ProductCard from '../components/ProductCard'
import Pagination from '../components/Pagination'
import { formatCategoria } from '../utils/categoryImages'

const PAGE_SIZE = 20

export default function CatalogPage() {
  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [categoria, setCategoria] = useState('')
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
    queryKey: ['produtos', debouncedSearch, categoria, page],
    queryFn: () =>
      listProdutos({ search: debouncedSearch, categoria, page, page_size: PAGE_SIZE }),
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
    setPage(1)
  }

  const hasFilters = debouncedSearch || categoria

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-white">Catálogo de Produtos</h1>
        <p className="text-gray-400 mt-1">
          {data ? (
            <>
              <span className="text-white font-medium">{data.total}</span> produtos encontrados
            </>
          ) : (
            'Gerenciamento completo do seu estoque'
          )}
        </p>
      </div>

      {/* Search & Filter bar */}
      <div className="flex gap-3 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
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
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`btn-secondary relative ${categoria ? 'border-brand-500 text-brand-400' : ''}`}
        >
          <Filter className="w-4 h-4" />
          <span className="hidden sm:inline">Categoria</span>
          {categoria && (
            <span className="absolute -top-1 -right-1 w-2 h-2 bg-brand-500 rounded-full" />
          )}
        </button>

        {hasFilters && (
          <button onClick={clearFilters} className="btn-secondary text-red-400 border-red-900/50">
            <X className="w-4 h-4" />
            <span className="hidden sm:inline">Limpar</span>
          </button>
        )}
      </div>

      {/* Active category badge */}
      {categoria && (
        <div className="flex items-center gap-2 mb-4">
          <span className="text-sm text-gray-400">Filtrando por:</span>
          <span className="badge bg-brand-900/60 text-brand-300 border border-brand-700/50">
            {formatCategoria(categoria)}
            <button
              onClick={() => setCategoria('')}
              className="ml-1.5 hover:text-brand-100"
            >
              <X className="w-3 h-3" />
            </button>
          </span>
        </div>
      )}

      {/* Category panel */}
      {showFilters && (
        <div className="card p-4 mb-4 animate-in fade-in slide-in-from-top-2">
          <h3 className="text-sm font-semibold text-gray-300 mb-3">Selecionar Categoria</h3>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => handleCategoryChange('')}
              className={`badge cursor-pointer transition-colors ${
                !categoria
                  ? 'bg-brand-700 text-brand-100'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-gray-200'
              }`}
            >
              Todas
            </button>
            {categorias?.map((c) => (
              <button
                key={c.categoria}
                onClick={() => handleCategoryChange(c.categoria)}
                className={`badge cursor-pointer transition-colors ${
                  categoria === c.categoria
                    ? 'bg-brand-700 text-brand-100'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-gray-200'
                }`}
              >
                {formatCategoria(c.categoria)}
                <span className="ml-1.5 opacity-60">({c.total_produtos})</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Loading */}
      {isLoading && (
        <div className="flex items-center justify-center py-24">
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="w-8 h-8 text-brand-500 animate-spin" />
            <p className="text-gray-400">Carregando produtos...</p>
          </div>
        </div>
      )}

      {/* Error */}
      {isError && (
        <div className="card p-8 text-center">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-white mb-1">Erro ao carregar produtos</h3>
          <p className="text-gray-400 text-sm">Verifique se o backend está rodando na porta 8000.</p>
        </div>
      )}

      {/* Empty state */}
      {!isLoading && !isError && data?.items.length === 0 && (
        <div className="card p-12 text-center">
          <Package className="w-16 h-16 text-gray-700 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-400 mb-2">Nenhum produto encontrado</h3>
          <p className="text-gray-500 text-sm">
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
