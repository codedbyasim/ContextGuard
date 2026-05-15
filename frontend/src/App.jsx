/**
 * ContextGuard Dashboard — Main App
 * Owner: [Developer name]
 * Two tabs: Threat Feed | OAuth Apps
 */

import { useState } from 'react'
import ThreatFeed from './ThreatFeed'
import OAuthApps from './OAuthApps'

export default function App() {
  const [activeTab, setActiveTab] = useState('threats')

  return (
    <div className="min-h-screen bg-gray-950 text-white">

      {/* Header */}
      <header className="bg-gray-900 border-b border-blue-800 px-6 py-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div>
            <h1 className="text-2xl font-bold text-blue-400">ContextGuard</h1>
            <p className="text-gray-400 text-sm">Enterprise AI Security Monitor</p>
          </div>
          <span className="text-xs text-gray-500 bg-gray-800 px-3 py-1 rounded-full">
            Live — polling every 10s
          </span>
        </div>
      </header>

      {/* Tabs */}
      <nav className="bg-gray-900 border-b border-gray-800 px-6">
        <div className="max-w-7xl mx-auto flex gap-6">
          {['threats', 'apps'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-gray-400 hover:text-white'
              }`}
            >
              {tab === 'threats' ? '🚨 Threat Feed' : '🔑 OAuth Apps'}
            </button>
          ))}
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-6 py-6">
        {activeTab === 'threats' ? <ThreatFeed /> : <OAuthApps />}
      </main>
    </div>
  )
}
