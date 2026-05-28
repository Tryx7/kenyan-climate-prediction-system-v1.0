"use client"

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Calendar, CloudRain, Sun, Snowflake, ArrowRight } from 'lucide-react'
import { climateApi } from '@/lib/api'

interface SeasonalData {
  current_season: string
  next_season: string
  enso_influence: string
  outlook: string
  historical_comparison: {
    last_5_years_average_rainfall_mm: number
    last_year_rainfall_mm: number
    deviation_from_average: number
    trend: string
  }
}

export default function SeasonalOutlook({ location }: { location: string }) {
  const [outlook, setOutlook] = useState<SeasonalData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchOutlook = async () => {
      setLoading(true)
      try {
        const response = await climateApi.getSeasonalOutlook(location)
        setOutlook(response.data)
      } catch (error) {
        console.error('Outlook fetch error:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchOutlook()
  }, [location])

  if (loading) {
    return (
      <div className="climate-card animate-pulse">
        <div className="h-48 bg-slate-700 rounded-lg"></div>
      </div>
    )
  }

  if (!outlook) return null

  const getSeasonIcon = (season: string) => {
    if (season.includes('Rain')) return <CloudRain className="w-6 h-6 text-blue-400" />
    if (season.includes('Dry')) return <Sun className="w-6 h-6 text-yellow-400" />
    if (season.includes('Cool')) return <Snowflake className="w-6 h-6 text-cyan-400" />
    return <Calendar className="w-6 h-6 text-slate-400" />
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="climate-card"
    >
      <div className="flex items-center gap-2 mb-4">
        <Calendar className="w-5 h-5 text-climate-yellow" />
        <h3 className="text-lg font-semibold text-white">Seasonal Outlook</h3>
      </div>

      {/* Season Timeline */}
      <div className="flex items-center gap-4 mb-6">
        <div className="flex-1 p-4 bg-slate-800/50 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            {getSeasonIcon(outlook.current_season)}
            <span className="text-sm font-medium text-white">Current</span>
          </div>
          <p className="text-lg font-bold text-white">{outlook.current_season}</p>
        </div>

        <ArrowRight className="w-5 h-5 text-slate-500" />

        <div className="flex-1 p-4 bg-slate-800/50 rounded-lg border border-climate-blue/20">
          <div className="flex items-center gap-2 mb-2">
            {getSeasonIcon(outlook.next_season)}
            <span className="text-sm font-medium text-climate-blue">Next</span>
          </div>
          <p className="text-lg font-bold text-white">{outlook.next_season}</p>
        </div>
      </div>

      {/* ENSO Influence */}
      <div className="p-4 bg-slate-800/50 rounded-lg mb-4">
        <p className="text-sm font-medium text-white mb-1">ENSO Influence</p>
        <p className="text-sm text-slate-300">{outlook.enso_influence} conditions affecting this outlook</p>
      </div>

      {/* Outlook Text */}
      <div className="p-4 bg-gradient-to-r from-climate-blue/10 to-climate-green/10 rounded-lg border border-climate-blue/20 mb-4">
        <p className="text-sm text-slate-200 leading-relaxed">{outlook.outlook}</p>
      </div>

      {/* Historical Comparison */}
      <div className="border-t border-slate-700 pt-4">
        <p className="text-sm font-medium text-white mb-3">Historical Comparison</p>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-xs text-slate-400">5-Year Avg</p>
            <p className="text-lg font-bold text-white">{outlook.historical_comparison.last_5_years_average_rainfall_mm}mm</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-slate-400">Last Year</p>
            <p className="text-lg font-bold text-white">{outlook.historical_comparison.last_year_rainfall_mm}mm</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-slate-400">Deviation</p>
            <p className={`text-lg font-bold ${
              outlook.historical_comparison.deviation_from_average < 0 ? 'text-red-400' : 'text-green-400'
            }`}>
              {outlook.historical_comparison.deviation_from_average > 0 ? '+' : ''}
              {outlook.historical_comparison.deviation_from_average}%
            </p>
          </div>
        </div>
        <div className="mt-3 flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${
            outlook.historical_comparison.trend === 'decreasing' ? 'bg-red-400' : 'bg-green-400'
          }`} />
          <p className="text-xs text-slate-400">
            Rainfall trend: {outlook.historical_comparison.trend}
          </p>
        </div>
      </div>
    </motion.div>
  )
}
