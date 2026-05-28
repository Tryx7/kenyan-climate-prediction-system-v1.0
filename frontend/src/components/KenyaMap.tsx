"use client"

import { useState } from 'react'
import { motion } from 'framer-motion'
import { MapPin, Info } from 'lucide-react'

interface MapLocation {
  name: string
  lat: number
  lon: number
  risk: 'low' | 'medium' | 'high' | 'critical'
}

const locations: MapLocation[] = [
  { name: 'Nairobi', lat: -1.29, lon: 36.82, risk: 'medium' },
  { name: 'Mombasa', lat: -4.04, lon: 39.67, risk: 'high' },
  { name: 'Kisumu', lat: -0.10, lon: 34.76, risk: 'medium' },
  { name: 'Nakuru', lat: -0.30, lon: 36.07, risk: 'low' },
  { name: 'Eldoret', lat: 0.51, lon: 35.27, risk: 'low' },
  { name: 'Garissa', lat: -0.46, lon: 39.66, risk: 'critical' },
  { name: 'Lodwar', lat: 3.12, lon: 35.60, risk: 'critical' },
  { name: 'Wajir', lat: 1.75, lon: 40.06, risk: 'high' },
  { name: 'Mandera', lat: 3.93, lon: 41.86, risk: 'high' },
  { name: 'Marsabit', lat: 2.33, lon: 37.99, risk: 'high' },
]

const getRiskColor = (risk: string) => {
  switch (risk) {
    case 'critical': return '#ef4444'
    case 'high': return '#f97316'
    case 'medium': return '#eab308'
    default: return '#22c55e'
  }
}

export default function KenyaMap({ onLocationSelect }: { onLocationSelect: (loc: string) => void }) {
  const [hoveredLocation, setHoveredLocation] = useState<string | null>(null)
  const [selectedLocation, setSelectedLocation] = useState<string>('Nairobi')

  const handleClick = (loc: MapLocation) => {
    setSelectedLocation(loc.name)
    onLocationSelect(loc.name)
  }

  // Simple coordinate mapping for Kenya
  const mapLat = (lat: number) => {
    const minLat = -5
    const maxLat = 5
    return ((lat - minLat) / (maxLat - minLat)) * 100
  }

  const mapLon = (lon: number) => {
    const minLon = 33
    const maxLon = 42
    return ((lon - minLon) / (maxLon - minLon)) * 100
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="climate-card"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <MapPin className="w-5 h-5 text-climate-green" />
          <h3 className="text-lg font-semibold text-white">Kenya Climate Risk Map</h3>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-500"></span> Low</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-yellow-500"></span> Medium</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-orange-500"></span> High</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500"></span> Critical</span>
        </div>
      </div>

      <div className="relative h-80 bg-slate-800/50 rounded-lg overflow-hidden">
        {/* Simplified Kenya outline */}
        <svg viewBox="0 0 100 100" className="w-full h-full">
          {/* Kenya shape approximation */}
          <path
            d="M20,85 L25,70 L30,65 L35,60 L40,55 L45,50 L50,45 L55,40 L60,35 L65,30 L70,25 L75,20 L80,15 L85,20 L90,25 L85,35 L80,45 L75,55 L70,65 L65,75 L60,85 L55,90 L50,85 L45,80 L40,85 L35,90 L30,85 L25,80 L20,85 Z"
            fill="rgba(30, 41, 59, 0.5)"
            stroke="rgba(148, 163, 184, 0.3)"
            strokeWidth="0.5"
          />

          {/* Location markers */}
          {locations.map((loc) => (
            <g key={loc.name}>
              <circle
                cx={mapLon(loc.lon)}
                cy={mapLat(loc.lat)}
                r={selectedLocation === loc.name ? 4 : 3}
                fill={getRiskColor(loc.risk)}
                stroke="white"
                strokeWidth={selectedLocation === loc.name ? 2 : 1}
                className="cursor-pointer transition-all hover:r-5"
                onMouseEnter={() => setHoveredLocation(loc.name)}
                onMouseLeave={() => setHoveredLocation(null)}
                onClick={() => handleClick(loc)}
              />
              {hoveredLocation === loc.name && (
                <text
                  x={mapLon(loc.lon)}
                  y={mapLat(loc.lat) - 8}
                  textAnchor="middle"
                  fill="white"
                  fontSize="3"
                  fontWeight="bold"
                >
                  {loc.name}
                </text>
              )}
            </g>
          ))}
        </svg>

        {/* Legend */}
        <div className="absolute bottom-2 left-2 bg-slate-900/80 rounded-lg p-2 text-xs">
          <p className="text-slate-400 mb-1">Selected: <span className="text-white font-medium">{selectedLocation}</span></p>
          <p className="text-slate-500">Click any point to view details</p>
        </div>
      </div>
    </motion.div>
  )
}
