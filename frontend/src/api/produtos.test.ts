/**
 * Testes de contrato da API de Produtos
 *
 * Cobertura:
 *  - listProdutos monta URL e params corretamente
 *    (busca, categorias únicas, múltiplas categorias, ordenar, paginação)
 *  - getCategorias chama o endpoint correto
 *  - getProduto chama o endpoint correto
 *  - createProduto faz POST com o payload
 *  - deleteProduto faz DELETE no endpoint correto
 */

// Funções mock elevadas antes do vi.mock para ficarem disponíveis no factory
const mockGet    = vi.hoisted(() => vi.fn())
const mockPost   = vi.hoisted(() => vi.fn())
const mockPut    = vi.hoisted(() => vi.fn())
const mockDelete = vi.hoisted(() => vi.fn())

vi.mock('axios', () => ({
  default: {
    create: () => ({
      get:    mockGet,
      post:   mockPost,
      put:    mockPut,
      delete: mockDelete,
    }),
  },
}))

import {
  listProdutos,
  getProduto,
  getCategorias,
  createProduto,
  deleteProduto,
} from './produtos'

beforeEach(() => {
  vi.clearAllMocks()
  mockGet.mockResolvedValue({ data: {} })
  mockPost.mockResolvedValue({ data: {} })
  mockDelete.mockResolvedValue({ data: undefined })
})

describe('API de Produtos', () => {

  describe('listProdutos', () => {

    it('chama /produtos sem parâmetros', async () => {
      await listProdutos()
      expect(mockGet).toHaveBeenCalledWith('/produtos', { params: {} })
    })

    it('passa o parâmetro search', async () => {
      await listProdutos({ search: 'notebook' })
      const params = mockGet.mock.calls[0][1].params
      expect(params.search).toBe('notebook')
    })

    it('passa uma única categoria sem join', async () => {
      await listProdutos({ categorias: ['eletronicos'] })
      const params = mockGet.mock.calls[0][1].params
      expect(params.categoria).toBe('eletronicos')
    })

    it('junta múltiplas categorias com vírgula', async () => {
      await listProdutos({ categorias: ['eletronicos', 'livros', 'esportes'] })
      const params = mockGet.mock.calls[0][1].params
      expect(params.categoria).toBe('eletronicos,livros,esportes')
    })

    it('não envia "categoria" quando o array está vazio', async () => {
      await listProdutos({ categorias: [] })
      const params = mockGet.mock.calls[0][1].params
      expect(params.categoria).toBeUndefined()
    })

    it('passa o parâmetro ordenar', async () => {
      await listProdutos({ ordenar: 'avaliacao' })
      const params = mockGet.mock.calls[0][1].params
      expect(params.ordenar).toBe('avaliacao')
    })

    it('passa os parâmetros de paginação', async () => {
      await listProdutos({ page: 2, page_size: 10 })
      const params = mockGet.mock.calls[0][1].params
      expect(params.page).toBe(2)
      expect(params.page_size).toBe(10)
    })
  })

  describe('getCategorias', () => {
    it('chama /produtos/categorias', async () => {
      await getCategorias()
      expect(mockGet).toHaveBeenCalledWith('/produtos/categorias')
    })
  })

  describe('getProduto', () => {
    it('chama /produtos/:id com o id correto', async () => {
      await getProduto('abc123')
      expect(mockGet).toHaveBeenCalledWith('/produtos/abc123')
    })
  })

  describe('createProduto', () => {
    it('faz POST para /produtos com o payload', async () => {
      const payload = { nome_produto: 'Teclado', categoria_produto: 'perifericos' }
      await createProduto(payload)
      expect(mockPost).toHaveBeenCalledWith('/produtos', payload)
    })
  })

  describe('deleteProduto', () => {
    it('faz DELETE para /produtos/:id', async () => {
      await deleteProduto('xyz789')
      expect(mockDelete).toHaveBeenCalledWith('/produtos/xyz789')
    })
  })
})
