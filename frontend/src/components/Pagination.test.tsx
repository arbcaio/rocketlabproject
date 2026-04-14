import { render, screen, fireEvent } from '@testing-library/react'
import Pagination from './Pagination'

const defaultProps = {
  page: 1,
  pages: 3,
  total: 50,
  pageSize: 20,
  onPageChange: vi.fn(),
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('Pagination', () => {
  it('não renderiza nada quando pages é 1', () => {
    const { container } = render(
      <Pagination {...defaultProps} pages={1} total={10} pageSize={10} />
    )
    expect(container).toBeEmptyDOMElement()
  })

  it('não renderiza nada quando pages é 0', () => {
    const { container } = render(
      <Pagination {...defaultProps} pages={0} total={0} />
    )
    expect(container).toBeEmptyDOMElement()
  })

  it('exibe o range de itens da página atual', () => {
    render(<Pagination {...defaultProps} page={1} pages={3} total={50} pageSize={20} />)
    expect(screen.getByText('1–20')).toBeInTheDocument()
    expect(screen.getByText('50')).toBeInTheDocument()
  })

  it('calcula o range corretamente para a última página parcial', () => {
    render(<Pagination {...defaultProps} page={3} pages={3} total={50} pageSize={20} />)
    expect(screen.getByText('41–50')).toBeInTheDocument()
  })

  it('desabilita o botão anterior na primeira página', () => {
    render(<Pagination {...defaultProps} page={1} />)
    const buttons = screen.getAllByRole('button')
    expect(buttons[0]).toBeDisabled()
  })

  it('desabilita o botão próximo na última página', () => {
    render(<Pagination {...defaultProps} page={3} pages={3} />)
    const buttons = screen.getAllByRole('button')
    expect(buttons[buttons.length - 1]).toBeDisabled()
  })

  it('chama onPageChange com page-1 ao clicar em anterior', () => {
    const onPageChange = vi.fn()
    render(<Pagination {...defaultProps} page={2} onPageChange={onPageChange} />)
    const buttons = screen.getAllByRole('button')
    fireEvent.click(buttons[0])
    expect(onPageChange).toHaveBeenCalledWith(1)
  })

  it('chama onPageChange com page+1 ao clicar em próximo', () => {
    const onPageChange = vi.fn()
    render(<Pagination {...defaultProps} page={1} onPageChange={onPageChange} />)
    const buttons = screen.getAllByRole('button')
    fireEvent.click(buttons[buttons.length - 1])
    expect(onPageChange).toHaveBeenCalledWith(2)
  })

  it('exibe todos os números de página quando pages <= 7', () => {
    render(<Pagination {...defaultProps} page={1} pages={5} total={100} pageSize={20} />)
    expect(screen.getByText('1')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
    expect(screen.getByText('5')).toBeInTheDocument()
  })

  it('chama onPageChange ao clicar em um número de página', () => {
    const onPageChange = vi.fn()
    render(<Pagination {...defaultProps} page={1} pages={5} total={100} pageSize={20} onPageChange={onPageChange} />)
    fireEvent.click(screen.getByText('4'))
    expect(onPageChange).toHaveBeenCalledWith(4)
  })

  it('destaca a página atual com bg-gray-900', () => {
    render(<Pagination {...defaultProps} page={2} pages={5} total={100} pageSize={20} />)
    expect(screen.getByText('2')).toHaveClass('bg-gray-900')
  })

  it('não destaca as demais páginas', () => {
    render(<Pagination {...defaultProps} page={2} pages={5} total={100} pageSize={20} />)
    expect(screen.getByText('1')).not.toHaveClass('bg-gray-900')
    expect(screen.getByText('3')).not.toHaveClass('bg-gray-900')
  })

  it('exibe reticências quando há muitas páginas', () => {
    render(<Pagination {...defaultProps} page={5} pages={10} total={200} pageSize={20} />)
    expect(screen.getAllByText('…').length).toBeGreaterThanOrEqual(1)
  })

  it('sempre exibe a primeira e última página em listas longas', () => {
    render(<Pagination {...defaultProps} page={5} pages={10} total={200} pageSize={20} />)
    expect(screen.getByText('1')).toBeInTheDocument()
    expect(screen.getByText('10')).toBeInTheDocument()
  })
})
