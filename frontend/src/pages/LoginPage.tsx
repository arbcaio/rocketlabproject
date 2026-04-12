import { useState, FormEvent } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Loader2, AlertCircle, Eye, EyeOff, LogIn } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const from = (location.state as { from?: string })?.from ?? '/produtos'

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    setError('')

    if (!username.trim() || !password) {
      setError('Preencha usuário e senha.')
      return
    }

    setLoading(true)
    // Pequeno delay para simular verificação
    setTimeout(() => {
      const ok = login(username.trim(), password)
      if (ok) {
        navigate(from, { replace: true })
      } else {
        setError('Usuário ou senha incorretos.')
        setLoading(false)
      }
    }, 400)
  }

  return (
    <div className="min-h-screen bg-champagne-100 flex items-center justify-center px-4">
      <div className="w-full max-w-sm">

        {/* Logo / marca */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 border border-black bg-white flex items-center justify-center mb-4 overflow-hidden">
            <img
              src="/icon/OIP-1038731913.jpg"
              alt="E-Commerce"
              className="w-full h-full object-cover"
              onError={(e) => {
                ;(e.currentTarget as HTMLImageElement).style.display = 'none'
              }}
            />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 tracking-tight">E-Commerce</h1>
          <p className="text-sm text-gray-500 mt-1">Faça login para continuar</p>
        </div>

        {/* Card de login */}
        <div className="card p-6">
          <form onSubmit={handleSubmit} className="space-y-4" noValidate>

            {/* Erro */}
            {error && (
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-300 text-red-700 text-sm">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                {error}
              </div>
            )}

            {/* Usuário */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Usuário
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => {
                  setUsername(e.target.value)
                  if (error) setError('')
                }}
                placeholder="rocket"
                autoComplete="username"
                autoFocus
                className="input"
                disabled={loading}
              />
            </div>

            {/* Senha */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Senha
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value)
                    if (error) setError('')
                  }}
                  placeholder="••••••••••••"
                  autoComplete="current-password"
                  className="input pr-10"
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute inset-y-0 right-0 flex items-center px-3 text-gray-400 hover:text-gray-700 transition-colors"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Botão */}
            <button
              type="submit"
              className="btn-primary w-full justify-center mt-2"
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Entrando...
                </>
              ) : (
                <>
                  <LogIn className="w-4 h-4" />
                  Entrar
                </>
              )}
            </button>
          </form>
        </div>

        <p className="text-center text-xs text-gray-400 mt-6">
          © {new Date().getFullYear()} E-Commerce Management
        </p>
      </div>
    </div>
  )
}
