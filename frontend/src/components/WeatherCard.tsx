"use client"

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Cloud, Sun, CloudRain, Wind, Droplets, Thermometer, Eye } from 'lucide-react'
import { weatherApi } from '@/lib/api'
import toast from 'react-hot-toast'

interface WeatherData {
  location: string
  current: {
    temperature_2m: number
    relative_humidity_2m: number
    precipitation: number
    weather_code: number
    wind_speed_10m: number
    wind_direction_10m: number
    pressure_msl: number
    cloud_cover: number
  }
  coordinates: { lat: number; lon: number }
  region: string
}

export default function WeatherCard({ location }: { location: string }) {
  const [weather, setWeather] = useState<WeatherData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchWeather = async () => {
      setLoading(true)
      try {
        const response = await weatherApi.getCurrent(location)
        setWeather(response.data)
      } catch (error) {
        toast.error('Failed to fetch weather data')
        console.error(error)
      } finally {
        setLoading(false)
      }
    }

    fetchWeather()
  }, [location])

  if (loading) {
    return (
      <div className="climate-card animate-pulse">
        <div className="h-48 bg-slate-700 rounded-lg"></div>
      </div>
    )
  }

  if (!weather) return null

  const current = weather.current
  const weatherIcon = getWeatherIcon(current.weather_code)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="climate-card"
    >
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white">{weather.location}</h2>
          <p className="text-sm text-slate-400">{weather.region} Region</p>
          <p className="text-xs text-slate-500 mt-1">
            {weather.coordinates.lat.toFixed(4)}, {weather.coordinates.lon.toFixed(4)}
          </p>
        </div>
        <div className="text-right">
          <div className="text-5xl font-bold text-white">{Math.round(current.temperature_2m)}°C</div>
          <div className="flex items-center gap-2 mt-2 text-slate-300">
            {weatherIcon}
            <span className="text-sm">{getWeatherDescription(current.weather_code)}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <WeatherMetric 
          icon={<Droplets className="w-5 h-5 text-blue-400" />}
          label="Humidity"
          value={`${current.relative_humidity_2m}%`}
        />
        <WeatherMetric 
          icon={<Wind className="w-5 h-5 text-green-400" />}
          label="Wind"
          value={`${current.wind_speed_10m} km/h`}
        />
        <WeatherMetric 
          icon={<Eye className="w-5 h-5 text-yellow-400" />}
          label="Pressure"
          value={`${current.pressure_msl} hPa`}
        />
        <WeatherMetric 
          icon={<Cloud className="w-5 h-5 text-slate-400" />}
          label="Cloud Cover"
          value={`${current.cloud_cover}%`}
        />
      </div>
    </motion.div>
  )
}

function WeatherMetric({ icon, label, value }: { icon: React.ReactNode, label: string, value: string }) {
  return (
    <div className="bg-slate-800/50 rounded-lg p-3">
      <div className="flex items-center gap-2 mb-1">
        {icon}
        <span className="text-xs text-slate-400">{label}</span>
      </div>
      <p className="text-lg font-semibold text-white">{value}</p>
    </div>
  )
}

function getWeatherIcon(code: number) {
  if (code === 0) return <Sun className="w-8 h-8 text-yellow-400" />
  if (code <= 3) return <Cloud className="w-8 h-8 text-slate-400" />
  if (code <= 67) return <CloudRain className="w-8 h-8 text-blue-400" />
  return <Cloud className="w-8 h-8 text-slate-400" />
}

function getWeatherDescription(code: number) {
  const descriptions: Record<number, string> = {
    0: 'Clear sky',
    1: 'Mainly clear',
    2: 'Partly cloudy',
    3: 'Overcast',
    45: 'Foggy',
    48: 'Depositing rime fog',
    51: 'Light drizzle',
    53: 'Moderate drizzle',
    55: 'Dense drizzle',
    61: 'Slight rain',
    63: 'Moderate rain',
    65: 'Heavy rain',
    71: 'Slight snow',
    73: 'Moderate snow',
    75: 'Heavy snow',
  }
  return descriptions[code] || 'Unknown'
}
