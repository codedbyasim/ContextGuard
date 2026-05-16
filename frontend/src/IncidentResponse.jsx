import { useState, useEffect } from 'react'
import axios from 'axios'
import { ShieldAlert, AlertOctagon, CheckCircle2, ChevronRight, PlayCircle, Key } from 'lucide-react'

const API = import.meta.env.DEV ? 'http://localhost:3000' : ''

export default function IncidentResponse() {
  const [incidents, setIncidents] = useState([])
  const [selectedInc, setSelectedInc] = useState(null)
  const [actionLoading, setActionLoading] = useState(false)

  const fetchIncidents = async () => {
    try {
      const res = await axios.get(`${API}/api/incidents`)
      setIncidents(res.data.incidents || [])
    } catch (e) {
      console.error(e)
    }
  }

  useEffect(() => {
    fetchIncidents()
    const int = setInterval(fetchIncidents, 10000)
    return () => clearInterval(int)
  }, [])

  const advanceStep = async (incId, stepId) => {
    setActionLoading(true)
    try {
      await axios.post(`${API}/api/incidents/${incId}/advance`, { step_id: stepId })
      await fetchIncidents()
      if (selectedInc && selectedInc.id === incId) {
        const updated = await axios.get(`${API}/api/incidents/${incId}`)
        setSelectedInc(updated.data)
      }
    } catch (e) {
      console.error(e)
    }
    setActionLoading(false)
  }

  const rotateCredentials = async (incId) => {
    setActionLoading(true)
    try {
      await axios.post(`${API}/api/incidents/${incId}/rotate`)
      await fetchIncidents()
      if (selectedInc && selectedInc.id === incId) {
        const updated = await axios.get(`${API}/api/incidents/${incId}`)
        setSelectedInc(updated.data)
      }
    } catch (e) {
      console.error(e)
    }
    setActionLoading(false)
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-6">
      {/* Incident List */}
      <div className="w-1/3 bg-[#0f172a]/60 border border-slate-800 rounded-2xl flex flex-col overflow-hidden backdrop-blur-md">
        <div className="p-5 border-b border-slate-800 bg-slate-900/50">
          <h2 className="text-lg font-black text-slate-100 flex items-center">
            <AlertOctagon className="w-5 h-5 mr-2 text-rose-500" />
            Active Incidents
          </h2>
        </div>
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {incidents.length === 0 ? (
            <p className="text-center text-slate-500 mt-10 text-sm">No incidents reported.</p>
          ) : incidents.map(inc => (
            <button
              key={inc.id}
              onClick={() => setSelectedInc(inc)}
              className={`w-full text-left p-4 rounded-xl border transition-all ${
                selectedInc?.id === inc.id 
                  ? 'bg-blue-600/10 border-blue-500/30 text-blue-100' 
                  : 'bg-slate-900/50 border-slate-800 text-slate-300 hover:border-slate-700 hover:bg-slate-800/50'
              }`}
            >
              <div className="flex justify-between items-start mb-2">
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                  inc.severity === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400' : 'bg-orange-500/20 text-orange-400'
                }`}>
                  {inc.severity}
                </span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                  inc.status === 'resolved' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-700 text-slate-300'
                }`}>
                  {inc.status}
                </span>
              </div>
              <h4 className="font-bold text-sm line-clamp-2">{inc.title}</h4>
              <p className="text-xs text-slate-500 mt-2">{new Date(inc.created_at).toLocaleString()}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Incident Details & Playbook */}
      <div className="flex-1 bg-[#0f172a]/80 border border-slate-800 rounded-2xl overflow-y-auto backdrop-blur-md p-6">
        {selectedInc ? (
          <div className="animate-in fade-in">
            <div className="flex justify-between items-start border-b border-slate-800 pb-6 mb-6">
              <div>
                <h2 className="text-2xl font-black text-slate-100">{selectedInc.title}</h2>
                <div className="flex space-x-4 mt-3 text-sm text-slate-400">
                  <span>ID: INC-{selectedInc.id.toString().padStart(4, '0')}</span>
                  <span>Event ID: {selectedInc.event_id}</span>
                </div>
              </div>
              {selectedInc.status === 'resolved' && (
                <div className="bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 px-4 py-2 rounded-lg flex items-center font-bold">
                  <CheckCircle2 className="w-5 h-5 mr-2" />
                  Resolved
                </div>
              )}
            </div>

            <div className="mb-8">
              <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-4">AI Event Summary</h3>
              <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 text-sm text-slate-300 leading-relaxed font-mono">
                {JSON.stringify(selectedInc.event_summary, null, 2)}
              </div>
            </div>

            <div>
              <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-4">Remediation Playbook</h3>
              <div className="space-y-4">
                {selectedInc.steps?.map((step, idx) => {
                  const isCompleted = step.status === 'completed';
                  const isCurrent = idx + 1 === selectedInc.current_step && selectedInc.status !== 'resolved';
                  
                  return (
                    <div key={step.id} className={`p-4 rounded-xl border ${
                      isCompleted ? 'bg-emerald-500/5 border-emerald-500/20' : 
                      isCurrent ? 'bg-blue-600/10 border-blue-500/30 shadow-[0_0_15px_rgba(37,99,235,0.1)]' : 
                      'bg-slate-900/50 border-slate-800 opacity-50'
                    }`}>
                      <div className="flex items-start">
                        <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold mr-4 mt-0.5 ${
                          isCompleted ? 'bg-emerald-500 text-white' : 
                          isCurrent ? 'bg-blue-500 text-white' : 'bg-slate-700 text-slate-400'
                        }`}>
                          {isCompleted ? <CheckCircle2 className="w-4 h-4" /> : idx + 1}
                        </div>
                        <div className="flex-1">
                          <h4 className={`font-bold ${isCurrent ? 'text-blue-100' : 'text-slate-200'}`}>{step.title}</h4>
                          <p className="text-sm text-slate-400 mt-1">{step.description}</p>
                          
                          {isCurrent && (
                            <div className="mt-4 flex space-x-3">
                              {step.action_type === 'rotate_credentials' && (
                                <button 
                                  onClick={() => rotateCredentials(selectedInc.id)}
                                  disabled={actionLoading}
                                  className="flex items-center bg-rose-600 hover:bg-rose-500 text-white px-4 py-2 rounded-lg text-sm font-bold transition disabled:opacity-50"
                                >
                                  <Key className="w-4 h-4 mr-2" />
                                  1-Click Rotate Keys
                                </button>
                              )}
                              <button 
                                onClick={() => advanceStep(selectedInc.id, step.id)}
                                disabled={actionLoading}
                                className="flex items-center bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-bold transition disabled:opacity-50"
                              >
                                Mark Complete <ChevronRight className="w-4 h-4 ml-1" />
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-slate-500">
            <ShieldAlert className="w-16 h-16 mb-4 opacity-20" />
            <p className="text-lg">Select an incident to view details</p>
          </div>
        )}
      </div>
    </div>
  )
}
