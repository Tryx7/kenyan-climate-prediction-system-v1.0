"use client"

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Cloud, Droplets, Thermometer, Wind, AlertTriangle, TrendingUp, MapPin, Search, BarChart3, Activity } from 'lucide-react'
import LocationSearch from '@/components/LocationSearch'
import WeatherCard from '@/components/WeatherCard'
import ENSOIndicator from '@/components/ENSOIndicator'
import RiskAssessment from '@/components/RiskAssessment'
import PredictionChart from '@/components/PredictionChart'
import SeasonalOutlook from '@/components/SeasonalOutlook'
import AlertsPanel from '@/components/AlertsPanel'
import ForecastComparison from '@/components/ForecastComparison'
import KenyaMap from '@/components/KenyaMap'
import toast from 'react-hot-toast'

export default function Dashboard() {
  const [selectedLocation, setSelectedLocation] = useState<string>('Nairobi')
  const [isLoading, setIsLoading] = useState(false)
  const [activeSection, setActiveSection] = useState<'overview' | 'predictions' | 'alerts' | 'analytics'>('overview')

  const handleLocationSelect = (location: string) => {
    setIsLoading(true)
    setSelectedLocation(location)
    toast.success(`Location updated to ${location}`)
    setTimeout(() => setIsLoading(false), 500)
  }

  return (
    <div className="min-h-screen bg-climate-dark">
      {/* Header */}
      <header className="border-b border-slate-700 bg-climate-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 climate-gradient rounded-lg flex items-center justify-center">
              <Cloud className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Kenya Climate Predict</h1>
              <p className="text-xs text-slate-400">AI-Powered Weather Intelligence</p>
            </div>
          </div>

          <div className="flex items-center gap-6">
            {/* Navigation */}
            <nav className="hidden md:flex items-center gap-1">
              {[
                { id: 'overview', label: 'Overview', icon: Activity },
                { id: 'predictions', label: 'Predictions', icon: TrendingUp },
                { id: 'alerts', label: 'Alerts', icon: AlertTriangle },
                { id: 'analytics', label: 'Analytics', icon: BarChart3 },
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveSection(item.id as any)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-colors ${
                    activeSection === item.id
                      ? 'bg-climate-blue text-white'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  <item.icon className="w-4 h-4" />
                  {item.label}
                </button>
              ))}
            </nav>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-sm text-slate-400">
                <MapPin className="w-4 h-4" />
                <span>{selectedLocation}</span>
              </div>
              <div className="w-48">
                <LocationSearch onSelect={handleLocationSelect} />
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {isLoading && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-center py-12"
          >
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-climate-blue"></div>
          </motion.div>
        )}

        {/* Overview Section */}
        {activeSection === 'overview' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >
            {/* Top Stats Row */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard 
                icon={<Droplets className="w-6 h-6 text-blue-400" />}
                label="Rainfall Forecast"
                value="150mm"
                change="+12%"
                positive={true}
              />
              <StatCard 
                icon={<Thermometer className="w-6 h-6 text-red-400" />}
                label="Temperature"
                value="24°C"
                change="+1.2°C"
                positive={false}
              />
              <StatCard 
                icon={<Wind className="w-6 h-6 text-green-400" />}
                label="Wind Speed"
                value="12 km/h"
                change="-3%"
                positive={true}
              />
              <StatCard 
                icon={<AlertTriangle className="w-6 h-6 text-yellow-400" />}
                label="Risk Level"
                value="Medium"
                change="Stable"
                positive={true}
              />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column */}
              <div className="lg:col-span-2 space-y-6">
                <WeatherCard location={selectedLocation} />
                <KenyaMap onLocationSelect={handleLocationSelect} />
                <PredictionChart location={selectedLocation} />
              </div>

              {/* Right Column */}
              <div className="space-y-6">
                <ENSOIndicator />
                <RiskAssessment location={selectedLocation} />
                <SeasonalOutlook location={selectedLocation} />

                {/* Quick Stats */}
                <div className="climate-card">
                  <h3 className="text-lg font-semibold text-white mb-4">Climate Quick Stats</h3>
                  <div className="space-y-3">
                    <StatItem icon={<Droplets className="w-5 h-5 text-blue-400" />} 
                             label="Avg Rainfall" value="850mm/year" />
                    <StatItem icon={<Thermometer className="w-5 h-5 text-red-400" />} 
                             label="Avg Temperature" value="22°C" />
                    <StatItem icon={<Wind className="w-5 h-5 text-green-400" />} 
                             label="Wind Speed" value="12 km/h" />
                    <StatItem icon={<TrendingUp className="w-5 h-5 text-yellow-400" />} 
                             label="Trend" value="Warming +1.2°C" />
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Predictions Section */}
        {activeSection === 'predictions' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <PredictionChart location={selectedLocation} />
              <ForecastComparison location={selectedLocation} />
            </div>
            <SeasonalOutlook location={selectedLocation} />
          </motion.div>
        )}

        {/* Alerts Section */}
        {activeSection === 'alerts' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="max-w-3xl mx-auto"
          >
            <AlertsPanel location={selectedLocation} />
          </motion.div>
        )}

        {/* Analytics Section */}
        {activeSection === 'analytics' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >
            <div className="climate-card">
              <h3 className="text-lg font-semibold text-white mb-4">System Analytics</h3>
              <p className="text-slate-400">Analytics dashboard powered by Grafana. Access detailed metrics at <a href="/grafana" className="text-climate-blue hover:underline">/grafana</a></p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <PredictionChart location={selectedLocation} />
              <ForecastComparison location={selectedLocation} />
            </div>
          </motion.div>
        )}
      </main>
    </div>
  )
}

function StatCard({ icon, label, value, change, positive }: { 
  icon: React.ReactNode, 
  label: string, 
  value: string, 
  change: string,
  positive: boolean 
}) {
  return (
    <div className="climate-card">
      <div className="flex items-center justify-between mb-2">
        {icon}
        <span className={`text-xs font-medium ${positive ? 'text-green-400' : 'text-red-400'}`}>
          {change}
        </span>
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
      <p className="text-xs text-slate-400">{label}</p>
    </div>
  )
}

function StatItem({ icon, label, value }: { icon: React.ReactNode, label: string, value: string }) {
  return (
    <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
      <div className="flex items-center gap-3">
        {icon}
        <span className="text-sm text-slate-300">{label}</span>
      </div>
      <span className="text-sm font-semibold text-white">{value}</span>
    </div>
  )
}
