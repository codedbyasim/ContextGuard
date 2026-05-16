// ThreatFeed.jsx
import { useState, useEffect } from 'react'
import axios from 'axios'
import { ShieldAlert, AlertTriangle, Info, CheckCircle2, FileText, Download, Activity } from 'lucide-react'

import { jsPDF } from "jspdf"

const API = import.meta.env.DEV ? 'http://localhost:3000' : ''

const SEVERITY_STYLES = {
  CRITICAL: { icon: ShieldAlert, color: 'text-rose-500', bg: 'bg-rose-500/10', border: 'border-rose-500/30' },
  HIGH: { icon: AlertTriangle, color: 'text-orange-500', bg: 'bg-orange-500/10', border: 'border-orange-500/30' },
  MEDIUM: { icon: Info, color: 'text-amber-400', bg: 'bg-amber-400/10', border: 'border-amber-400/30' },
  LOW: { icon: CheckCircle2, color: 'text-emerald-500', bg: 'bg-emerald-500/10', border: 'border-emerald-500/30' },
  UNKNOWN: { icon: Activity, color: 'text-slate-400', bg: 'bg-slate-800/50', border: 'border-slate-700' }
}

export default function ThreatFeed() {
  const [events, setEvents] = useState([])
  const [stats, setStats] = useState(null)
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(false)

  const fetchData = async () => {
    try {
      const [eventsRes, statsRes] = await Promise.all([
        axios.get(`${API}/api/events?hours=24`),
        axios.get(`${API}/api/stats`)
      ])
      setEvents(eventsRes.data.events || [])
      setStats(statsRes.data)
    } catch (error) {
      console.error("Failed to fetch feed data", error)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 10000)
    return () => clearInterval(interval)
  }, [])

  const generateReport = async () => {
    setLoading(true)
    try {
      const res = await axios.get(`${API}/api/report`)
      setReport(res.data.report)
    } catch (e) {
      console.error("Failed to generate report", e)
    }
    setLoading(false)
  }

  const downloadReport = () => {
    if (!report) return
    const doc = new jsPDF()
    doc.setFont("helvetica", "normal")
    doc.setFontSize(10)
    const splitText = doc.splitTextToSize(report, 180)
    
    // Add text with simple pagination
    let y = 15;
    for (let i = 0; i < splitText.length; i++) {
      if (y > 280) {
        doc.addPage()
        y = 15;
      }
      doc.text(splitText[i], 15, y)
      y += 5;
    }
    
    doc.save(`contextguard-report-${new Date().toISOString().slice(0,10)}.pdf`)
  }

  return (
    <div className="space-y-8">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { label: 'OAuth Apps Monitored', value: stats?.total_apps || 0, color: 'from-blue-600/10 to-blue-900/20', text: 'text-blue-400' },
          { label: 'Critical / High Threats', value: (stats?.critical_apps || 0) + (stats?.high_risk_apps || 0), color: 'from-rose-600/10 to-rose-900/20', text: 'text-rose-400' },
          { label: 'Events Intercepted (24h)', value: stats?.total_events_24h || 0, color: 'from-emerald-600/10 to-emerald-900/20', text: 'text-emerald-400' },
        ].map(stat => (
          <div key={stat.label} className={`relative overflow-hidden rounded-2xl bg-gradient-to-br ${stat.color} border border-slate-800 p-6 backdrop-blur-sm group hover:border-slate-700 transition-all`}>
            <div className="relative z-10">
              <div className={`text-5xl font-black tracking-tight ${stat.text}`}>{stat.value}</div>
              <div className="text-slate-400 font-medium mt-2">{stat.label}</div>
            </div>
            <div className="absolute -right-4 -bottom-4 w-28 h-28 bg-white/5 rounded-full blur-2xl group-hover:bg-white/10 transition-all"></div>
          </div>
        ))}
      </div>

      {/* Report Section */}
      <div className="bg-[#0f172a]/60 border border-slate-800 rounded-2xl p-6 backdrop-blur-md shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold text-slate-200">Compliance & Audit Report</h3>
            <p className="text-sm text-slate-400">Generate a SOC2/HIPAA ready PDF summary of the last 24 hours.</p>
          </div>
          <button
            onClick={generateReport}
            disabled={loading}
            className="flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:hover:bg-indigo-600 px-5 py-2.5 rounded-lg text-sm font-semibold transition-all shadow-[0_0_15px_rgba(79,70,229,0.3)] hover:shadow-[0_0_20px_rgba(79,70,229,0.5)]"
          >
            {loading ? (
              <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div><span>Analyzing with Gemini...</span></>
            ) : (
              <><FileText className="w-4 h-4" /><span>Generate Report</span></>
            )}
          </button>
        </div>
        
        {report && (
          <div className="mt-6 bg-[#020817] border border-slate-800 rounded-xl p-5 relative group animate-in slide-in-from-top-4 fade-in duration-300">
            <button className="absolute top-4 right-4 p-2 text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors opacity-0 group-hover:opacity-100" onClick={downloadReport} title="Download report">
              <Download className="w-4 h-4" />
            </button>
            <div className="flex items-center space-x-2 mb-4 border-b border-slate-800/80 pb-3">
              <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse shadow-[0_0_8px_rgba(99,102,241,0.8)]"></div>
              <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">Gemini Intelligence Summary</span>
            </div>
            <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap font-mono">{report}</p>
          </div>
        )}
      </div>

      {/* Events Feed */}
      <div>
        <h2 className="text-xl font-bold text-slate-200 mb-6 flex items-center">
          <Activity className="w-5 h-5 mr-2 text-blue-500" />
          Live DPI Interceptions
        </h2>
        {events.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 border border-slate-800 border-dashed rounded-2xl bg-[#0f172a]/30">
            <ShieldAlert className="w-12 h-12 text-slate-600 mb-4 opacity-50" />
            <p className="text-slate-400 font-medium text-lg">No malicious traffic detected.</p>
            <p className="text-sm text-slate-500 mt-2">Lobster Trap DPI is actively monitoring all AI agent traffic.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {events.map((event, idx) => {
              const style = SEVERITY_STYLES[event.severity] || SEVERITY_STYLES.UNKNOWN
              const Icon = style.icon
              return (
                <div key={idx} className={`relative overflow-hidden rounded-xl bg-[#0f172a]/80 border ${style.border} backdrop-blur-md transition-all hover:scale-[1.01] hover:shadow-lg duration-200`}>
                  <div className={`absolute top-0 left-0 w-1.5 h-full ${style.bg} border-l-2 ${style.border}`}></div>
                  <div className="p-5 pl-7">
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex items-center space-x-4">
                        <div className={`p-3 rounded-xl ${style.bg} shadow-inner`}>
                          <Icon className={`w-6 h-6 ${style.color}`} />
                        </div>
                        <div>
                          <h4 className="text-slate-100 font-bold text-lg">{event.policy_triggered}</h4>
                          <span className="text-xs text-slate-500 font-semibold uppercase tracking-wider">{new Date(event.timestamp).toLocaleString()}</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-black ${style.bg} ${style.color} uppercase tracking-wider border ${style.border} shadow-sm`}>
                          {event.severity}
                        </span>
                      </div>
                    </div>
                    <div className="mt-4 bg-[#020817] rounded-lg p-4 border border-slate-800/80 shadow-inner">
                      <p className="text-sm text-slate-300">
                        <span className="text-blue-500 font-mono text-xs font-bold mr-3 uppercase tracking-wider">[AI Insight]</span>
                        {event.alert_message}
                      </p>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
