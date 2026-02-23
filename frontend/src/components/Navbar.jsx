import React from "react"


export default function Navbar() {
  return (
    <nav className="bg-gray-900 text-white px-6 py-4 flex items-center gap-4 shadow-lg">
      <span className="text-2xl">🎬</span>
      <h1 className="text-xl font-bold text-blue-400">MovieRec</h1>
      <span className="text-gray-400 text-sm">Deep Learning Recommendations</span>
    </nav>
  );
}