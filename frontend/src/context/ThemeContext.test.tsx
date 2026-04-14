/**
 * Testes do ThemeContext
 *
 * Cobertura:
 *  - Leitura do tema salvo no localStorage
 *  - Fallback para 'light' quando não há preferência
 *  - Fallback para preferência do sistema (prefers-color-scheme)
 *  - toggleTheme alterna entre light ↔ dark
 *  - Aplica/remove classe 'dark' no <html>
 *  - Persiste o tema no localStorage
 *  - useTheme fora do provider lança erro
 */

import { render, screen, act } from '@testing-library/react'
import { ThemeProvider, useTheme } from './ThemeContext'

function ThemeConsumer() {
  const { theme, toggleTheme } = useTheme()
  return (
    <div>
      <span data-testid="tema">{theme}</span>
      <button onClick={toggleTheme}>toggle</button>
    </div>
  )
}

function renderTheme() {
  return render(
    <ThemeProvider>
      <ThemeConsumer />
    </ThemeProvider>
  )
}

describe('ThemeContext', () => {

  it('lê o tema "light" salvo no localStorage', () => {
    localStorage.setItem('ecommerce_theme', 'light')
    renderTheme()
    expect(screen.getByTestId('tema')).toHaveTextContent('light')
  })

  it('lê o tema "dark" salvo no localStorage', () => {
    localStorage.setItem('ecommerce_theme', 'dark')
    renderTheme()
    expect(screen.getByTestId('tema')).toHaveTextContent('dark')
  })

  it('usa "light" como padrão quando localStorage está vazio e sistema é light', () => {
    // matchMedia já retorna matches: false por padrão no setup
    renderTheme()
    expect(screen.getByTestId('tema')).toHaveTextContent('light')
  })

  it('usa "dark" quando sistema prefere dark e localStorage está vazio', () => {
    vi.mocked(window.matchMedia).mockReturnValueOnce({
      matches: true, media: '(prefers-color-scheme: dark)',
      onchange: null, addListener: vi.fn(), removeListener: vi.fn(),
      addEventListener: vi.fn(), removeEventListener: vi.fn(), dispatchEvent: vi.fn(),
    } as unknown as MediaQueryList)
    renderTheme()
    expect(screen.getByTestId('tema')).toHaveTextContent('dark')
  })

  it('toggleTheme alterna de light para dark', () => {
    localStorage.setItem('ecommerce_theme', 'light')
    renderTheme()
    act(() => { screen.getByText('toggle').click() })
    expect(screen.getByTestId('tema')).toHaveTextContent('dark')
  })

  it('toggleTheme alterna de dark para light', () => {
    localStorage.setItem('ecommerce_theme', 'dark')
    renderTheme()
    act(() => { screen.getByText('toggle').click() })
    expect(screen.getByTestId('tema')).toHaveTextContent('light')
  })

  it('adiciona classe "dark" ao documentElement quando tema é dark', () => {
    localStorage.setItem('ecommerce_theme', 'dark')
    renderTheme()
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('remove classe "dark" do documentElement quando tema é light', () => {
    // Garante que a classe estava antes
    document.documentElement.classList.add('dark')
    localStorage.setItem('ecommerce_theme', 'light')
    renderTheme()
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })

  it('persiste o tema no localStorage ao alternar', () => {
    localStorage.setItem('ecommerce_theme', 'light')
    renderTheme()
    act(() => { screen.getByText('toggle').click() })
    expect(localStorage.getItem('ecommerce_theme')).toBe('dark')
  })

  it('useTheme fora do ThemeProvider lança erro', () => {
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {})
    expect(() => render(<ThemeConsumer />)).toThrow(
      'useTheme deve ser usado dentro de ThemeProvider'
    )
    spy.mockRestore()
  })
})
