/**
 * Testes da LoginPage
 *
 * Cobertura:
 *  - Renderização (inputs, box de credenciais provisórias, botão)
 *  - Validação de campos vazios
 *  - Erro com credenciais erradas (após timeout de 400ms)
 *  - Login bem-sucedido: navega para /produtos
 *  - Estado de loading durante o login
 *  - Toggle mostrar/ocultar senha
 */

import { render, screen, fireEvent, act, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AuthProvider } from '../context/AuthContext'
import LoginPage from './LoginPage'

// Mockar useNavigate para capturar chamadas de navegação
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual('react-router-dom')),
  useNavigate: () => mockNavigate,
  useLocation: () => ({ state: null, pathname: '/login' }),
}))

function renderLogin() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <LoginPage />
      </AuthProvider>
    </MemoryRouter>
  )
}

describe('LoginPage', () => {

  beforeEach(() => {
    mockNavigate.mockReset()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  // ── Renderização ────────────────────────────────────────────────────────────

  it('renderiza o campo de usuário', () => {
    renderLogin()
    expect(screen.getByPlaceholderText('rocket')).toBeInTheDocument()
  })

  it('renderiza o campo de senha', () => {
    renderLogin()
    expect(screen.getByPlaceholderText('••••••••••••')).toBeInTheDocument()
  })

  it('exibe o box de acesso provisório com as credenciais', () => {
    renderLogin()
    expect(screen.getByText('Acesso provisório')).toBeInTheDocument()
    expect(screen.getByText('rocket')).toBeInTheDocument()
    expect(screen.getByText('equipeRocket@1')).toBeInTheDocument()
  })

  it('renderiza o botão Entrar', () => {
    renderLogin()
    expect(screen.getByRole('button', { name: /entrar/i })).toBeInTheDocument()
  })

  // ── Validação ───────────────────────────────────────────────────────────────

  it('exibe erro ao submeter com campos vazios', () => {
    renderLogin()
    fireEvent.click(screen.getByRole('button', { name: /entrar/i }))
    expect(screen.getByText('Preencha usuário e senha.')).toBeInTheDocument()
  })

  it('não aciona o timeout com campos vazios (retorno imediato)', () => {
    renderLogin()
    fireEvent.click(screen.getByRole('button', { name: /entrar/i }))
    // Loading NÃO deve aparecer pois a validação retorna antes do setTimeout
    expect(screen.queryByText('Entrando...')).not.toBeInTheDocument()
  })

  // ── Credenciais erradas ─────────────────────────────────────────────────────

  it('exibe erro após 400ms com credenciais erradas', async () => {
    renderLogin()
    fireEvent.change(screen.getByPlaceholderText('rocket'), { target: { value: 'errado' } })
    fireEvent.change(screen.getByPlaceholderText('••••••••••••'), { target: { value: 'senha_errada' } })
    fireEvent.click(screen.getByRole('button', { name: /entrar/i }))

    // Antes do timeout: mostra "Entrando..."
    expect(screen.getByText('Entrando...')).toBeInTheDocument()

    await act(async () => { vi.advanceTimersByTime(400) })

    expect(screen.getByText('Usuário ou senha incorretos.')).toBeInTheDocument()
  })

  // ── Login bem-sucedido ──────────────────────────────────────────────────────

  it('navega para /produtos após login bem-sucedido', async () => {
    renderLogin()
    fireEvent.change(screen.getByPlaceholderText('rocket'), { target: { value: 'rocket' } })
    fireEvent.change(screen.getByPlaceholderText('••••••••••••'), { target: { value: 'equipeRocket@1' } })
    fireEvent.click(screen.getByRole('button', { name: /entrar/i }))

    await act(async () => { vi.advanceTimersByTime(400) })

    expect(mockNavigate).toHaveBeenCalledWith('/produtos', { replace: true })
  })

  // ── Toggle senha ────────────────────────────────────────────────────────────

  it('alterna visibilidade da senha ao clicar no botão olho', () => {
    renderLogin()
    const senhaInput = screen.getByPlaceholderText('••••••••••••')
    expect(senhaInput).toHaveAttribute('type', 'password')

    // Clica no botão de toggle (único button type="button" na página)
    const toggleBtn = screen.getByRole('button', { name: '' })
    fireEvent.click(toggleBtn)

    expect(senhaInput).toHaveAttribute('type', 'text')
  })

  it('limpa o erro ao digitar no campo de usuário', async () => {
    renderLogin()
    fireEvent.click(screen.getByRole('button', { name: /entrar/i }))
    expect(screen.getByText('Preencha usuário e senha.')).toBeInTheDocument()

    fireEvent.change(screen.getByPlaceholderText('rocket'), { target: { value: 'a' } })
    expect(screen.queryByText('Preencha usuário e senha.')).not.toBeInTheDocument()
  })
})
