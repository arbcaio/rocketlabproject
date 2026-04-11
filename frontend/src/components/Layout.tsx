import { Link, useLocation } from 'react-router-dom'
import { ShoppingBag, Plus, BarChart3 } from 'lucide-react'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navbar */}
      <header className="sticky top-0 z-50 bg-gray-900/95 backdrop-blur border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/produtos" className="flex items-center gap-3 group">
              <div className="p-2 bg-brand-600 rounded-xl group-hover:bg-brand-500 transition-colors">
                <ShoppingBag className="w-5 h-5 text-white" />
              </div>
              <div>
                <span className="text-lg font-bold text-white">E-Commerce</span>
                <span className="text-xs text-gray-400 block -mt-1">Painel do Gerente</span>
              </div>
            </Link>

            <nav className="flex items-center gap-2">
              <Link
                to="/produtos"
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors
                  ${location.pathname === '/produtos'
                    ? 'bg-brand-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                  }`}
              >
                <BarChart3 className="w-4 h-4" />
                <span className="hidden sm:inline">Catálogo</span>
              </Link>

              <Link
                to="/produtos/novo"
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors
                  ${location.pathname === '/produtos/novo'
                    ? 'bg-brand-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                  }`}
              >
                <Plus className="w-4 h-4" />
                <span className="hidden sm:inline">Novo Produto</span>
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-4 text-center text-xs text-gray-600">
        E-Commerce Manager © {new Date().getFullYear()}
      </footer>
    </div>
  )
}
