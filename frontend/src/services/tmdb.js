// frontend/src/services/tmdb.js
const TMDB_KEY  = import.meta.env.VITE_TMDB_API_KEY
const TMDB_BASE = "https://api.themoviedb.org/3"
const TMDB_IMG  = "https://image.tmdb.org/t/p/w500"

let linksCache  = null
let moviesCache = null

// ── Load MovieLens ID → TMDb ID mapping ──────────────────
export async function getMovieLinks() {
  if (linksCache) return linksCache
  const res  = await fetch("/links.csv")
  const text = await res.text()
  const map  = {}
  text.trim().split("\n").slice(1).forEach(row => {
    const [movieId, , tmdbId] = row.split(",")
    if (tmdbId?.trim()) map[parseInt(movieId)] = parseInt(tmdbId.trim())
  })
  linksCache = map
  return map
}

// ── Load MovieLens titles for search ─────────────────────
export async function getAllMovies() {
  if (moviesCache) return moviesCache
  const res  = await fetch("/movies.dat")
  const text = await res.text()
  const movies = []
  text.trim().split("\n").forEach(row => {
    const parts = row.split("::")
    if (parts.length >= 2) {
      movies.push({
        movieId: parseInt(parts[0]),
        title:   parts[1].trim(),
        genres:  parts[2]?.trim() || ""
      })
    }
  })
  moviesCache = movies
  return movies
}

// ── Search movies by name ─────────────────────────────────
export async function searchMoviesByName(query) {
  const movies = await getAllMovies()
  const q = query.toLowerCase()
  return movies
    .filter(m => m.title.toLowerCase().includes(q))
    .slice(0, 8)
}

// ── Get full movie details from TMDb ──────────────────────
export async function getMovieDetails(movieLensId) {
  try {
    const links  = await getMovieLinks()
    const tmdbId = links[movieLensId]

    // Get local title as fallback
    const movies = await getAllMovies()
    const local  = movies.find(m => m.movieId === movieLensId)

    if (!tmdbId || !TMDB_KEY) {
      return {
        id:       movieLensId,
        title:    local?.title || `Movie #${movieLensId}`,
        overview: "TMDb API key not configured.",
        poster:   null,
        rating:   0,
        year:     local?.title?.match(/\((\d{4})\)/)?.[1] || "N/A",
        genres:   local?.genres?.split("|") || [],
      }
    }

    const res  = await fetch(`${TMDB_BASE}/movie/${tmdbId}?api_key=${TMDB_KEY}`)
    const data = await res.json()

    return {
      id:       movieLensId,
      tmdbId,
      title:    data.title       || local?.title || `Movie #${movieLensId}`,
      overview: data.overview    || "No description available.",
      poster:   data.poster_path ? `${TMDB_IMG}${data.poster_path}` : null,
      rating:   data.vote_average || 0,
      year:     data.release_date ? data.release_date.split("-")[0] : "N/A",
      genres:   data.genres       ? data.genres.map(g => g.name) : [],
    }
  } catch {
    return null
  }
}