import { ChevronLeft, ChevronRight } from 'lucide-react'

interface PaginationProps {
  page: number
  pages: number
  total: number
  pageSize: number
  onPageChange: (page: number) => void
}

export default function Pagination({
  page,
  pages,
  total,
  pageSize,
  onPageChange,
}: PaginationProps) {
  if (pages <= 1) return null

  const start = (page - 1) * pageSize + 1
  const end = Math.min(page * pageSize, total)

  const getPages = () => {
    const range: (number | '...')[] = []
    if (pages <= 7) {
      return Array.from({ length: pages }, (_, i) => i + 1)
    }
    range.push(1)
    if (page > 3) range.push('...')
    for (let i = Math.max(2, page - 1); i <= Math.min(pages - 1, page + 1); i++) {
      range.push(i)
    }
    if (page < pages - 2) range.push('...')
    range.push(pages)
    return range
  }

  return (
    <div className="flex items-center justify-between mt-6">
      <p className="text-sm text-gray-500">
        Mostrando <span className="text-gray-900 font-medium">{start}–{end}</span> de{' '}
        <span className="text-gray-900 font-medium">{total}</span> produtos
      </p>

      <div className="flex items-center gap-1">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page === 1}
          className="p-1.5 border border-black text-gray-600 hover:bg-gray-900 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>

        {getPages().map((p, i) =>
          p === '...' ? (
            <span key={`ellipsis-${i}`} className="px-2 text-gray-400">
              …
            </span>
          ) : (
            <button
              key={p}
              onClick={() => onPageChange(p as number)}
              className={`w-8 h-8 text-sm font-medium border transition-colors
                ${p === page
                  ? 'bg-gray-900 text-white border-black'
                  : 'bg-white text-gray-600 border-black hover:bg-gray-900 hover:text-white'
                }`}
            >
              {p}
            </button>
          )
        )}

        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page === pages}
          className="p-1.5 border border-black text-gray-600 hover:bg-gray-900 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  )
}
