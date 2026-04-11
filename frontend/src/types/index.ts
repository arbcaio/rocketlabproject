export interface Produto {
  id_produto: string
  nome_produto: string
  categoria_produto: string
  peso_produto_gramas: number | null
  comprimento_centimetros: number | null
  altura_centimetros: number | null
  largura_centimetros: number | null
}

export interface ProdutoDetalhe extends Produto {
  media_avaliacao: number | null
  total_avaliacoes: number
  total_vendas: number
  receita_total: number
  preco_medio: number | null
}

export interface ProdutoCreate {
  nome_produto: string
  categoria_produto: string
  peso_produto_gramas?: number | null
  comprimento_centimetros?: number | null
  altura_centimetros?: number | null
  largura_centimetros?: number | null
}

export type ProdutoUpdate = Partial<ProdutoCreate>

export interface Avaliacao {
  id_avaliacao: string
  avaliacao: number
  titulo_comentario: string | null
  comentario: string | null
  data_comentario: string | null
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface PaginatedAvaliacoes extends PaginatedResponse<Avaliacao> {
  media_avaliacao: number | null
}

export interface Categoria {
  categoria: string
  total_produtos: number
}
