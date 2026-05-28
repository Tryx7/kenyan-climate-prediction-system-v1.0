"use client"

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line, Bar } from 'react-chartjs-2'
import { predictionsApi } from '@/lib/api'
import { Droplets, Thermometer } from 'lucide-react'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface PredictionData {
  rainfall: {
    monthly_breakdown: Array<{ month: number; predicted_mm: number; confidence: number }>
    total_predicted_mm: number
  }
  temperature: {
    monthly_breakdown: Array<{ month: number; predicted_temp_c: number; anomaly_c: number }>
  }
}

export default function PredictionChart({ location }: { location: string }) {
  const [data, setData] = useState<PredictionData | null>(null)
  const [activeTab, setActiveTab] = useState<'rainfall' | 'temperature'>('rainfall')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchPredictions = async () => {
      setLoading(true)
      try {
        const [rainfallRes, tempRes] = await Promise.all([
          predictionsApi.getRainfall(location, 6),
          predictionsApi.getTemperature(location, 6)
        ])

        setData({
          rainfall: rainfallRes.data,
          temperature: tempRes.data
        })
      } catch (error) {
        console.error('Prediction fetch error:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchPredictions()
  }, [location])

  if (loading) {
    return (
      <div className="climate-card animate-pulse">
        <div className="h-64 bg-slate-700 rounded-lg"></div>
      </div>
    )
  }

  if (!data) return null

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

  const rainfallData = {
    labels: data.rainfall.monthly_breakdown.map(m => months[m.month - 1]),
    datasets: [
      {
        label: 'Predicted Rainfall (mm)',
        data: data.rainfall.monthly_breakdown.map(m => m.predicted_mm),
        backgroundColor: 'rgba(14, 165, 233, 0.5)',
        borderColor: 'rgba(14, 165, 233, 1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4
      }
    ]
  }

  const temperatureData = {
    labels: data.temperature.monthly_breakdown.map(m => months[m.month - 1]),
    datasets: [
      {
        label: 'Predicted Temperature (°C)',
        data: data.temperature.monthly_breakdown.map(m => m.predicted_temp_c),
        borderColor: 'rgba(239, 68, 68, 1)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4
      },
      {
        label: 'Anomaly (°C)',
        data: data.temperature.monthly_breakdown.map(m => m.anomaly_c),
        borderColor: 'rgba(245, 158, 11, 1)',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        borderWidth: 2,
        borderDash: [5, 5],
        fill: false,
        tension: 0.4
      }
    ]
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: '#94a3b8' }
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(148, 163, 184, 0.1)' },
        ticks: { color: '#94a3b8' }
      },
      y: {
        grid: { color: 'rgba(148, 163, 184, 0.1)' },
        ticks: { color: '#94a3b8' }
      }
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="climate-card"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white">Climate Predictions (6 Months)</h3>
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('rainfall')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-colors ${
              activeTab === 'rainfall' 
                ? 'bg-climate-blue text-white' 
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            <Droplets className="w-4 h-4" />
            Rainfall
          </button>
          <button
            onClick={() => setActiveTab('temperature')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-colors ${
              activeTab === 'temperature' 
                ? 'bg-red-500 text-white' 
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            <Thermometer className="w-4 h-4" />
            Temperature
          </button>
        </div>
      </div>

      <div className="h-64">
        {activeTab === 'rainfall' ? (
          <Line data={rainfallData} options={chartOptions} />
        ) : (
          <Line data={temperatureData} options={chartOptions} />
        )}
      </div>

      <div className="mt-4 grid grid-cols-3 gap-4">
        <div className="bg-slate-800/50 rounded-lg p-3 text-center">
          <p className="text-xs text-slate-400">Total Rainfall</p>
          <p className="text-lg font-bold text-climate-blue">{data.rainfall.total_predicted_mm}mm</p>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-3 text-center">
          <p className="text-xs text-slate-400">Avg Temperature</p>
          <p className="text-lg font-bold text-red-400">
            {Math.round(data.temperature.monthly_breakdown.reduce((a, b) => a + b.predicted_temp_c, 0) / data.temperature.monthly_breakdown.length)}°C
          </p>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-3 text-center">
          <p className="text-xs text-slate-400">Confidence</p>
          <p className="text-lg font-bold text-green-400">
            {Math.round(data.rainfall.monthly_breakdown.reduce((a, b) => a + b.confidence, 0) / data.rainfall.monthly_breakdown.length * 100)}%
          </p>
        </div>
      </div>
    </motion.div>
  )
}
