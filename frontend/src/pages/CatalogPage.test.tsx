import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import CatalogPage from './CatalogPage'

// ── Mocks ────────────────────────────────────────────────────────────────────

const mockListProdutos = vi.hoisted(() => vi.fn())
const mockGetCategorias = vi.hoisted(() => vi.fn())

vi.mock('../api/produtos', () => ({
  listProdutos: mockListProdutos,
  getCategorias: mockGetCategorias,
}))

vi.mock('../components/ProductCard', () => ({
  default: ({ produto }: { produto: { id_produto: string; nome_produto: string } }) => (
    <div data-testid="product-card">{produto.nome_produto}</div>
  ),
}))

vi.mock('../components/Pagination', () => ({
  default: ({
    page,
    onPageChange,
  }: {
    page: number
    pages: number
    onPageChange: (p: number) => void
  }) => (
    <div data-testid="pagination">
      <button onClick={() => onPageChange(page + 1)}>Próxima página</button>
    </div>
  ),
}))

vi.mock('../utils/categoryImages', () => ({
  formatCategoria: (cat: string) => cat.toUpperCase(),
}))

// ── Helpers ──────────────────────────────────────────────────────────────────

function makeClient() {
  return new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
}

async function renderPage() {
  render(
    <QueryClientProvider client={makeClient()}>
      <CatalogPage />
    </QueryClientProvider>
  )
  // Flush React Query's initial async queries
  await act(async () => {})
}

const mockProduto = {
  id_produto: 'prod-1',
  nome_produto: 'Produto Teste',
  preco_BRL: 149.9,
  avaliacao_media: 4.2,
  total_vendas: 15,
  total_avaliacoes: 8,
  peso_g: 300,
  categoria: 'eletronicos',
}

const mockData = {
  items: [mockProduto],
  total: 1,
  page: 1,
  pages: 1,
  page_size: 20,
}

const mockCategorias = [
  { categoria: 'eletronicos', total_produtos: 5 },
  { categoria: 'livros', total_produtos: 3 },
]

// ── Setup ────────────────────────────────────────────────────────────────────

beforeEach(() => {
  vi.clearAllMocks()
  mockListProdutos.mockResolvedValue(mockData)
  mockGetCategorias.mockResolvedValue(mockCategorias)
})

afterEach(() => {
  // Garante que fake timers nunca vazam entre testes
  vi.useRealTimers()
})

// ── Tests ────────────────────────────────────────────────────────────────────

describe('CatalogPage', () => {
  describe('estados de carregamento', () => {
    it('exibe spinner enquanto os dados carregam', () => {
      mockListProdutos.mockImplementation(() => new Promise(() => {}))
      render(
        <QueryClientProvider client={makeClient()}>
          <CatalogPage />
        </QueryClientProvider>
      )
      expect(screen.getByText('Carregando produtos...')).toBeInTheDocument()
    })

    it('exibe os produtos após o carregamento', async () => {
      await renderPage()
      await waitFor(() => expect(screen.getByText('Produto Teste')).toBeInTheDocument())
    })

    it('exibe a contagem total de produtos encontrados', async () => {
      await renderPage()
      await waitFor(() =>
        expect(screen.getByText(/produtos encontrados/)).toBeInTheDocument()
      )
    })

    it('exibe estado vazio quando não há produtos', async () => {
      mockListProdutos.mockResolvedValue({
        items: [],
        total: 0,
        page: 1,
        pages: 0,
        page_size: 20,
      })
      await renderPage()
      await waitFor(() => expect(screen.getByText('Nenhum produto encontrado')).toBeInTheDocument())
    })

    it('exibe estado de erro quando a API falha', async () => {
      mockListProdutos.mockRejectedValue(new Error('network error'))
      await renderPage()
      await waitFor(() =>
        expect(screen.getByText('Erro ao carregar produtos')).toBeInTheDocument()
      )
    })
  })

  describe('busca', () => {
    it('renderiza o campo de busca', async () => {
      await renderPage()
      expect(screen.getByPlaceholderText('Buscar produtos...')).toBeInTheDocument()
    })

    it('atualiza o valor do input ao digitar', async () => {
      await renderPage()
      const input = screen.getByPlaceholderText('Buscar produtos...')
      fireEvent.change(input, { target: { value: 'notebook' } })
      expect(input).toHaveValue('notebook')
    })

    it('exibe botão X para limpar a busca ao digitar', async () => {
      await renderPage()
      const input = screen.getByPlaceholderText('Buscar produtos...')
      fireEvent.change(input, { target: { value: 'notebook' } })
      const clearBtn = input.parentElement!.querySelector('button')
      expect(clearBtn).toBeInTheDocument()
    })

    it('limpa o campo ao clicar no botão X', async () => {
      await renderPage()
      const input = screen.getByPlaceholderText('Buscar produtos...')
      fireEvent.change(input, { target: { value: 'notebook' } })
      const clearBtn = input.parentElement!.querySelector('button')!
      fireEvent.click(clearBtn)
      expect(input).toHaveValue('')
    })

    it('chama listProdutos com termo de busca após o debounce', async () => {
      vi.useFakeTimers()

      render(
        <QueryClientProvider client={makeClient()}>
          <CatalogPage />
        </QueryClientProvider>
      )

      // Flush carregamento inicial
      await act(async () => { vi.runAllTimers() })

      const input = screen.getByPlaceholderText('Buscar produtos...')
      fireEvent.change(input, { target: { value: 'notebook' } })

      // Avança o debounce de 350ms
      await act(async () => { vi.advanceTimersByTime(400) })

      vi.useRealTimers()

      await waitFor(() => {
        const lastArgs = mockListProdutos.mock.calls.at(-1)?.[0]
        expect(lastArgs?.search).toBe('notebook')
      })
    })
  })

  describe('ordenação', () => {
    it('exibe os 5 botões de ordenação', async () => {
      await renderPage()
      expect(screen.getByText('Nome')).toBeInTheDocument()
      expect(screen.getByText('Avaliação')).toBeInTheDocument()
      expect(screen.getByText('Vendas')).toBeInTheDocument()
      expect(screen.getByText('Menor preço')).toBeInTheDocument()
      expect(screen.getByText('Maior preço')).toBeInTheDocument()
    })

    it('"Nome" é o botão ativo por padrão', async () => {
      await renderPage()
      expect(screen.getByText('Nome')).toHaveClass('bg-gray-900')
    })

    it('altera o botão ativo ao clicar em outra ordenação', async () => {
      await renderPage()
      fireEvent.click(screen.getByText('Vendas'))
      expect(screen.getByText('Vendas')).toHaveClass('bg-gray-900')
      expect(screen.getByText('Nome')).not.toHaveClass('bg-gray-900')
    })

    it('chama listProdutos com o novo ordenar ao trocar', async () => {
      await renderPage()
      fireEvent.click(screen.getByText('Vendas'))
      await waitFor(() => {
        const lastArgs = mockListProdutos.mock.calls.at(-1)?.[0]
        expect(lastArgs?.ordenar).toBe('vendas')
      })
    })
  })

  describe('filtros por categoria', () => {
    it('exibe botão de filtro por categoria', async () => {
      await renderPage()
      expect(screen.getByText('Categoria')).toBeInTheDocument()
    })

    it('abre o painel de categorias ao clicar em Categoria', async () => {
      await renderPage()
      fireEvent.click(screen.getByText('Categoria'))
      expect(screen.getByText('Selecionar Categorias')).toBeInTheDocument()
    })

    it('exibe as categorias disponíveis no painel', async () => {
      await renderPage()
      fireEvent.click(screen.getByText('Categoria'))
      await waitFor(() => {
        expect(screen.getByText(/ELETRONICOS/)).toBeInTheDocument()
        expect(screen.getByText(/LIVROS/)).toBeInTheDocument()
      })
    })

    it('fecha o painel ao clicar em Categoria novamente', async () => {
      await renderPage()
      const btn = screen.getByText('Categoria')
      fireEvent.click(btn)
      expect(screen.getByText('Selecionar Categorias')).toBeInTheDocument()
      fireEvent.click(btn)
      expect(screen.queryByText('Selecionar Categorias')).not.toBeInTheDocument()
    })

    it('exibe badge de categoria ativa após seleção', async () => {
      await renderPage()
      fireEvent.click(screen.getByText('Categoria'))
      await waitFor(() => screen.getByText(/ELETRONICOS/))
      fireEvent.click(screen.getByText(/ELETRONICOS/))
      expect(screen.getByText('Filtrando por:')).toBeInTheDocument()
    })

    it('exibe botão Limpar quando há filtros ativos', async () => {
      await renderPage()
      fireEvent.click(screen.getByText('Categoria'))
      await waitFor(() => screen.getByText(/ELETRONICOS/))
      fireEvent.click(screen.getByText(/ELETRONICOS/))
      expect(screen.getByText('Limpar')).toBeInTheDocument()
    })

    it('remove os badges ao clicar em Limpar', async () => {
      await renderPage()
      fireEvent.click(screen.getByText('Categoria'))
      await waitFor(() => screen.getByText(/ELETRONICOS/))
      fireEvent.click(screen.getByText(/ELETRONICOS/))
      fireEvent.click(screen.getByText('Limpar'))
      expect(screen.queryByText('Filtrando por:')).not.toBeInTheDocument()
    })
  })
})
