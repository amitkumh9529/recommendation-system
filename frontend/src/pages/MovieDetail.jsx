// frontend/src/pages/MovieDetail.jsx
import React, { useState, useEffect } from "react"
import { useParams, useNavigate, useLocation } from "react-router-dom"
import { getSimilarMovies } from "../services/api"
import { getMovieDetails } from "../services/tmdb"

export default function MovieDetail() {
  const { id }       = useParams()
  const navigate     = useNavigate()
  const location     = useLocation()
  const [movie, setMovie]         = useState(location.state?.movie || null)
  const [similar, setSimilar]     = useState([])
  const [similarMovies, setSimilarMovies] = useState([])
  const [loading, setLoading]     = useState(true)

  const colors = [
    "from-blue-500 to-purple-600",
    "from-green-500 to-teal-600",
    "from-orange-500 to-red-600",
    "from-pink-500 to-rose-600",
    "from-indigo-500 to-blue-600",
    "from-yellow-500 to-orange-600",
  ]

  // Load main movie if not passed via state
  useEffect(() => {
    if (!movie) {
      getMovieDetails(parseInt(id)).then(setMovie)
    }
  }, [id])

  // Load similar movie IDs then fetch their details
  useEffect(() => {
    getSimilarMovies(parseInt(id), 6)
      .then(async res => {
        const ids = res.data.similar_items
        setSimilar(ids)
        const details = await Promise.all(ids.map(getMovieDetails))
        setSimilarMovies(details)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [id])

  return (
    <div className="min-h-screen bg-gray-50">

      {/* Hero */}
      <div className="bg-gradient-to-r from-gray-900 to-blue-900 text-white p-6 sm:p-10 flex flex-col sm:flex-row gap-8 items-start">
        <button
          onClick={() => navigate(-1)}
          className="text-blue-300 hover:text-white font-semibold mb-2 sm:hidden"
        >
          ← Back
        </button>

        {/* Poster */}
        {movie?.poster ? (
          <img
            src={movie.poster}
            alt={movie.title}
            className="w-48 rounded-xl shadow-2xl flex-shrink-0 mx-auto sm:mx-0"
          />
        ) : (
          <div className={`bg-gradient-to-br ${colors[parseInt(id) % colors.length]} w-48 h-72 rounded-xl flex items-center justify-center flex-shrink-0 mx-auto sm:mx-0`}>
            <span className="text-6xl">🎬</span>
          </div>
        )}

        {/* Info */}
        <div className="flex flex-col justify-center">
          <button
            onClick={() => navigate(-1)}
            className="text-blue-300 hover:text-white font-semibold mb-4 hidden sm:block w-fit"
          >
            ← Back
          </button>
          <h1 className="text-3xl sm:text-4xl font-extrabold mb-2">
            {movie ? movie.title : `Movie #${id}`}
          </h1>
          <div className="flex gap-3 flex-wrap mb-3">
            {movie && (
              <>
                <span className="bg-blue-700 px-3 py-1 rounded-full text-sm">{movie.year}</span>
                <span className="bg-yellow-600 px-3 py-1 rounded-full text-sm">⭐ {movie.rating.toFixed(1)}</span>
                {movie.genres.slice(0, 3).map(g => (
                  <span key={g} className="bg-gray-700 px-3 py-1 rounded-full text-sm">{g}</span>
                ))}
              </>
            )}
          </div>
          <p className="text-gray-300 max-w-2xl leading-relaxed">
            {movie ? movie.overview : "Loading movie details..."}
          </p>
        </div>
      </div>

      {/* Similar Movies */}
      <div className="p-6 sm:p-10 max-w-6xl mx-auto">
        <h3 className="text-2xl font-bold text-gray-800 mb-6">🎯 Similar Movies</h3>
        {loading ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-gray-200 animate-pulse rounded-xl h-48" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
            {similar.map((itemId, i) => {
              const m = similarMovies[i]
              return (
                <div
                  key={itemId}
                  onClick={() => navigate(`/movie/${itemId}`, { state: { movie: m } })}
                  className="bg-white rounded-xl shadow hover:shadow-lg hover:scale-105 transition-all cursor-pointer overflow-hidden"
                >
                  {m?.poster ? (
                    <img src={m.poster} alt={m.title} className="w-full h-36 object-cover" />
                  ) : (
                    <div className={`bg-gradient-to-br ${colors[itemId % colors.length]} h-36 flex items-center justify-center`}>
                      <span className="text-3xl">🎬</span>
                    </div>
                  )}
                  <div className="p-2">
                    <p className="text-xs font-semibold text-gray-700 truncate">
                      {m ? m.title : `#${itemId}`}
                    </p>
                    {m && <p className="text-xs text-gray-400">⭐ {m.rating.toFixed(1)}</p>}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}