import React from "react"

import MovieCard from "./MovieCard";

export default function RecommendationGrid({ recommendations, userId }) {
  if (!recommendations.length) return null;

  return (
    <div className="px-6 pb-10">
      <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
        🎯 Top {recommendations.length} Recommendations
      </h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-5">
        {recommendations.map((item, index) => (
          <MovieCard
            key={item.itemId}
            itemId={item.itemId}
            score={item.score}
            userId={userId}
            rank={index + 1}
          />
        ))}
      </div>
    </div>
  );
}