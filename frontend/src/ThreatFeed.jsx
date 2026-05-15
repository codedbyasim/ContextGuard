/**
 * Threat Feed Tab
 * Owner: [Developer name]
 * Shows DPI events from last 24h + compliance report button
 * TODO: implement polling and event display
 */

import { useState, useEffect } from 'react'
import axios from 'axios'

const API = 'http://localhost:3000'

const SEVERITY_COLORS = {
  CRITICAL: 'bg-red-900 text-red-300 border-red-700',
  HIGH:     'bg-orange-900 text-orange-300 border-orange-700',
  MEDIUM:   'bg-yellow-900 text-yellow-300 border-yellow-700',
  LOW:      'bg-green-900 text-green-300 border-green-700',
}

export default function ThreatFeed() {
  const [events, setEvents]   = useState([])
  const [report, setReport]   = useState(null)
  const [loading, setLoading] = useState(false)

  // TODO: fetch events every 10 seconds
  // useEffect(() => { ... }, [])

  const generateReport = async () => {
    setLoading(true)
    // TODO: call GET /api/report and set report state
    setLoading(false)
  }

  return (
    <div className="space-y-6">

      {/* Summary banner — TODO: fill with real counts */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Apps Scanned', value: '—', color: 'text-blue-400' },
          { label: 'Critical Apps', value: '—', color: 'text-red-400' },
          { label: 'Events (1h)',   value: '—', color: 'text-orange-400' },
        ].map(stat => (
          <div key={stat.label} className="bg-gray-900 rounded-lg p-4 border border-gray-800">
            <div className={`text-3xl font-bold ${stat.color}`}>{stat.value}</div>
            <div className="text-gray-400 text-sm mt-1">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Report button */}
      <button
        onClick={generateReport}
        disabled={loading}
        className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 px-4 py-2 rounded-lg text-sm font-medium"
      >
        {loading ? 'Generating...' : '📄 Generate Compliance Report'}
      </button>

      {/* Report modal — TODO: style this properly */}
      {report && (
        <div className="bg-gray-900 border border-blue-800 rounded-lg p-4">
          <h3 className="text-blue-400 font-bold mb-2">Compliance Report</h3>
          <pre className="text-gray-300 text-sm whitespace-pre-wrap">{report}</pre>
        </div>
      )}

      {/* Events list */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-3">DPI Events — Last 24h</h2>
        {events.length === 0 ? (
          <p className="text-gray-500 text-sm">No events yet. Waiting for Lobster Trap...</p>
        ) : (
          <div className="space-y-2">
            {events.map(event => (
              <div key={event.id} className={`border rounded-lg p-3 ${SEVERITY_COLORS[event.severity] || ''}`}>
                {/* TODO: render event details */}
                <pre className="text-xs">{JSON.stringify(event, null, 2)}</pre>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  )
}
