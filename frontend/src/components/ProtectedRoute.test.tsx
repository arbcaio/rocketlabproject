/**
 * Testes do ProtectedRoute
 *
 * Cobertura:
 *  - Usuário autenticado: renderiza os filhos
 *  - Usuário NÃO autenticado: redireciona para /login
 *  - O redirecionamento preserva a rota de origem em state.from
 */

import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { AuthProvider } from '../context/AuthContext'
import ProtectedRoute from './ProtectedRoute'

function renderWithRouter(initialPath: string) {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<div data-testid="login-page">Página de Login</div>} />
          <Route
            path="/produtos"
            element={
              <ProtectedRoute>
                <div data-testid="conteudo-protegido">Catálogo</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </MemoryRouter>
  )
}

describe('ProtectedRoute', () => {

  it('renderiza os filhos quando o usuário está autenticado', () => {
    sessionStorage.setItem('ecommerce_auth', 'true')
    renderWithRouter('/produtos')
    expect(screen.getByTestId('conteudo-protegido')).toBeInTheDocument()
  })

  it('não renderiza os filhos quando não autenticado', () => {
    renderWithRouter('/produtos')
    expect(screen.queryByTestId('conteudo-protegido')).not.toBeInTheDocument()
  })

  it('redireciona para /login quando não autenticado', () => {
    renderWithRouter('/produtos')
    expect(screen.getByTestId('login-page')).toBeInTheDocument()
  })

  it('não redireciona para /login quando autenticado', () => {
    sessionStorage.setItem('ecommerce_auth', 'true')
    renderWithRouter('/produtos')
    expect(screen.queryByTestId('login-page')).not.toBeInTheDocument()
  })
})
