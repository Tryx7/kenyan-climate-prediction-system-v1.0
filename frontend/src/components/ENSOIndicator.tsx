"use client"

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Waves, ArrowUp, ArrowDown, Minus, AlertTriangle } from 'lucide-react'
import { climateApi } from '@/lib/api'

interface ENSOData {
  current_phase: string
  severity: string
  oni_value: number
  period: string
  description: string
  typical_duration_months: number
}

export default function ENSOIndicator() {
  const [enso, setEnso] = useState<ENSOData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchENSO = async () => {
      try {
        const response = await climateApi.getENSOCurrent()
        setEnso(response.data)
      } catch (error) {
        console.error('ENSO fetch error:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchENSO()
    const interval = setInterval(fetchENSO, 3600000) // Update every hour
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="climate-card animate-pulse">
        <div className="h-32 bg-slate-700 rounded-lg"></div>
      </div>
    )
  }

  if (!enso) return null

  const getPhaseColor = () => {
    switch (enso.current_phase) {
      case 'El Nino': return 'text-red-400 bg-red-400/10 border-red-400/20'
      case 'La Nina': return 'text-blue-400 bg-blue-400/10 border-blue-400/20'
      default: return 'text-green-400 bg-green-400/10 border-green-400/20'
    }
  }

  const getPhaseIcon = () => {
    switch (enso.current_phase) {
      case 'El Nino': return <ArrowUp className="w-6 h-6" />
      case 'La Nina': return <ArrowDown className="w-6 h-6" />
      default: return <Minus className="w-6 h-6" />
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="climate-card"
    >
      <div className="flex items-center gap-2 mb-4">
        <Waves className="w-5 h-5 text-climate-blue" />
        <h3 className="text-lg font-semibold text-white">ENSO Status</h3>
      </div>

      <div className={`p-4 rounded-lg border ${getPhaseColor()} mb-4`}>
        <div className="flex items-center gap-3">
          {getPhaseIcon()}
          <div>
            <p className="text-lg font-bold">{enso.current_phase}</p>
            <p className="text-sm opacity-80">{enso.severity}</p>
          </div>
        </div>
        <div className="mt-3 flex items-center gap-4">
          <div>
            <p className="text-xs opacity-70">ONI Value</p>
            <p className="text-xl font-bold">{enso.oni_value}</p>
          </div>
          <div>
            <p className="text-xs opacity-70">Period</p>
            <p className="text-sm font-medium">{enso.period}</p>
          </div>
          <div>
            <p className="text-xs opacity-70">Duration</p>
            <p className="text-sm font-medium">~{enso.typical_duration_months} months</p>
          </div>
        </div>
      </div>

      <p className="text-sm text-slate-300 leading-relaxed">{enso.description}</p>

      {enso.current_phase !== 'Neutral' && (
        <div className="mt-4 flex items-start gap-2 p-3 bg-yellow-400/10 border border-yellow-400/20 rounded-lg">
          <AlertTriangle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-yellow-200">
            {enso.current_phase === 'El Nino' 
              ? 'Monitor for enhanced rainfall and potential flooding during OND season.'
              : 'Prepare for potential drought conditions. Water conservation recommended.'}
          </p>
        </div>
      )}
    </motion.div>
  )
}
