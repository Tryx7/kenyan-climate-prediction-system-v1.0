import type { Metadata } from 'next'
import './globals.css'
import { Toaster } from 'react-hot-toast'

export const metadata: Metadata = {
  title: 'Kenyan Climate & Weather Prediction System',
  description: 'AI-powered weather forecasting analyzing El Nino and La Nina impacts on Kenya',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-climate-dark">
        {children}
        <Toaster position="top-right" />
      </body>
    </html>
  )
}
