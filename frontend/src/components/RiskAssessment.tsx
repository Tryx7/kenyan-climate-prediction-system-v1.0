"use client"

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { AlertTriangle, Droplets, Flame, Waves, Shield } from 'lucide-react'
import { climateApi } from '@/lib/api'

interface RiskData {
  overall_risk: string
  risk_score: number
  detailed_risks: Array<{
    type: string
    risk_level: string
    description: string
    affected_seasons: string[]
    confidence: number
  }>
  recommendations: string[]
}

export default function RiskAssessment({ location }: { location: string }) {
  const [risk, setRisk] = useState<RiskData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchRisk = async () => {
      setLoading(true)
      try {
        const response = await climateApi.getENSOImpact(location)
        setRisk(response.data.risk_assessment)
      } catch (error) {
        console.error('Risk fetch error:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchRisk()
  }, [location])

  if (loading) {
    return (
      <div className="climate-card animate-pulse">
        <div className="h-48 bg-slate-700 rounded-lg"></div>
      </div>
    )
  }

  if (!risk) return null

  const getRiskColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'high': return 'text-red-400 bg-red-400/10 border-red-400/20'
      case 'medium-high': return 'text-orange-400 bg-orange-400/10 border-orange-400/20'
      case 'medium': return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20'
      default: return 'text-green-400 bg-green-400/10 border-green-400/20'
    }
  }

  const getRiskIcon = (type: string) => {
    switch (type) {
      case 'drought': return <Flame className="w-5 h-5" />
      case 'heavy_rainfall': return <Droplets className="w-5 h-5" />
      case 'flooding': return <Waves className="w-5 h-5" />
      default: return <AlertTriangle className="w-5 h-5" />
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="climate-card"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-climate-green" />
          <h3 className="text-lg font-semibold text-white">Risk Assessment</h3>
        </div>
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(risk.overall_risk)}`}>
          {risk.overall_risk} Risk
        </div>
      </div>

      {/* Risk Score Bar */}
      <div className="mb-4">
        <div className="flex justify-between text-sm mb-1">
          <span className="text-slate-400">Risk Score</span>
          <span className="text-white font-medium">{risk.risk_score}%</span>
        </div>
        <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${risk.risk_score}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
            className={`h-full rounded-full ${
              risk.risk_score > 70 ? 'bg-red-400' : 
              risk.risk_score > 40 ? 'bg-yellow-400' : 'bg-green-400'
            }`}
          />
        </div>
      </div>

      {/* Detailed Risks */}
      <div className="space-y-3 mb-4">
        {risk.detailed_risks.map((r, i) => (
          <div key={i} className={`p-3 rounded-lg border ${getRiskColor(r.risk_level)}`}>
            <div className="flex items-center gap-2 mb-1">
              {getRiskIcon(r.type)}
              <span className="text-sm font-medium capitalize">{r.type.replace('_', ' ')}</span>
              <span className="text-xs opacity-70 ml-auto">{(r.confidence * 100).toFixed(0)}% confidence</span>
            </div>
            <p className="text-xs opacity-80">{r.description}</p>
          </div>
        ))}
      </div>

      {/* Recommendations */}
      <div className="border-t border-slate-700 pt-4">
        <p className="text-sm font-medium text-white mb-2">Recommendations</p>
        <ul className="space-y-1">
          {risk.recommendations.map((rec, i) => (
            <li key={i} className="text-xs text-slate-300 flex items-start gap-2">
              <span className="text-climate-green mt-0.5">•</span>
              {rec}
            </li>
          ))}
        </ul>
      </div>
    </motion.div>
  )
}
