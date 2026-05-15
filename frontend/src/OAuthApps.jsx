/**
 * OAuth Apps Tab
 * Owner: Maira
 * Shows all scanned OAuth apps with risk scores + scan button
 * TODO: implement app list and chart
 */

import { useState, useEffect } from 'react'
import axios from 'axios'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const API = 'http://localhost:3000'

const RISK_COLORS = {
  CRITICAL: 'text-red-400 bg-red-950 border-red-800',
  HIGH:     'text-orange-400 bg-orange-950 border-orange-800',
  MEDIUM:   'text-yellow-400 bg-yellow-950 border-yellow-800',
  LOW:      'text-green-400 bg-green-950 border-green-800',
  UNKNOWN:  'text-gray-400 bg-gray-900 border-gray-700',
}

export default function OAuthApps() {
  const [apps, setApps]       = useState([])
  const [scanning, setScanning] = useState(false)

  // TODO: fetch apps on mount and every 10s

  const triggerScan = async () => {
    setScanning(true)
    // TODO: call POST /api/scan then refresh apps
    setScanning(false)
  }

  return (
    <div className="space-y-6">

      {/* Scan button */}
      <button
        onClick={triggerScan}
        disabled={scanning}
        className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 px-4 py-2 rounded-lg text-sm font-medium"
      >
        {scanning ? '🔍 Scanning...' : '🔍 Scan OAuth Apps Now'}
      </button>

      {/* Risk score chart — TODO: wire up real data */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
        <h3 className="text-white font-semibold mb-4">Risk Score Trends (Top 5 Apps)</h3>
        <div className="h-48 text-gray-500 text-sm flex items-center justify-center">
          TODO: add Recharts LineChart here
        </div>
      </div>

      {/* Apps list */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-3">Connected OAuth Applications</h2>
        {apps.length === 0 ? (
          <p className="text-gray-500 text-sm">No apps scanned yet. Click the scan button.</p>
        ) : (
          <div className="space-y-2">
            {apps.map(app => (
              <div key={app.id} className={`border rounded-lg p-4 ${RISK_COLORS[app.risk_category]}`}>
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-medium">{app.name}</h4>
                    <p className="text-sm opacity-75">{app.publisher}</p>
                    <p className="text-xs mt-1 opacity-60">{app.explanation}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold">{app.risk_score}</div>
                    <div className="text-xs font-medium">{app.risk_category}</div>
                    {app.is_ioc && (
                      <div className="text-xs text-red-300 mt-1">⚠️ IOC MATCH</div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  )
}
