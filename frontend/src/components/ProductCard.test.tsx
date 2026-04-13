/**
 * Testes do ProductCard
 *
 * Cobertura:
 *  - Renderização do nome do produto
 *  - Exibição de preço formatado / "Sem preço"
 *  - Exibição de estrelas / "Sem avaliações"
 *  - Contadores de vendas e avaliações
 *  - Formatação de peso (g e kg)
 *  - Formatação de dimensões
 *  - Link correto para /produtos/:id
 */

import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import ProductCard from './ProductCard'
import type { Produto } from '../types'

// Mocks de dependências externas ao componente
vi.mock('../utils/categoryImages', () => ({
  getCategoryImage: () => 'https://example.com/img.jpg',
  formatCategoria: (cat: string) => cat,
}))

vi.mock('./StarRating', () => ({
  default: ({ rating }: { rating: number }) => (
    <span data-testid="star-rating">{rating} estrelas</span>
  ),
}))

const produtoBase: Produto = {
  id_produto: 'prod-001',
  nome_produto: 'Notebook Gamer X',
  categoria_produto: 'informatica',
  peso_produto_gramas: 2500,
  comprimento_centimetros: 38,
  altura_centimetros: 2.5,
  largura_centimetros: 26,
  media_avaliacao: 4.5,
  total_avaliacoes: 120,
  total_vendas: 350,
  preco_medio: 4999.99,
}

function renderCard(produto: Partial<Produto> = {}) {
  return render(
    <MemoryRouter>
      <ProductCard produto={{ ...produtoBase, ...produto }} />
    </MemoryRouter>
  )
}

describe('ProductCard', () => {

  it('exibe o nome do produto', () => {
    renderCard()
    expect(screen.getByText('Notebook Gamer X')).toBeInTheDocument()
  })

  it('exibe o preço médio formatado corretamente', () => {
    renderCard({ preco_medio: 4999.99 })
    expect(screen.getByText(/R\$ 4\.999,99/)).toBeInTheDocument()
  })

  it('exibe "Sem preço" quando preco_medio é null', () => {
    renderCard({ preco_medio: null })
    expect(screen.getByText('Sem preço')).toBeInTheDocument()
  })

  it('exibe o StarRating quando há avaliação', () => {
    renderCard({ media_avaliacao: 4.5 })
    expect(screen.getByTestId('star-rating')).toBeInTheDocument()
    expect(screen.getByTestId('star-rating')).toHaveTextContent('4.5')
  })

  it('exibe "Sem avaliações" quando media_avaliacao é null', () => {
    renderCard({ media_avaliacao: null })
    expect(screen.queryByTestId('star-rating')).not.toBeInTheDocument()
    expect(screen.getByText('Sem avaliações')).toBeInTheDocument()
  })

  it('exibe o contador de vendas', () => {
    renderCard({ total_vendas: 350 })
    expect(screen.getByText(/350.*vendas/)).toBeInTheDocument()
  })

  it('exibe o contador de avaliações', () => {
    renderCard({ total_avaliacoes: 120 })
    expect(screen.getByText(/120.*aval\./)).toBeInTheDocument()
  })

  it('formata peso em gramas corretamente (< 1000 g)', () => {
    renderCard({ peso_produto_gramas: 500 })
    expect(screen.getByText(/500.*g/)).toBeInTheDocument()
  })

  it('formata peso em quilogramas corretamente (>= 1000 g)', () => {
    renderCard({ peso_produto_gramas: 2500 })
    expect(screen.getByText(/2\.5 kg/)).toBeInTheDocument()
  })

  it('oculta peso quando peso_produto_gramas é null', () => {
    renderCard({
      peso_produto_gramas: null,
      comprimento_centimetros: null,
      altura_centimetros: null,
      largura_centimetros: null,
    })
    expect(screen.queryByText(/kg/)).not.toBeInTheDocument()
    expect(screen.queryByText(/ g/)).not.toBeInTheDocument()
  })

  it('exibe dimensões quando todos os valores estão presentes', () => {
    renderCard({ comprimento_centimetros: 38, altura_centimetros: 2.5, largura_centimetros: 26 })
    expect(screen.getByText(/38×2\.5×26 cm/)).toBeInTheDocument()
  })

  it('o link aponta para /produtos/:id', () => {
    renderCard({ id_produto: 'prod-001' })
    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('href', '/produtos/prod-001')
  })
})
