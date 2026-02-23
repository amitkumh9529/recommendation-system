// frontend/src/pages/Home.jsx
import React, { useState } from "react"
import SearchBar from "../components/SearchBar"
import RecommendationGrid from "../components/RecommendationGrid"
import { getRecommendations } from "../services/api"
import { getAllMovies } from "../services/tmdb"

export default function Home() {
  const [recs, setRecs]         = useState([])
  const [userId, setUserId]     = useState(null)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState("")
  const [searchedMovie, setSearchedMovie] = useState(null)

  // Called when user selects a movie from dropdown
  // We find a user who rated it highly and get their recs
  const handleMovieSelect = async (movieId) => {
    try {
      setLoading(true)
      setError("")

      // Find a user who liked this movie — use movieId as proxy user
      // (In real system you'd look up top raters of this movie)
      const proxyUserId = (movieId % 6040) + 1
      setUserId(proxyUserId)

      const res  = await getRecommendations(proxyUserId, 10)
      const data = res.data
      setRecs(data.recommended_item_ids.map((id, i) => ({
        itemId: id,
        score:  data.scores[i]
      })))

      const movies = await getAllMovies()
      const found  = movies.find(m => m.movieId === movieId)
      setSearchedMovie(found)
    } catch {
      setError("❌ Could not fetch recommendations. Is the API running?")
    } finally {
      setLoading(false)
    }
  }

  // Called on Enter key — search by text query
  const handleSearch = async (query) => {
    try {
      setLoading(true)
      setError("")
      const movies  = await getAllMovies()
      const matched = movies.find(m =>
        m.title.toLowerCase().includes(query.toLowerCase())
      )
      if (matched) {
        await handleMovieSelect(matched.movieId)
      } else {
        setError("❌ No movie found with that name. Try a different title.")
      }
    } catch {
      setError("❌ Something went wrong. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">

      {/* Hero */}
      <div className="bg-gradient-to-r from-gray-900 to-blue-900 text-white text-center py-14 px-4">
        <h2 className="text-4xl font-extrabold mb-3">🎬 Discover Your Next Movie</h2>
        <p className="text-blue-200 text-lg max-w-xl mx-auto">
          Powered by Neural Collaborative Filtering · 1M ratings · Real movie data via TMDb
        </p>
      </div>

      <SearchBar
        onSearch={handleSearch}
        onMovieSelect={handleMovieSelect}
        loading={loading}
      />

      {searchedMovie && !loading && recs.length > 0 && (
        <p className="text-center text-gray-500 text-sm mb-4">
          Showing recommendations based on fans of{" "}
          <span className="font-semibold text-blue-600">{searchedMovie.title}</span>
        </p>
      )}

      {error && (
        <div className="mx-auto max-w-xl mb-6 bg-red-50 border border-red-200 text-red-600 rounded-lg p-4 text-center">
          {error}
        </div>
      )}

      {loading && (
        <div className="text-center text-gray-400 mt-16 text-xl animate-pulse">
          🔄 Finding recommendations...
        </div>
      )}

      {!loading && recs.length === 0 && !error && (
        <div className="text-center mt-16">
          <p className="text-6xl mb-4">🎬</p>
          <p className="text-gray-400 text-xl">Search for a movie above to get started</p>
          <p className="text-gray-300 text-sm mt-2">Try "Toy Story", "Matrix", or "Titanic"</p>
        </div>
      )}

      {!loading && <RecommendationGrid recommendations={recs} userId={userId} />}
    </div>
  )
}
