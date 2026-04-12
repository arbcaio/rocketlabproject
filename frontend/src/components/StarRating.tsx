import { Star } from 'lucide-react'

interface StarRatingProps {
  rating: number | null
  maxRating?: number
  size?: 'sm' | 'md' | 'lg'
  showValue?: boolean
}

export default function StarRating({
  rating,
  maxRating = 5,
  size = 'md',
  showValue = true,
}: StarRatingProps) {
  if (rating === null || rating === undefined) {
    return <span className="text-gray-500 text-sm">Sem avaliações</span>
  }

  const sizeMap = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
  }

  const textSizeMap = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
  }

  return (
    <div className="flex items-center gap-1.5">
      <div className="flex items-center gap-0.5">
        {Array.from({ length: maxRating }, (_, i) => {
          const filled = i + 1 <= Math.round(rating)
          const half = !filled && i + 0.5 < rating
          return (
            <Star
              key={i}
              className={`${sizeMap[size]} ${
                filled
                  ? 'text-amber-400 fill-amber-400'
                  : half
                  ? 'text-amber-400 fill-amber-200'
                  : 'text-gray-300'
              }`}
            />
          )
        })}
      </div>
      {showValue && (
        <span className={`${textSizeMap[size]} font-medium text-gray-600`}>
          {rating.toFixed(1)}
        </span>
      )}
    </div>
  )
}
