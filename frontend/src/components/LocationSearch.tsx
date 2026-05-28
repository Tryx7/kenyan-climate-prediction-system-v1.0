"use client"

import { useState, useEffect, useRef } from 'react'
import { Search, MapPin } from 'lucide-react'
import { locationsApi } from '@/lib/api'

interface LocationSearchProps {
  onSelect: (location: string) => void
}

interface LocationResult {
  name: string
  type: string
  region: string
  coordinates: { lat: number; lon: number }
}

export default function LocationSearch({ onSelect }: LocationSearchProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<LocationResult[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const debounceRef = useRef<NodeJS.Timeout>()

  useEffect(() => {
    if (query.length < 2) {
      setResults([])
      return
    }

    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
    }

    debounceRef.current = setTimeout(async () => {
      setIsLoading(true)
      try {
        const response = await locationsApi.search(query, 8)
        setResults(response.data.results || [])
      } catch (error) {
        console.error('Search error:', error)
      } finally {
        setIsLoading(false)
      }
    }, 300)

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current)
      }
    }
  }, [query])

  const handleSelect = (location: LocationResult) => {
    setQuery(location.name)
    setIsOpen(false)
    onSelect(location.name)
  }

  return (
    <div className="relative">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value)
            setIsOpen(true)
          }}
          onFocus={() => setIsOpen(true)}
          placeholder="Search location..."
          className="w-full pl-10 pr-4 py-2 bg-slate-800 border border-slate-600 rounded-lg text-sm text-white placeholder-slate-400 focus:outline-none focus:border-climate-blue"
        />
        {isLoading && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <div className="w-4 h-4 border-2 border-climate-blue border-t-transparent rounded-full animate-spin" />
          </div>
        )}
      </div>

      {isOpen && results.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-slate-800 border border-slate-600 rounded-lg shadow-xl z-50 max-h-64 overflow-y-auto">
          {results.map((result) => (
            <button
              key={result.name}
              onClick={() => handleSelect(result)}
              className="w-full px-4 py-3 flex items-center gap-3 hover:bg-slate-700 transition-colors text-left"
            >
              <MapPin className="w-4 h-4 text-climate-blue flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-white">{result.name}</p>
                <p className="text-xs text-slate-400">{result.type} • {result.region}</p>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
