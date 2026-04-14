/**
 * Testes do AuthContext
 *
 * Cobertura:
 *  - Estado inicial (sessionStorage vazio vs. preenchido)
 *  - login com credenciais corretas / erradas
 *  - logout
 *  - useAuth fora do provider lança erro
 */

import { render, screen, act } from '@testing-library/react'
import { AuthProvider, useAuth } from './AuthContext'

// Componente auxiliar que expõe o contexto na UI
function AuthConsumer() {
  const { isAuthenticated, login, logout } = useAuth()
  return (
    <div>
      <span data-testid="status">{isAuthenticated ? 'autenticado' : 'não autenticado'}</span>
      <button onClick={() => login('rocket', 'equipeRocket@1')}>login-correto</button>
      <button onClick={() => login('rocket', 'errada')}>login-errado</button>
      <button onClick={logout}>logout</button>
    </div>
  )
}

function renderAuth() {
  return render(
    <AuthProvider>
      <AuthConsumer />
    </AuthProvider>
  )
}

describe('AuthContext', () => {

  it('começa como não autenticado quando sessionStorage está vazio', () => {
    renderAuth()
    expect(screen.getByTestId('status')).toHaveTextContent('não autenticado')
  })

  it('começa como autenticado quando sessionStorage contém a flag', () => {
    sessionStorage.setItem('ecommerce_auth', 'true')
    renderAuth()
    expect(screen.getByTestId('status')).toHaveTextContent('autenticado')
  })

  it('login com credenciais corretas retorna true e autentica', () => {
    renderAuth()
    act(() => { screen.getByText('login-correto').click() })
    expect(screen.getByTestId('status')).toHaveTextContent('autenticado')
  })

  it('login correto persiste no sessionStorage', () => {
    renderAuth()
    act(() => { screen.getByText('login-correto').click() })
    expect(sessionStorage.getItem('ecommerce_auth')).toBe('true')
  })

  it('login com senha errada NÃO autentica', () => {
    renderAuth()
    act(() => { screen.getByText('login-errado').click() })
    expect(screen.getByTestId('status')).toHaveTextContent('não autenticado')
  })

  it('login com senha errada NÃO grava no sessionStorage', () => {
    renderAuth()
    act(() => { screen.getByText('login-errado').click() })
    expect(sessionStorage.getItem('ecommerce_auth')).toBeNull()
  })

  it('logout remove autenticação', () => {
    sessionStorage.setItem('ecommerce_auth', 'true')
    renderAuth()
    act(() => { screen.getByText('logout').click() })
    expect(screen.getByTestId('status')).toHaveTextContent('não autenticado')
  })

  it('logout remove a flag do sessionStorage', () => {
    sessionStorage.setItem('ecommerce_auth', 'true')
    renderAuth()
    act(() => { screen.getByText('logout').click() })
    expect(sessionStorage.getItem('ecommerce_auth')).toBeNull()
  })

  it('useAuth fora do AuthProvider lança erro', () => {
    // Suprimir o console.error do React durante o teste de erro intencional
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {})
    expect(() => render(<AuthConsumer />)).toThrow(
      'useAuth deve ser usado dentro de AuthProvider'
    )
    spy.mockRestore()
  })
})
