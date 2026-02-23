// frontend/src/components/MovieCard.jsx
import React, { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { sendFeedback } from "../services/api"
import { getMovieDetails } from "../services/tmdb"

export default function MovieCard({ itemId, score, userId, rank }) {
  const navigate = useNavigate()
  const [movie, setMovie] = useState(null)
  const [imgError, setImgError] = useState(false)

  const colors = [
    "from-blue-500 to-purple-600",
    "from-green-500 to-teal-600",
    "from-orange-500 to-red-600",
    "from-pink-500 to-rose-600",
    "from-indigo-500 to-blue-600",
    "from-yellow-500 to-orange-600",
  ]
  const gradient = colors[itemId % colors.length]

  useEffect(() => {
    getMovieDetails(itemId).then(setMovie)
  }, [itemId])

  const handleClick = async () => {
    sendFeedback(userId, itemId, true).catch(() => {})
    navigate(`/movie/${itemId}`, { state: { movie } })
  }

  return (
    <div
      onClick={handleClick}
      className="bg-white rounded-xl shadow-md hover:shadow-xl hover:scale-105 transition-all duration-200 cursor-pointer overflow-hidden border border-gray-100"
    >
      {/* Poster */}
      {movie?.poster && !imgError ? (
        <img
          src={movie.poster}
          alt={movie.title}
          onError={() => setImgError(true)}
          className="w-full h-56 object-cover"
        />
      ) : (
        <div className={`bg-gradient-to-br ${gradient} h-56 flex flex-col items-center justify-center gap-2`}>
          {movie ? (
            <p className="text-white font-bold text-center px-2 text-sm">
              {movie.title}
            </p>
          ) : (
            <div className="animate-pulse text-white text-3xl">🎬</div>
          )}
        </div>
      )}

      {/* Info */}
      <div className="p-3">
        <p className="font-semibold text-gray-800 text-sm truncate">
          {movie ? movie.title : `Movie #${itemId}`}
        </p>
        <p className="text-xs text-gray-400 mb-2">
          {movie ? `${movie.year} · ⭐ ${movie.rating.toFixed(1)}` : "Loading..."}
        </p>

        <div className="flex justify-between items-center">
          <span className="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-1 rounded-full">
            #{rank}
          </span>
          <span className="text-xs text-gray-400">
            {(score * 100).toFixed(1)}% match
          </span>
        </div>

        <div className="mt-2 w-full bg-gray-100 rounded-full h-1.5">
          <div
            className="bg-blue-500 h-1.5 rounded-full"
            style={{ width: `${score * 100}%` }}
          />
        </div>
      </div>
    </div>
  )
}