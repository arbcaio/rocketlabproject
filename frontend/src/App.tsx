import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import { ThemeProvider } from './context/ThemeContext'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import CatalogPage from './pages/CatalogPage'
import ProductDetailPage from './pages/ProductDetailPage'
import ProductFormPage from './pages/ProductFormPage'

function AppRoutes() {
  const { isAuthenticated } = useAuth()

  return (
    <Routes>
      {/* Rota pública */}
      <Route
        path="/login"
        element={isAuthenticated ? <Navigate to="/produtos" replace /> : <LoginPage />}
      />

      {/* Rotas protegidas */}
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <Layout>
              <Routes>
                <Route path="/" element={<Navigate to="/produtos" replace />} />
                <Route path="/produtos" element={<CatalogPage />} />
                <Route path="/produtos/novo" element={<ProductFormPage />} />
                <Route path="/produtos/:id/editar" element={<ProductFormPage />} />
                <Route path="/produtos/:id" element={<ProductDetailPage />} />
                <Route path="*" element={<Navigate to="/produtos" replace />} />
              </Routes>
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </ThemeProvider>
  )
}
