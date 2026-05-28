"use client"

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { BarChart3, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { predictionsApi } from '@/lib/api'

interface ComparisonData {
  location: string
  prediction_type: string
  current_value: number
  predicted_value: number
  previous_value: number
  change_percent: number
  confidence: number
}

export default function ForecastComparison({ location }: { location: string }) {
  const [comparisons, setComparisons] = useState<ComparisonData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        // Simulate comparison data
        const types = ['rainfall', 'temperature', 'humidity', 'wind_speed']
        const data: ComparisonData[] = types.map(type => ({
          location,
          prediction_type: type,
          current_value: Math.random() * 100,
          predicted_value: Math.random() * 100,
          previous_value: Math.random() * 100,
          change_percent: (Math.random() - 0.5) * 40,
          confidence: 0.65 + Math.random() * 0.25
        }))
        setComparisons(data)
      } catch (error) {
        console.error('Comparison fetch error:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [location])

  const getChangeIcon = (change: number) => {
    if (change > 5) return <TrendingUp className="w-4 h-4 text-green-400" />
    if (change < -5) return <TrendingDown className="w-4 h-4 text-red-400" />
    return <Minus className="w-4 h-4 text-slate-400" />
  }

  const getChangeColor = (change: number) => {
    if (change > 5) return 'text-green-400'
    if (change < -5) return 'text-red-400'
    return 'text-slate-400'
  }

  if (loading) {
    return (
      <div className="climate-card animate-pulse">
        <div className="h-48 bg-slate-700 rounded-lg"></div>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="climate-card"
    >
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 className="w-5 h-5 text-climate-blue" />
        <h3 className="text-lg font-semibold text-white">Forecast vs Historical</h3>
      </div>

      <div className="space-y-4">
        {comparisons.map((item, i) => (
          <div key={i} className="bg-slate-800/50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-white capitalize">{item.prediction_type.replace('_', ' ')}</span>
              <div className={`flex items-center gap-1 ${getChangeColor(item.change_percent)}`}>
                {getChangeIcon(item.change_percent)}
                <span className="text-sm font-semibold">
                  {item.change_percent > 0 ? '+' : ''}{item.change_percent.toFixed(1)}%
                </span>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2 text-center">
              <div>
                <p className="text-xs text-slate-400">Previous</p>
                <p className="text-sm font-semibold text-slate-300">{item.previous_value.toFixed(1)}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400">Current</p>
                <p className="text-sm font-semibold text-white">{item.current_value.toFixed(1)}</p>
              </div>
              <div>
                <p className="text-xs text-climate-blue">Predicted</p>
                <p className="text-sm font-semibold text-climate-blue">{item.predicted_value.toFixed(1)}</p>
              </div>
            </div>

            <div className="mt-2">
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-400">Confidence</span>
                <span className="text-white">{(item.confidence * 100).toFixed(0)}%</span>
              </div>
              <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${item.confidence * 100}%` }}
                  transition={{ duration: 1, delay: i * 0.1 }}
                  className="h-full bg-climate-blue rounded-full"
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  )
}
