"use client"

import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertTriangle, Bell, X, MapPin, Calendar, ChevronRight } from 'lucide-react'
import { alertsApi } from '@/lib/api'

interface Alert {
  id: number
  location: string
  alert_type: string
  severity: string
  title: string
  description: string
  start_date: string
  end_date: string
  is_active: boolean
}

export default function AlertsPanel({ location }: { location: string }) {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [dismissed, setDismissed] = useState<number[]>([])

  useEffect(() => {
    const fetchAlerts = async () => {
      setLoading(true)
      try {
        const response = await alertsApi.getActive(location)
        setAlerts(response.data.alerts || [])
      } catch (error) {
        console.error('Alerts fetch error:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchAlerts()
    const interval = setInterval(fetchAlerts, 300000) // Refresh every 5 minutes
    return () => clearInterval(interval)
  }, [location])

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return 'bg-red-500/20 border-red-500/50 text-red-400'
      case 'high': return 'bg-orange-500/20 border-orange-500/50 text-orange-400'
      case 'medium': return 'bg-yellow-500/20 border-yellow-500/50 text-yellow-400'
      default: return 'bg-blue-500/20 border-blue-500/50 text-blue-400'
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return <AlertTriangle className="w-5 h-5 text-red-400" />
      case 'high': return <AlertTriangle className="w-5 h-5 text-orange-400" />
      case 'medium': return <Bell className="w-5 h-5 text-yellow-400" />
      default: return <Bell className="w-5 h-5 text-blue-400" />
    }
  }

  const activeAlerts = alerts.filter(a => !dismissed.includes(a.id))

  if (loading) {
    return (
      <div className="climate-card animate-pulse">
        <div className="h-32 bg-slate-700 rounded-lg"></div>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="climate-card"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Bell className="w-5 h-5 text-climate-yellow" />
          <h3 className="text-lg font-semibold text-white">Climate Alerts</h3>
        </div>
        {activeAlerts.length > 0 && (
          <span className="px-2 py-1 bg-red-500/20 text-red-400 text-xs font-medium rounded-full">
            {activeAlerts.length} Active
          </span>
        )}
      </div>

      <AnimatePresence>
        {activeAlerts.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-8 text-slate-400"
          >
            <Bell className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No active alerts for this location</p>
          </motion.div>
        ) : (
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {activeAlerts.map((alert) => (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className={`p-4 rounded-lg border ${getSeverityColor(alert.severity)} relative`}
              >
                <button
                  onClick={() => setDismissed([...dismissed, alert.id])}
                  className="absolute top-2 right-2 text-slate-400 hover:text-white transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>

                <div className="flex items-start gap-3">
                  {getSeverityIcon(alert.severity)}
                  <div className="flex-1 pr-6">
                    <h4 className="text-sm font-semibold text-white mb-1">{alert.title}</h4>
                    <p className="text-xs opacity-80 mb-2">{alert.description}</p>
                    <div className="flex items-center gap-4 text-xs opacity-60">
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        {alert.location}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {alert.start_date} - {alert.end_date}
                      </span>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
