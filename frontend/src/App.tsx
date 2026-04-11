import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import CatalogPage from './pages/CatalogPage'
import ProductDetailPage from './pages/ProductDetailPage'
import ProductFormPage from './pages/ProductFormPage'

export default function App() {
  return (
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
  )
}
