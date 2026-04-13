import { render, screen } from '@testing-library/react'
import StarRating from './StarRating'

describe('StarRating', () => {
  it('exibe "Sem avaliações" quando rating é null', () => {
    render(<StarRating rating={null} />)
    expect(screen.getByText('Sem avaliações')).toBeInTheDocument()
  })

  it('não renderiza estrelas quando rating é null', () => {
    const { container } = render(<StarRating rating={null} />)
    expect(container.querySelectorAll('svg')).toHaveLength(0)
  })

  it('renderiza 5 estrelas por padrão', () => {
    const { container } = render(<StarRating rating={3} />)
    expect(container.querySelectorAll('svg')).toHaveLength(5)
  })

  it('respeita maxRating customizado', () => {
    const { container } = render(<StarRating rating={2} maxRating={3} />)
    expect(container.querySelectorAll('svg')).toHaveLength(3)
  })

  it('exibe o valor numérico com showValue=true (padrão)', () => {
    render(<StarRating rating={4} />)
    expect(screen.getByText('4.0')).toBeInTheDocument()
  })

  it('formata o valor com uma casa decimal', () => {
    render(<StarRating rating={3.7} />)
    expect(screen.getByText('3.7')).toBeInTheDocument()
  })

  it('não exibe o valor numérico com showValue=false', () => {
    render(<StarRating rating={4} showValue={false} />)
    expect(screen.queryByText('4.0')).not.toBeInTheDocument()
  })

  it('não exibe "Sem avaliações" quando rating é um número válido', () => {
    render(<StarRating rating={1} />)
    expect(screen.queryByText('Sem avaliações')).not.toBeInTheDocument()
  })
})
