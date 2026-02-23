// frontend/src/components/SearchBar.jsx
import React, { useState, useEffect, useRef } from "react"
import { searchMoviesByName } from "../services/tmdb"

export default function SearchBar({ onSearch, onMovieSelect, loading }) {
  const [query, setQuery]           = useState("")
  const [suggestions, setSuggestions] = useState([])
  const [showDrop, setShowDrop]     = useState(false)
  const ref = useRef()

  // Close dropdown on outside click
  useEffect(() => {
    const handler = e => {
      if (ref.current && !ref.current.contains(e.target)) setShowDrop(false)
    }
    document.addEventListener("mousedown", handler)
    return () => document.removeEventListener("mousedown", handler)
  }, [])

  // Search as user types
  useEffect(() => {
    if (query.length < 2) { setSuggestions([]); return }
    const timer = setTimeout(async () => {
      const results = await searchMoviesByName(query)
      setSuggestions(results)
      setShowDrop(true)
    }, 300)
    return () => clearTimeout(timer)
  }, [query])

  const handleSelect = (movie) => {
    setQuery(movie.title)
    setShowDrop(false)
    onMovieSelect(movie.movieId)
  }

  const handleSubmit = () => {
    if (query.trim()) onSearch(query)
  }

  return (
    <div className="flex flex-col items-center my-8 px-4" ref={ref}>
      <div className="relative w-full max-w-xl">
        <div className="flex gap-3">
          <input
            type="text"
            placeholder="🔍 Search by movie name e.g. Toy Story..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleSubmit()}
            onFocus={() => suggestions.length && setShowDrop(true)}
            className="border border-gray-300 rounded-lg px-4 py-3 w-full text-base focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
          <button
            onClick={handleSubmit}
            disabled={loading || !query.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-6 py-3 rounded-lg font-semibold whitespace-nowrap transition-colors"
          >
            {loading ? "Loading..." : "Get Recs"}
          </button>
        </div>

        {/* Dropdown Suggestions */}
        {showDrop && suggestions.length > 0 && (
          <div className="absolute top-full left-0 right-0 bg-white border border-gray-200 rounded-xl shadow-xl z-50 mt-1 overflow-hidden">
            {suggestions.map(movie => (
              <div
                key={movie.movieId}
                onClick={() => handleSelect(movie)}
                className="flex justify-between items-center px-4 py-3 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-0"
              >
                <div>
                  <p className="font-semibold text-gray-800 text-sm">{movie.title}</p>
                  <p className="text-xs text-gray-400">{movie.genres.split("|").slice(0,3).join(" · ")}</p>
                </div>
                <span className="text-xs text-blue-500 font-medium ml-2">
                  ID #{movie.movieId}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
      <p className="text-xs text-gray-400 mt-2">
        Search by movie title to find users who loved it, then get recommendations
      </p>
    </div>
  )
}