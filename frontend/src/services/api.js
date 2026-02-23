import axios from "axios"

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1"

const api = axios.create({ baseURL: BASE_URL })

export const getRecommendations = (userId, topK = 10) =>
  api.get(`/recommend/${userId}`, { params: { top_k: topK } })

export const getSimilarMovies = (itemId, topK = 6) =>
  api.get(`/similar/${itemId}`, { params: { top_k: topK } })

export const sendFeedback = (userId, itemId, clicked, rating = null) =>
  api.post("/feedback", { user_id: userId, item_id: itemId, clicked, rating })

export default api