import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Plus, BarChart3, LogOut } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const navigate = useNavigate()
  const { logout } = useAuth()

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="min-h-screen flex flex-col bg-champagne-100">
      {/* Navbar */}
      <header className="sticky top-0 z-50 bg-white border-b border-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/produtos" className="flex items-center gap-3 group">
              <img
                src="/icon/OIP-1038731913.jpg"
                alt="E-Commerce"
                className="w-9 h-9 object-contain"
              />
              <div>
                <span className="text-lg font-bold text-gray-900 tracking-tight">E-Commerce</span>
                <span className="text-xs text-gray-500 block -mt-1">Painel do Gerente</span>
              </div>
            </Link>

            <nav className="flex items-center gap-1">
              <Link
                to="/produtos"
                className={`flex items-center gap-2 px-3 py-2 text-sm font-medium border transition-colors
                  ${location.pathname === '/produtos'
                    ? 'bg-gray-900 text-white border-black'
                    : 'bg-white text-gray-600 border-transparent hover:border-black hover:text-gray-900'
                  }`}
              >
                <BarChart3 className="w-4 h-4" />
                <span className="hidden sm:inline">Catálogo</span>
              </Link>

              <Link
                to="/produtos/novo"
                className={`flex items-center gap-2 px-3 py-2 text-sm font-medium border transition-colors
                  ${location.pathname === '/produtos/novo'
                    ? 'bg-gray-900 text-white border-black'
                    : 'bg-white text-gray-600 border-transparent hover:border-black hover:text-gray-900'
                  }`}
              >
                <Plus className="w-4 h-4" />
                <span className="hidden sm:inline">Novo Produto</span>
              </Link>
            </nav>

            {/* Logout */}
            <button
              onClick={handleLogout}
              className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-gray-500 hover:text-gray-900 border border-transparent hover:border-black transition-colors"
              title="Sair"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">Sair</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-black py-4 text-center text-xs text-gray-500">
        E-Commerce Manager © {new Date().getFullYear()}
      </footer>
    </div>
  )
}
