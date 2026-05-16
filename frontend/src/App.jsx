import { useState, useEffect } from 'react'
import ThreatFeed from './ThreatFeed'
import OAuthApps from './OAuthApps'
import EnvGuardian from './EnvGuardian'
import RedTeamSimulator from './RedTeamSimulator'
import IncidentResponse from './IncidentResponse'
import axios from 'axios'
import { ShieldAlert, AppWindow, FileKey, Crosshair, Activity, LogOut, Menu, Bell, Shield, Wifi, WifiOff, Database, Lock, CheckCircle2 } from 'lucide-react'

const API = import.meta.env.DEV ? 'http://localhost:3000' : ''

export default function App() {
  const [activeTab, setActiveTab] = useState('threats')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [systemStatus, setSystemStatus] = useState(null)
  const [showLanding, setShowLanding] = useState(true)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await axios.get(`${API}/api/status`)
        setSystemStatus(res.data)
      } catch (e) {
        setSystemStatus(null)
      }
    }
    fetchStatus()
    const interval = setInterval(fetchStatus, 15000)
    return () => clearInterval(interval)
  }, [])

  const handleDisconnect = async () => {
    try {
      await axios.post(`${API}/api/workspace/disconnect`);
      setSystemStatus(prev => ({ ...prev, workspace: { ...prev.workspace, connected: false, mode: 'synthetic_demo' } }));
      setShowLanding(true);
    } catch(e) {
      console.error("Failed to disconnect", e)
    }
  }

  const TABS = [
    { id: 'threats', label: 'Threat Feed', icon: Activity },
    { id: 'apps', label: 'OAuth Apps', icon: AppWindow },
    { id: 'env', label: 'Env Guardian', icon: FileKey },
    { id: 'redteam', label: 'Red Team Simulator', icon: Crosshair },
    { id: 'response', label: 'Incident Response', icon: ShieldAlert },
  ]

  const renderContent = () => {
    switch(activeTab) {
      case 'threats': return <ThreatFeed />
      case 'apps': return <OAuthApps />
      case 'env': return <EnvGuardian />
      case 'redteam': return <RedTeamSimulator />
      case 'response': return <IncidentResponse />
      default: return null
    }
  }

  const wsConnected = systemStatus?.workspace?.connected
  const proxyOnline = systemStatus?.proxy?.online

  if (showLanding) {
    return (
      <div className="flex h-screen bg-[#020817] text-slate-100 flex-col items-center justify-center relative overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-blue-600/20 blur-[120px] rounded-full pointer-events-none"></div>
        <Shield className="w-24 h-24 text-blue-500 mb-8 drop-shadow-[0_0_20px_rgba(59,130,246,0.6)]" />
        <h1 className="text-5xl font-black mb-4 tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-500">ContextGuard</h1>
        <p className="text-xl text-slate-400 max-w-2xl text-center mb-12 leading-relaxed">Enterprise AI Security Platform. Monitor, inspect, and protect your organization from third-party AI supply-chain attacks.</p>
        
        <div className="flex items-center space-x-6 z-10">
          <button onClick={() => setShowLanding(false)} className="px-8 py-4 flex items-center bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold transition-all shadow-[0_0_20px_rgba(37,99,235,0.4)] hover:shadow-[0_0_30px_rgba(37,99,235,0.6)] hover:-translate-y-1">
            <Activity className="w-5 h-5 mr-3" /> Explore Demo Mode
          </button>
          <button onClick={() => { setShowLanding(false); setActiveTab('apps'); }} className="px-8 py-4 flex items-center bg-[#0f172a] hover:bg-slate-800 text-white border border-slate-700 rounded-xl font-bold transition-all hover:border-slate-500">
            <Lock className="w-5 h-5 mr-3" /> Connect Real Workspace
          </button>
        </div>

        <div className="absolute bottom-8 text-slate-500 text-sm flex items-center space-x-4">
          <span className="flex items-center"><CheckCircle2 className="w-4 h-4 mr-1 text-emerald-500" /> SOC2 Ready</span>
          <span className="w-1 h-1 rounded-full bg-slate-700"></span>
          <span className="flex items-center"><Shield className="w-4 h-4 mr-1 text-blue-500" /> AI-Powered Defense</span>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-[#020817] text-slate-100 font-sans overflow-hidden selection:bg-blue-500/30">
      {/* Sidebar */}
      <aside className={`transition-all duration-300 ease-in-out border-r border-slate-800/50 bg-[#0f172a]/80 backdrop-blur-xl ${sidebarOpen ? 'w-64' : 'w-20'} flex flex-col z-20`}>
        <div className="flex items-center h-16 px-4 border-b border-slate-800/50">
          <Shield className="w-8 h-8 text-blue-500 mr-3 flex-shrink-0 drop-shadow-[0_0_10px_rgba(59,130,246,0.5)]" />
          {sidebarOpen && (
            <span className="font-bold text-lg bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-400">
              ContextGuard
            </span>
          )}
        </div>
        
        <nav className="flex-1 py-6 px-3 space-y-2">
          {TABS.map(tab => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center px-3 py-3 rounded-xl transition-all duration-200 group ${
                  isActive 
                    ? 'bg-blue-600/10 text-blue-400 shadow-[0_0_15px_rgba(37,99,235,0.1)] border border-blue-500/20' 
                    : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                }`}
              >
                <Icon className={`w-5 h-5 flex-shrink-0 ${sidebarOpen ? 'mr-3' : 'mx-auto'} ${isActive ? 'text-blue-400' : 'text-slate-500 group-hover:text-slate-300 transition-colors'}`} />
                {sidebarOpen && <span className="font-medium whitespace-nowrap">{tab.label}</span>}
              </button>
            )
          })}
        </nav>

        {/* System Status Panel in sidebar */}
        {sidebarOpen && systemStatus && (
          <div className="px-4 pb-4 space-y-2">
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">System Status</p>
            <div className={`flex items-center space-x-2 text-xs rounded-lg px-3 py-2 border ${wsConnected ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-slate-800 border-slate-700 text-slate-400'}`}>
              <Database className="w-3.5 h-3.5 flex-shrink-0" />
              <span className="truncate">{wsConnected ? systemStatus.workspace.admin_email : 'Demo Mode'}</span>
            </div>
            <div className={`flex items-center space-x-2 text-xs rounded-lg px-3 py-2 border ${proxyOnline ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-slate-800/50 border-slate-700 text-slate-500'}`}>
              {proxyOnline ? <Wifi className="w-3.5 h-3.5 flex-shrink-0" /> : <WifiOff className="w-3.5 h-3.5 flex-shrink-0" />}
              <span>{proxyOnline ? 'Proxy Online' : 'Proxy Offline'}</span>
            </div>
          </div>
        )}

        <div className="p-4 border-t border-slate-800/50">
          <button onClick={handleDisconnect} className="w-full flex items-center px-3 py-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 rounded-lg transition-colors">
            <LogOut className={`w-5 h-5 flex-shrink-0 ${sidebarOpen ? 'mr-3' : 'mx-auto'}`} />
            {sidebarOpen && <span>Disconnect</span>}
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-slate-900/40 via-[#020817] to-[#020817]">
        {/* Top Navbar */}
        <header className="h-16 flex items-center justify-between px-6 border-b border-slate-800/50 bg-[#0f172a]/50 backdrop-blur-md z-10 shadow-sm">
          <div className="flex items-center">
            <button 
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="text-slate-400 hover:text-white mr-4 p-2 rounded-lg hover:bg-slate-800 transition-colors"
            >
              <Menu className="w-5 h-5" />
            </button>
            <h2 className="text-xl font-semibold text-slate-100 tracking-tight">
              {TABS.find(t => t.id === activeTab)?.label}
            </h2>
          </div>
          
          <div className="flex items-center space-x-3">
            {/* Real workspace status */}
            {systemStatus ? (
              <div className={`flex items-center space-x-2 rounded-full px-4 py-1.5 border text-xs font-bold tracking-wide uppercase ${
                wsConnected
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                  : 'bg-slate-900/80 border-slate-700 text-slate-400'
              }`}>
                <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.8)]' : 'bg-slate-500'}`}></div>
                <span>{wsConnected ? `Workspace: ${systemStatus.workspace.apps_in_db} Apps` : 'Demo Mode'}</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2 bg-slate-900/80 border border-slate-800 rounded-full px-4 py-1.5">
                <div className="w-2 h-2 rounded-full bg-slate-500"></div>
                <span className="text-xs font-bold tracking-wide text-slate-400 uppercase">Connecting...</span>
              </div>
            )}
            <button className="relative p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-full transition-colors">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-rose-500 rounded-full border-2 border-[#0f172a]"></span>
            </button>
            <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 border-2 border-slate-700 shadow-sm cursor-pointer hover:shadow-indigo-500/20 transition-all"></div>
          </div>
        </header>

        {/* Dynamic Content */}
        <main className="flex-1 overflow-y-auto p-6 scroll-smooth">
          <div className="max-w-[1400px] mx-auto animate-in fade-in duration-500">
            {renderContent()}
          </div>
        </main>
      </div>
    </div>
  )
}
