import axios from 'axios'
import type {
  Avaliacao,
  Categoria,
  PaginatedAvaliacoes,
  PaginatedResponse,
  Produto,
  ProdutoCreate,
  ProdutoDetalhe,
  ProdutoUpdate,
} from '../types'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// ── Produtos ──────────────────────────────────────────────────────────────────

export interface ListProdutosParams {
  search?: string
  categoria?: string
  page?: number
  page_size?: number
}

export async function listProdutos(
  params: ListProdutosParams = {}
): Promise<PaginatedResponse<Produto>> {
  const { data } = await api.get<PaginatedResponse<Produto>>('/produtos', { params })
  return data
}

export async function getProduto(id: string): Promise<ProdutoDetalhe> {
  const { data } = await api.get<ProdutoDetalhe>(`/produtos/${id}`)
  return data
}

export async function createProduto(payload: ProdutoCreate): Promise<Produto> {
  const { data } = await api.post<Produto>('/produtos', payload)
  return data
}

export async function updateProduto(id: string, payload: ProdutoUpdate): Promise<Produto> {
  const { data } = await api.put<Produto>(`/produtos/${id}`, payload)
  return data
}

export async function deleteProduto(id: string): Promise<void> {
  await api.delete(`/produtos/${id}`)
}

// ── Avaliações ────────────────────────────────────────────────────────────────

export async function getAvaliacoes(
  id: string,
  params: { page?: number; page_size?: number } = {}
): Promise<PaginatedAvaliacoes> {
  const { data } = await api.get<PaginatedAvaliacoes>(`/produtos/${id}/avaliacoes`, { params })
  return data
}

// ── Categorias ────────────────────────────────────────────────────────────────

export async function getCategorias(): Promise<Categoria[]> {
  const { data } = await api.get<Categoria[]>('/produtos/categorias')
  return data
}
