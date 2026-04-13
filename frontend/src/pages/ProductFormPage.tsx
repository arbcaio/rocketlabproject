import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Save, Loader2, AlertCircle, Package } from 'lucide-react'
import { getProduto, createProduto, updateProduto, getCategorias } from '../api/produtos'
import type { ProdutoCreate } from '../types'
import { formatCategoria } from '../utils/categoryImages'

interface FormData {
  nome_produto: string
  categoria_produto: string
  peso_produto_gramas: string
  comprimento_centimetros: string
  altura_centimetros: string
  largura_centimetros: string
}

const EMPTY_FORM: FormData = {
  nome_produto: '',
  categoria_produto: '',
  peso_produto_gramas: '',
  comprimento_centimetros: '',
  altura_centimetros: '',
  largura_centimetros: '',
}

export default function ProductFormPage() {
  const { id } = useParams<{ id?: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const isEditing = !!id

  const [form, setForm] = useState<FormData>(EMPTY_FORM)
  const [errors, setErrors] = useState<Partial<FormData>>({})

  // Load existing product for edit
  const { data: produto, isLoading: loadingProduto } = useQuery({
    queryKey: ['produto', id],
    queryFn: () => getProduto(id!),
    enabled: isEditing,
  })

  // Categories list
  const { data: categorias } = useQuery({
    queryKey: ['categorias'],
    queryFn: getCategorias,
    staleTime: Infinity,
  })

  useEffect(() => {
    if (produto) {
      setForm({
        nome_produto: produto.nome_produto,
        categoria_produto: produto.categoria_produto,
        peso_produto_gramas: produto.peso_produto_gramas?.toString() ?? '',
        comprimento_centimetros: produto.comprimento_centimetros?.toString() ?? '',
        altura_centimetros: produto.altura_centimetros?.toString() ?? '',
        largura_centimetros: produto.largura_centimetros?.toString() ?? '',
      })
    }
  }, [produto])

  const createMutation = useMutation({
    mutationFn: (payload: ProdutoCreate) => createProduto(payload),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['produtos'] })
      navigate(`/produtos/${data.id_produto}`)
    },
  })

  const updateMutation = useMutation({
    mutationFn: (payload: ProdutoCreate) => updateProduto(id!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['produto', id] })
      queryClient.invalidateQueries({ queryKey: ['produtos'] })
      navigate(`/produtos/${id}`)
    },
  })

  const isPending = createMutation.isPending || updateMutation.isPending
  const mutationError = createMutation.error || updateMutation.error

  const validate = (): boolean => {
    const newErrors: Partial<FormData> = {}
    if (!form.nome_produto.trim()) newErrors.nome_produto = 'Nome é obrigatório'
    if (!form.categoria_produto.trim()) newErrors.categoria_produto = 'Categoria é obrigatória'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return

    const payload: ProdutoCreate = {
      nome_produto: form.nome_produto.trim(),
      categoria_produto: form.categoria_produto.trim(),
      peso_produto_gramas: form.peso_produto_gramas ? parseFloat(form.peso_produto_gramas) : null,
      comprimento_centimetros: form.comprimento_centimetros
        ? parseFloat(form.comprimento_centimetros)
        : null,
      altura_centimetros: form.altura_centimetros ? parseFloat(form.altura_centimetros) : null,
      largura_centimetros: form.largura_centimetros ? parseFloat(form.largura_centimetros) : null,
    }

    if (isEditing) {
      updateMutation.mutate(payload)
    } else {
      createMutation.mutate(payload)
    }
  }

  const handleChange = (field: keyof FormData, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: undefined }))
  }

  if (isEditing && loadingProduto) {
    return (
      <div className="flex items-center justify-center py-24">
        <Loader2 className="w-8 h-8 text-gray-700 animate-spin" />
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Back */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-1.5 text-gray-500 hover:text-gray-900 mb-6 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Voltar
      </button>

      {/* Header */}
      <div className="mb-6 flex items-center gap-3">
        <div className="p-2.5 bg-gray-900 border border-black">
          <Package className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            {isEditing ? 'Editar Produto' : 'Novo Produto'}
          </h1>
          <p className="text-gray-500 dark:text-gray-400 text-sm">
            {isEditing ? `Editando: ${produto?.nome_produto}` : 'Preencha as informações do produto'}
          </p>
        </div>
      </div>

      {/* Error banner */}
      {mutationError && (
        <div className="card p-4 mb-4 border-red-300 bg-red-50 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
          <p className="text-red-700 text-sm">
            Erro ao salvar produto. Verifique os dados e tente novamente.
          </p>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="card p-6 space-y-5">
        {/* Nome */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
            Nome do Produto <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={form.nome_produto}
            onChange={(e) => handleChange('nome_produto', e.target.value)}
            placeholder="Ex: Tênis Esportivo Premium"
            className={`input ${errors.nome_produto ? 'border-red-500 focus:ring-red-500' : ''}`}
          />
          {errors.nome_produto && (
            <p className="text-red-600 text-xs mt-1">{errors.nome_produto}</p>
          )}
        </div>

        {/* Categoria */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
            Categoria <span className="text-red-500">*</span>
          </label>
          {categorias && categorias.length > 0 ? (
            <select
              value={form.categoria_produto}
              onChange={(e) => handleChange('categoria_produto', e.target.value)}
              className={`input ${errors.categoria_produto ? 'border-red-500 focus:ring-red-500' : ''}`}
            >
              <option value="">Selecione uma categoria...</option>
              {categorias.map((c) => (
                <option key={c.categoria} value={c.categoria}>
                  {formatCategoria(c.categoria)}
                </option>
              ))}
              <option value="outros">Outros</option>
            </select>
          ) : (
            <input
              type="text"
              value={form.categoria_produto}
              onChange={(e) => handleChange('categoria_produto', e.target.value)}
              placeholder="Ex: eletronicos"
              className={`input ${errors.categoria_produto ? 'border-red-500 focus:ring-red-500' : ''}`}
            />
          )}
          {errors.categoria_produto && (
            <p className="text-red-600 text-xs mt-1">{errors.categoria_produto}</p>
          )}
        </div>

        {/* Divider */}
        <div className="border-t border-black/10 pt-4">
          <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-4 uppercase tracking-wider">
            Dimensões (opcional)
          </h3>
          <div className="grid grid-cols-2 gap-4">
            {/* Peso */}
            <div>
              <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                Peso (gramas)
              </label>
              <input
                type="number"
                min="0"
                step="0.1"
                value={form.peso_produto_gramas}
                onChange={(e) => handleChange('peso_produto_gramas', e.target.value)}
                placeholder="Ex: 500"
                className="input text-sm"
              />
            </div>

            {/* Comprimento */}
            <div>
              <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                Comprimento (cm)
              </label>
              <input
                type="number"
                min="0"
                step="0.1"
                value={form.comprimento_centimetros}
                onChange={(e) => handleChange('comprimento_centimetros', e.target.value)}
                placeholder="Ex: 30"
                className="input text-sm"
              />
            </div>

            {/* Altura */}
            <div>
              <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                Altura (cm)
              </label>
              <input
                type="number"
                min="0"
                step="0.1"
                value={form.altura_centimetros}
                onChange={(e) => handleChange('altura_centimetros', e.target.value)}
                placeholder="Ex: 15"
                className="input text-sm"
              />
            </div>

            {/* Largura */}
            <div>
              <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                Largura (cm)
              </label>
              <input
                type="number"
                min="0"
                step="0.1"
                value={form.largura_centimetros}
                onChange={(e) => handleChange('largura_centimetros', e.target.value)}
                placeholder="Ex: 10"
                className="input text-sm"
              />
            </div>
          </div>
        </div>

        {/* Submit */}
        <div className="flex justify-end gap-3 pt-2 border-t border-black/10">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="btn-secondary"
            disabled={isPending}
          >
            Cancelar
          </button>
          <button type="submit" className="btn-primary" disabled={isPending}>
            {isPending ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Salvando...
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                {isEditing ? 'Salvar Alterações' : 'Criar Produto'}
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
