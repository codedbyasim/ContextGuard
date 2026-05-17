import { useState, useEffect } from 'react'
import ThreatFeed from './ThreatFeed'
import OAuthApps from './OAuthApps'
import EnvGuardian from './EnvGuardian'
import RedTeamSimulator from './RedTeamSimulator'
import IncidentResponse from './IncidentResponse'
import { Routes, Route, useNavigate, useLocation, Link, Navigate, useParams } from 'react-router-dom'
import axios from 'axios'
import { useAuth, API } from './auth'
import { LoginPage, SignupPage } from './AuthPages'
import {
  ShieldAlert, AppWindow, FileKey, Crosshair, Activity,
  LogOut, Menu, Bell, Shield, Wifi, WifiOff, Database,
  Lock, CheckCircle2, X, ChevronRight, ArrowRight, ExternalLink,
  Eye, Zap, Globe, Users, Check,
  AlertTriangle, BarChart3, Server
} from 'lucide-react'

/* ─── AUTH ROUTES ─────────────────────────────────────────────── */
function AuthLoadingScreen() {
  return (
    <div className="min-h-screen bg-[#09090b] flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-blue-500/20 border-t-blue-500 rounded-full animate-spin" />
    </div>
  )
}

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  const location = useLocation()
  if (loading) return <AuthLoadingScreen />
  if (!user) return <Navigate to="/login" state={{ from: location }} replace />
  return children
}

function GuestRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <AuthLoadingScreen />
  if (user) return <Navigate to="/dashboard/threats" replace />
  return children
}

function useGoDashboard() {
  const navigate = useNavigate()
  const { user } = useAuth()
  return () => navigate(user ? '/dashboard/threats' : '/login')
}

function useGoSignup() {
  const navigate = useNavigate()
  const { user } = useAuth()
  return () => navigate(user ? '/dashboard/threats' : '/signup')
}

function MarketingHeaderActions() {
  const navigate = useNavigate()
  const { user } = useAuth()
  if (user) {
    return (
      <button onClick={() => navigate('/dashboard/threats')} className="px-4 py-2 text-sm bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium transition-colors">
        Open Dashboard
      </button>
    )
  }
  return (
    <div className="flex items-center gap-2">
      <button onClick={() => navigate('/login')} className="px-4 py-2 text-sm text-zinc-300 hover:text-zinc-100 transition-colors">Sign in</button>
      <button onClick={() => navigate('/signup')} className="px-4 py-2 text-sm bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium transition-colors">Get started</button>
    </div>
  )
}

/* ─── FOOTER ──────────────────────────────────────────────────── */
function Footer({ minimal }) {
  const navigate = useNavigate()
  if (minimal) return (
    <footer className="border-t border-zinc-800/60 py-6 px-6 text-center">
      <p className="text-xs text-zinc-600">© 2025 ContextGuard. All rights reserved.</p>
    </footer>
  )
  return (
    <footer className="border-t border-zinc-800/60 bg-zinc-900/20 px-6 py-14">
      <div className="max-w-5xl mx-auto grid md:grid-cols-4 gap-10">
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Shield className="w-5 h-5 text-blue-500" />
            <span className="font-semibold text-zinc-100">ContextGuard</span>
          </div>
          <p className="text-sm text-zinc-500 leading-relaxed">Enterprise AI security platform. Monitor, inspect, and protect your AI supply chain.</p>
        </div>
        {[
          { title: 'Product', links: ['Features', 'Pricing', 'Documentation', 'Changelog'] },
          { title: 'Company', links: ['About', 'Blog', 'Careers', 'Contact'] },
          { title: 'Legal', links: ['Privacy', 'Terms', 'Security', 'Cookie Policy'] },
        ].map(col => (
          <div key={col.title}>
            <h4 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-4">{col.title}</h4>
            <ul className="space-y-2.5">
              {col.links.map(link => (
                <li key={link}>
                  <button
                    onClick={() => { if (link === 'Pricing') navigate('/pricing'); if (link === 'About') navigate('/about'); if (link === 'Features') navigate('/') }}
                    className="text-sm text-zinc-500 hover:text-zinc-300 transition-colors"
                  >{link}</button>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="max-w-5xl mx-auto mt-10 pt-8 border-t border-zinc-800/60 flex flex-col sm:flex-row items-center justify-between gap-4">
        <p className="text-xs text-zinc-600">© 2025 ContextGuard. All rights reserved.</p>
        <div className="flex items-center gap-4">
          {[ExternalLink, ExternalLink, ExternalLink].map((Icon, i) => (
            <button key={i} className="text-zinc-600 hover:text-zinc-400 transition-colors"><Icon className="w-4 h-4" /></button>
          ))}
        </div>
      </div>
    </footer>
  )
}

/* ─── ABOUT PAGE ─────────────────────────────────────────────── */
function AboutPage() {
  const navigate = useNavigate()
  const goSignup = useGoSignup()
  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-100 font-sans">
      <header className="fixed top-0 left-0 right-0 z-50 border-b border-zinc-800/60 bg-[#09090b]/90 backdrop-blur-md">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <button onClick={() => navigate('/')} className="flex items-center gap-2.5">
            <Shield className="w-6 h-6 text-blue-500" />
            <span className="font-semibold text-zinc-100 tracking-tight">ContextGuard</span>
          </button>
          <MarketingHeaderActions />
        </div>
      </header>
      <div className="pt-24 md:pt-28 pb-16 md:pb-20 px-4 sm:px-6">
        <div className="max-w-4xl mx-auto">
          <button onClick={() => navigate('/')} className="flex items-center gap-2 text-sm text-zinc-500 hover:text-zinc-300 transition-colors mb-8 md:mb-10">
            <ChevronRight className="w-4 h-4 rotate-180" /> Back to home
          </button>
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-zinc-100 mb-4 md:mb-6">About ContextGuard</h1>
          <p className="text-base md:text-lg lg:text-xl text-zinc-400 leading-relaxed mb-10 md:mb-12">
            ContextGuard was built to make AI safe for everyone. We noticed that companies were using AI apps without knowing if they were safe. We built this tool to fix that problem easily.
          </p>
          <div className="grid md:grid-cols-2 gap-6 mb-16">
            {[
              { icon: Shield, title: 'Our Goal', desc: 'Make sure every company can use AI safely, even if they don\'t have a big security team.' },
              { icon: Eye, title: 'Our Dream', desc: 'A future where you know exactly what your AI apps are doing, without any hidden surprises.' },
              { icon: Zap, title: 'How We Do It', desc: 'We check your traffic safely in the background. You don\'t need to change any of your code.' },
              { icon: Globe, title: 'What We Cover', desc: 'We protect your Google Workspace, passwords, and the messages you send to AI.' },
            ].map(item => (
              <div key={item.title} className="p-6 rounded-xl border border-zinc-800 bg-zinc-900/40">
                <item.icon className="w-5 h-5 text-blue-400 mb-3" />
                <h3 className="font-semibold text-zinc-100 mb-2">{item.title}</h3>
                <p className="text-sm text-zinc-500 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
          <div className="border-t border-zinc-800 pt-12 mb-12">
            <h2 className="text-2xl font-bold text-zinc-100 mb-8">The problem we solve</h2>
            <div className="space-y-6">
              {[
                { title: 'AI Apps are risky', desc: 'Many AI apps ask for too much access. A bad app can read your private emails and steal your data.' },
                { title: 'Attacks are hard to see', desc: 'Some AI tools look safe but secretly steal your passwords. You wouldn\'t even know it happened.' },
                { title: 'Fixing problems is hard', desc: 'Most companies don\'t have an easy way to stop these bad AI tools when they attack.' },
              ].map((item, i) => (
                <div key={i} className="flex gap-4">
                  <div className="w-6 h-6 rounded-full bg-blue-600/20 border border-blue-500/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <AlertTriangle className="w-3 h-3 text-blue-400" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-zinc-200 mb-1">{item.title}</h4>
                    <p className="text-sm text-zinc-500 leading-relaxed">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="bg-zinc-900/60 border border-zinc-800 rounded-xl p-8 text-center">
            <h3 className="text-xl font-bold text-zinc-100 mb-3">Built for your team</h3>
            <p className="text-zinc-400 mb-6 text-sm">ContextGuard works with your current setup. No need to change anything.</p>
            <button onClick={goSignup} className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium transition-colors inline-flex items-center gap-2">
              See it in action <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
      <Footer onNavigate={() => {}} minimal />
    </div>
  )
}

/* ─── PRICING PAGE ───────────────────────────────────────────── */
function PricingPage() {
  const navigate = useNavigate()
  const goSignup = useGoSignup()
  const [annual, setAnnual] = useState(true)
  const plans = [
    {
      name: 'Starter', price: 0, period: 'Free forever',
      desc: 'For individuals and small teams exploring AI security.',
      features: ['Up to 5 OAuth apps', 'Basic threat feed', '7-day event history', 'Community support'],
      cta: 'Get started free', highlighted: false,
    },
    {
      name: 'Professional', price: annual ? 49 : 59, period: annual ? '/month, billed annually' : '/month',
      desc: 'For growing teams that need real-time protection and compliance.',
      features: ['Unlimited OAuth apps', 'Real-time DPI monitoring', '90-day event history', 'Gemini AI reports', 'Red team simulator', 'Incident response playbooks', 'SOC2 audit exports', 'Email support'],
      cta: 'Start free trial', highlighted: true,
    },
    {
      name: 'Enterprise', price: 'Custom', period: '',
      desc: 'For organizations with advanced compliance and scale requirements.',
      features: ['Everything in Professional', 'Custom DPI policies', 'SSO / SAML integration', 'Dedicated workspace tenant', 'SLA guarantees', 'On-prem deployment option', 'Dedicated security engineer', 'Priority support 24/7'],
      cta: 'Contact sales', highlighted: false,
    },
  ]
  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-100 font-sans">
      <header className="fixed top-0 left-0 right-0 z-50 border-b border-zinc-800/60 bg-[#09090b]/90 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <button onClick={() => navigate('/')} className="flex items-center gap-2.5">
            <Shield className="w-6 h-6 text-blue-500" />
            <span className="font-semibold text-zinc-100 tracking-tight">ContextGuard</span>
          </button>
          <MarketingHeaderActions />
        </div>
      </header>
      <div className="pt-24 md:pt-28 pb-16 md:pb-20 px-4 sm:px-6">
        <div className="max-w-6xl mx-auto">
          <button onClick={() => navigate('/')} className="flex items-center gap-2 text-sm text-zinc-500 hover:text-zinc-300 transition-colors mb-8 md:mb-10">
            <ChevronRight className="w-4 h-4 rotate-180" /> Back to home
          </button>
          <div className="text-center mb-10 md:mb-14">
            <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-zinc-100 mb-4">Simple, transparent pricing</h1>
            <p className="text-base md:text-lg text-zinc-400 mb-8">Start free. Scale as your security needs grow.</p>
            <div className="inline-flex items-center gap-0 bg-zinc-900 border border-zinc-800 rounded-lg p-1">
              <button onClick={() => setAnnual(false)} className={`px-4 py-2 text-sm rounded-md transition-colors ${!annual ? 'bg-zinc-700 text-zinc-100' : 'text-zinc-400 hover:text-zinc-200'}`}>Monthly</button>
              <button onClick={() => setAnnual(true)} className={`px-4 py-2 text-sm rounded-md transition-colors flex items-center gap-2 ${annual ? 'bg-zinc-700 text-zinc-100' : 'text-zinc-400 hover:text-zinc-200'}`}>
                Annual <span className="text-xs bg-emerald-500/20 text-emerald-400 px-1.5 py-0.5 rounded">Save 17%</span>
              </button>
            </div>
          </div>
          <div className="grid md:grid-cols-3 gap-4 mb-20">
            {plans.map(plan => (
              <div key={plan.name} className={`rounded-xl p-6 border flex flex-col relative ${plan.highlighted ? 'border-blue-500/40 bg-blue-600/5' : 'border-zinc-800 bg-zinc-900/40'}`}>
                {plan.highlighted && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-blue-600 rounded-full text-xs font-semibold text-white">Most popular</div>
                )}
                <div className="mb-6">
                  <h3 className="font-semibold text-zinc-100 mb-1">{plan.name}</h3>
                  <p className="text-xs text-zinc-500 mb-4">{plan.desc}</p>
                  <div className="flex items-baseline gap-1">
                    {typeof plan.price === 'number'
                      ? <><span className="text-3xl font-bold text-zinc-100">${plan.price}</span><span className="text-sm text-zinc-500">{plan.period}</span></>
                      : <span className="text-3xl font-bold text-zinc-100">{plan.price}</span>}
                  </div>
                </div>
                <ul className="space-y-2.5 flex-1 mb-6">
                  {plan.features.map(f => (
                    <li key={f} className="flex items-start gap-2.5 text-sm">
                      <Check className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                      <span className="text-zinc-400">{f}</span>
                    </li>
                  ))}
                </ul>
                <button onClick={goSignup} className={`w-full py-2.5 rounded-lg text-sm font-medium transition-colors ${plan.highlighted ? 'bg-blue-600 hover:bg-blue-500 text-white' : 'bg-zinc-800 hover:bg-zinc-700 text-zinc-100 border border-zinc-700'}`}>
                  {plan.cta}
                </button>
              </div>
            ))}
          </div>
          <div className="mt-4">
            <h2 className="text-2xl font-bold text-zinc-100 mb-8 text-center">Frequently asked questions</h2>
            <div className="grid md:grid-cols-2 gap-5 max-w-3xl mx-auto">
              {[
                { q: 'Do I need to change my code?', a: 'No. ContextGuard works in the background without changing anything.' },
                { q: 'Is my data safe?', a: 'Yes. We only check data in memory and never save it to disks.' },
                { q: 'Which AI platforms work with this?', a: 'Any AI platform like ChatGPT, Google Gemini, or Claude.' },
                { q: 'Can I install this on my own servers?', a: 'Yes. Enterprise plans allow you to host it completely on your own machines.' },
              ].map(item => (
                <div key={item.q} className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/40">
                  <h4 className="font-semibold text-zinc-200 mb-2 text-sm">{item.q}</h4>
                  <p className="text-sm text-zinc-500 leading-relaxed">{item.a}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      <Footer onNavigate={() => {}} minimal />
    </div>
  )
}

/* ─── LANDING PAGE ───────────────────────────────────────────── */
function LandingPage() {
  const navigate = useNavigate()
  const goSignup = useGoSignup()
  const { user } = useAuth()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-100 font-sans">
      {/* Navbar */}
      <header className="fixed top-0 left-0 right-0 z-50 border-b border-zinc-800/60 bg-[#09090b]/90 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Shield className="w-6 h-6 text-blue-500" />
            <span className="font-semibold text-zinc-100 tracking-tight">ContextGuard</span>
          </div>
          <nav className="hidden md:flex items-center gap-1">
            <button onClick={() => navigate('/')} className="px-4 py-2 text-sm text-zinc-400 hover:text-zinc-100 transition-colors rounded-md hover:bg-zinc-800/50">Product</button>
            <button onClick={() => navigate('/about')} className="px-4 py-2 text-sm text-zinc-400 hover:text-zinc-100 transition-colors rounded-md hover:bg-zinc-800/50">About</button>
            <button onClick={() => navigate('/pricing')} className="px-4 py-2 text-sm text-zinc-400 hover:text-zinc-100 transition-colors rounded-md hover:bg-zinc-800/50">Pricing</button>
          </nav>
          <div className="hidden md:flex items-center gap-3">
            <MarketingHeaderActions />
          </div>
          <button className="md:hidden p-2 text-zinc-400" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-zinc-800 bg-[#09090b] px-6 py-4 space-y-1">
            <button onClick={() => navigate('/about')} className="block w-full text-left px-3 py-2.5 text-sm text-zinc-400 hover:text-zinc-100 rounded-md">About</button>
            <button onClick={() => navigate('/pricing')} className="block w-full text-left px-3 py-2.5 text-sm text-zinc-400 hover:text-zinc-100 rounded-md">Pricing</button>
            <div className="pt-3 flex flex-col gap-2">
              <MarketingHeaderActions />
            </div>
          </div>
        )}
      </header>

      {/* Hero */}
      <section className="pt-32 pb-20 md:pt-40 md:pb-28 lg:pt-48 lg:pb-36 px-4 sm:px-6 text-center relative overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] md:w-[600px] md:h-[600px] bg-blue-600/8 blur-[100px] md:blur-[140px] rounded-full" />
        </div>
        <div className="max-w-4xl lg:max-w-5xl mx-auto relative">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-zinc-900 border border-zinc-700/60 rounded-full text-xs sm:text-sm text-zinc-400 mb-6 md:mb-8">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            Protected by Smart AI Security
          </div>
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl xl:text-8xl font-bold text-zinc-100 tracking-tight leading-tight mb-4 md:mb-6">
            Simple Security for<br className="hidden sm:block" /><span className="text-blue-400"> Your Workspace</span>
          </h1>
          <p className="text-base sm:text-lg md:text-xl lg:text-2xl text-zinc-400 leading-relaxed max-w-2xl lg:max-w-3xl mx-auto mb-8 md:mb-10">
            ContextGuard checks your Google Workspace and protects your company from bad AI apps easily and safely.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4">
            <button onClick={goSignup} className="w-full sm:w-auto px-6 py-3 sm:px-8 sm:py-4 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium text-base sm:text-lg transition-colors flex items-center justify-center gap-2">
              <Lock className="w-5 h-5" /> {user ? 'Open Dashboard' : 'Get started free'}
            </button>
            {!user && (
              <button onClick={() => navigate('/login')} className="w-full sm:w-auto px-6 py-3 sm:px-8 sm:py-4 border border-zinc-700 hover:border-zinc-500 text-zinc-200 rounded-lg font-medium text-base sm:text-lg transition-colors">
                Sign in
              </button>
            )}
          </div>
          <p className="mt-6 text-xs text-zinc-500">No credit card required · Safe & Secure · AI-Powered</p>
        </div>
      </section>

      {/* Stats */}
      <section className="border-y border-zinc-800/60 bg-zinc-900/30 py-8 md:py-12 px-4 sm:px-6">
        <div className="max-w-6xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-8 text-center">
          {[
            { value: '99.9%', label: 'Threats Blocked' },
            { value: '<2ms', label: 'Fast Checking' },
            { value: '500+', label: 'Security Rules' },
            { value: 'SOC2', label: 'Safe & Secure' },
          ].map(s => (
            <div key={s.label} className="p-2">
              <div className="text-3xl md:text-4xl lg:text-5xl font-bold text-zinc-100 mb-1 md:mb-2">{s.value}</div>
              <div className="text-xs sm:text-sm md:text-base text-zinc-500">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="py-20 md:py-32 px-4 sm:px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12 md:mb-20">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-zinc-100 mb-4 md:mb-6">Everything you need to stay safe</h2>
            <p className="text-base md:text-lg text-zinc-400 max-w-2xl mx-auto">A complete tool to watch your apps, stop bad attacks, and fix problems across your whole team.</p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
            {[
              { icon: Activity, title: 'Live Alerts', desc: 'See every blocked attack easily as it happens.' },
              { icon: AppWindow, title: 'App Checker', desc: 'Find out which connected apps are unsafe and asking for too much.' },
              { icon: FileKey, title: 'Secret Guard', desc: 'Protect your passwords and API keys from leaking.' },
              { icon: Crosshair, title: 'Attack Tester', desc: 'Test your system safely with fake attacks to see if it works.' },
              { icon: ShieldAlert, title: 'Fix Problems', desc: 'Get easy steps to solve any security problem in one click.' },
              { icon: BarChart3, title: 'Simple Reports', desc: 'Get easy-to-read PDF reports created by AI.' },
            ].map(f => (
              <div key={f.title} className="p-6 md:p-8 rounded-2xl border border-zinc-800 bg-zinc-900/40 hover:border-zinc-700 hover:bg-zinc-900/70 transition-all group">
                <div className="w-10 h-10 md:w-12 md:h-12 rounded-xl bg-blue-600/10 border border-blue-500/20 flex items-center justify-center mb-4 md:mb-6 group-hover:bg-blue-600/20 transition-colors">
                  <f.icon className="w-5 h-5 md:w-6 md:h-6 text-blue-400" />
                </div>
                <h3 className="text-lg md:text-xl font-semibold text-zinc-100 mb-2 md:mb-3">{f.title}</h3>
                <p className="text-sm md:text-base text-zinc-500 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-20 md:py-28 px-4 sm:px-6 border-t border-zinc-800/60 bg-zinc-900/20">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12 md:mb-16">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-zinc-100 mb-4">How ContextGuard works</h2>
            <p className="text-base md:text-lg text-zinc-400">Deployed as a transparent proxy between your AI agents and external services.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8 md:gap-12">
            {[
              { step: '01', title: 'Connect your workspace', desc: 'Just sign in with Google Workspace. No code changes required.' },
              { step: '02', title: 'We watch in the background', desc: 'Our engine checks all app requests quietly and safely.' },
              { step: '03', title: 'Bad apps are blocked', desc: 'Harmful actions are stopped instantly, and you get alerted.' },
            ].map(s => (
              <div key={s.step} className="text-center md:text-left">
                <div className="text-5xl md:text-6xl lg:text-7xl font-bold text-zinc-800 mb-4 md:mb-6 font-mono">{s.step}</div>
                <h3 className="text-xl md:text-2xl font-semibold text-zinc-100 mb-2 md:mb-3">{s.title}</h3>
                <p className="text-sm md:text-base text-zinc-500 leading-relaxed">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 md:py-32 px-4 sm:px-6 text-center">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-zinc-100 mb-4 md:mb-6">Ready to make your team safe?</h2>
          <p className="text-base md:text-lg text-zinc-400 mb-8 md:mb-10">Join other teams who trust ContextGuard to keep their tools safe.</p>
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center">
            <button onClick={goSignup} className="px-6 py-3 sm:px-8 sm:py-4 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium text-base sm:text-lg transition-colors flex items-center justify-center gap-2">
              {user ? 'Open Dashboard' : 'Get started'} <ArrowRight className="w-5 h-5" />
            </button>
            <button onClick={() => navigate('/pricing')} className="px-6 py-3 sm:px-8 sm:py-4 border border-zinc-700 hover:border-zinc-500 text-zinc-200 rounded-lg font-medium text-base sm:text-lg transition-colors">
              View Pricing
            </button>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  )
}

/* ─── NOTIFICATIONS DROPDOWN ─────────────────────────────────── */
// Converts a real DPI event from /api/events into a notification shape
function eventToNotification(event, idx) {
  const sevToType = { CRITICAL: 'critical', HIGH: 'warning', MEDIUM: 'info', LOW: 'info' }
  const ago = (ts) => {
    const diff = Math.floor((Date.now() - new Date(ts).getTime()) / 1000)
    if (diff < 60) return `${diff}s ago`
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
    return `${Math.floor(diff / 86400)}d ago`
  }
  return {
    id: event.id || idx,
    type: sevToType[event.severity] || 'info',
    title: event.policy_triggered || 'DPI Event',
    desc: event.alert_message || 'Threat intercepted by Lobster Trap.',
    time: ago(event.timestamp),
    read: false,
  }
}

function NotificationsDropdown({ onClose }) {
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)
  const unread = notifications.filter(n => !n.read).length

  useEffect(() => {
    const load = async () => {
      try {
        const res = await axios.get(`${API}/api/events?hours=24`)
        const events = (res.data.events || []).slice(0, 8)
        setNotifications(events.map((e, i) => eventToNotification(e, i)))
      } catch {
        setNotifications([])
      }
      setLoading(false)
    }
    load()
  }, [])

  const typeStyles = {
    critical: 'bg-rose-500/10 border-rose-500/20 text-rose-400',
    warning:  'bg-amber-500/10 border-amber-500/20 text-amber-400',
    info:     'bg-blue-500/10 border-blue-500/20 text-blue-400',
  }

  const markAllRead = () => setNotifications(prev => prev.map(n => ({ ...n, read: true })))

  return (
    <div className="absolute right-0 top-full mt-2 w-80 bg-[#0f1117] border border-zinc-800 rounded-xl shadow-2xl shadow-black/40 z-50 overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-zinc-100">Notifications</span>
          {unread > 0 && <span className="px-1.5 py-0.5 text-xs bg-rose-500 text-white rounded-full font-medium">{unread}</span>}
        </div>
        {unread > 0 && <button onClick={markAllRead} className="text-xs text-blue-400 hover:text-blue-300 transition-colors">Mark all read</button>}
      </div>
      <div className="max-h-80 overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="w-4 h-4 border-2 border-zinc-600 border-t-zinc-300 rounded-full animate-spin" />
          </div>
        ) : notifications.length === 0 ? (
          <p className="text-center text-xs text-zinc-600 py-8">No events in the last 24 hours.</p>
        ) : notifications.map(n => (
          <button key={n.id} onClick={() => setNotifications(prev => prev.map(x => x.id === n.id ? { ...x, read: true } : x))}
            className={`w-full text-left px-4 py-3 border-b border-zinc-800/60 hover:bg-zinc-800/30 transition-colors ${!n.read ? 'bg-zinc-800/20' : ''}`}>
            <div className="flex items-start gap-3">
              <div className={`mt-0.5 px-1.5 py-0.5 text-[10px] font-semibold rounded border uppercase tracking-wide flex-shrink-0 ${typeStyles[n.type]}`}>{n.type}</div>
              <div className="flex-1 min-w-0">
                <p className={`text-xs font-medium mb-0.5 truncate ${!n.read ? 'text-zinc-100' : 'text-zinc-300'}`}>{n.title}</p>
                <p className="text-xs text-zinc-500 leading-relaxed line-clamp-2">{n.desc}</p>
                <p className="text-[10px] text-zinc-600 mt-1">{n.time}</p>
              </div>
              {!n.read && <div className="w-2 h-2 rounded-full bg-blue-500 flex-shrink-0 mt-1" />}
            </div>
          </button>
        ))}
      </div>
      <div className="px-4 py-2.5 border-t border-zinc-800 text-center">
        <button onClick={onClose} className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors">View all in Threat Feed</button>
      </div>
    </div>
  )
}

/* ─── PROFILE DROPDOWN ───────────────────────────────────────── */
function ProfileDropdown({ onDisconnect, onSignOut, onClose, wsConnected, systemStatus, user }) {
  const menuItems = [
    { label: 'Dashboard', icon: Shield, action: onClose },
    { label: 'Settings', icon: Lock, action: onClose },
    { label: 'Documentation', icon: ExternalLink, action: onClose },
    { label: 'Support', icon: Users, action: onClose },
  ]
  return (
    <div className="absolute right-0 top-full mt-2 w-60 bg-[#0f1117] border border-zinc-800 rounded-xl shadow-2xl shadow-black/40 z-50 overflow-hidden">
      <div className="px-4 py-3 border-b border-zinc-800">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-blue-600/20 border border-blue-500/30 flex items-center justify-center flex-shrink-0">
            <Users className="w-4 h-4 text-blue-400" />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-zinc-100 truncate">
              {user?.name || (wsConnected ? systemStatus?.workspace?.admin_email?.split('@')[0] : 'User')}
            </p>
            <p className="text-xs text-zinc-500 truncate">
              {user?.email || (wsConnected ? systemStatus?.workspace?.admin_email : 'Not signed in')}
            </p>
          </div>
        </div>
        <div className={`mt-3 flex items-center gap-1.5 text-xs rounded-lg px-2.5 py-1.5 border ${wsConnected ? 'bg-emerald-500/10 border-emerald-900/60 text-emerald-400' : 'bg-zinc-900 border-zinc-800 text-zinc-500'}`}>
          <div className={`w-1.5 h-1.5 rounded-full ${wsConnected ? 'bg-emerald-500' : 'bg-zinc-600'}`} />
          {wsConnected ? 'Workspace connected' : 'Not connected'}
        </div>
      </div>
      <div className="py-1">
        {menuItems.map(item => (
          <button key={item.label} onClick={item.action}
            className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/50 transition-colors">
            <item.icon className="w-4 h-4 flex-shrink-0" />
            {item.label}
          </button>
        ))}
      </div>
      <div className="border-t border-zinc-800 py-1">
        <button onClick={onSignOut}
          className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/50 transition-colors">
          <LogOut className="w-4 h-4 flex-shrink-0" />
          Sign out
        </button>
        <button onClick={onDisconnect}
          className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 transition-colors">
          <LogOut className="w-4 h-4 flex-shrink-0" />
          Disconnect workspace
        </button>
      </div>
    </div>
  )
}

/* ─── DASHBOARD ────────────────────────────────────────────────── */
function Dashboard() {
  const { tab } = useParams()
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const activeTab = tab || 'threats'
  const setActiveTab = (newTab) => navigate(`/dashboard/${newTab}`)
  
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [systemStatus, setSystemStatus] = useState(null)
  const [showNotifications, setShowNotifications] = useState(false)
  const [showProfile, setShowProfile] = useState(false)

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

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handle = (e) => {
      if (!e.target.closest('[data-dropdown]')) {
        setShowNotifications(false)
        setShowProfile(false)
      }
    }
    document.addEventListener('mousedown', handle)
    return () => document.removeEventListener('mousedown', handle)
  }, [])

  const handleSignOut = async () => {
    await logout()
    navigate('/login')
  }

  const handleDisconnect = async () => {
    try {
      await axios.post(`${API}/api/workspace/disconnect`)
      setSystemStatus(prev => ({ ...prev, workspace: { ...prev.workspace, connected: false } }))
    } catch (e) { console.error('Failed to disconnect', e) }
    navigate('/')
  }

  const TABS = [
    { id: 'threats', label: 'Threat Feed', icon: Activity },
    { id: 'apps', label: 'OAuth Apps', icon: AppWindow },
    { id: 'env', label: 'Env Guardian', icon: FileKey },
    { id: 'redteam', label: 'Red Team', icon: Crosshair },
    { id: 'response', label: 'Incidents', icon: ShieldAlert },
  ]

  if (!TABS.find(t => t.id === activeTab)) {
    return <Navigate to="/dashboard/threats" replace />
  }

  const renderContent = () => {

    switch (activeTab) {
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

  if (systemStatus === null) {
    return (
      <div className="flex h-screen bg-[#09090b] items-center justify-center">
        <div className="flex flex-col items-center">
          <div className="w-8 h-8 border-2 border-blue-500/20 border-t-blue-500 rounded-full animate-spin mb-4" />
          <p className="text-zinc-500 text-sm font-medium animate-pulse">Initializing Security Engine...</p>
        </div>
      </div>
    )
  }

  if (!wsConnected) {
    return (
      <div className="h-screen w-screen bg-[#09090b] overflow-hidden relative">
        <OAuthApps />
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-[#09090b] text-zinc-100 font-sans overflow-hidden">
      {/* Sidebar */}
      <aside className={`transition-all duration-300 ease-in-out border-r border-zinc-800/60 bg-[#0f1117] ${sidebarOpen ? 'w-56' : 'w-16'} flex flex-col z-20 flex-shrink-0`}>
        <div className="flex items-center h-14 px-4 border-b border-zinc-800/60">
          <Shield className="w-6 h-6 text-blue-500 flex-shrink-0" />
          {sidebarOpen && <span className="ml-2.5 font-semibold text-zinc-100 text-sm tracking-tight whitespace-nowrap">ContextGuard</span>}
        </div>

        <nav className="flex-1 py-4 px-2 space-y-0.5">
          {TABS.map(tab => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center px-3 py-2.5 rounded-lg transition-all text-sm ${isActive ? 'bg-zinc-800 text-zinc-100' : 'text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800/50'}`}>
                <Icon className={`w-4 h-4 flex-shrink-0 ${!sidebarOpen ? 'mx-auto' : 'mr-2.5'} ${isActive ? 'text-blue-400' : ''}`} />
                {sidebarOpen && <span className="whitespace-nowrap font-medium">{tab.label}</span>}
              </button>
            )
          })}
        </nav>

        {sidebarOpen && systemStatus && (
          <div className="px-3 pb-3 space-y-1.5">
            <p className="text-[10px] font-semibold text-zinc-600 uppercase tracking-widest px-1 mb-2">System</p>
            <div className={`flex items-center gap-2 text-xs rounded-lg px-2.5 py-2 border ${wsConnected ? 'bg-emerald-500/8 border-emerald-900/60 text-emerald-400' : 'bg-zinc-900 border-zinc-800 text-zinc-500'}`}>
              <Database className="w-3 h-3 flex-shrink-0" />
              <span className="truncate">{wsConnected ? systemStatus.workspace.admin_email : 'Not connected'}</span>
            </div>
            <div className={`flex items-center gap-2 text-xs rounded-lg px-2.5 py-2 border ${proxyOnline ? 'bg-emerald-500/8 border-emerald-900/60 text-emerald-400' : 'bg-zinc-900 border-zinc-800 text-zinc-500'}`}>
              {proxyOnline ? <Wifi className="w-3 h-3 flex-shrink-0" /> : <WifiOff className="w-3 h-3 flex-shrink-0" />}
              <span>{proxyOnline ? 'Proxy online' : 'Proxy offline'}</span>
            </div>
          </div>
        )}

        <div className="p-2 border-t border-zinc-800/60">
          <button onClick={handleDisconnect}
            className="w-full flex items-center px-3 py-2.5 text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800/50 rounded-lg transition-colors text-sm">
            <LogOut className={`w-4 h-4 flex-shrink-0 ${sidebarOpen ? 'mr-2.5' : 'mx-auto'}`} />
            {sidebarOpen && <span>Disconnect</span>}
          </button>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-14 flex items-center justify-between px-5 border-b border-zinc-800/60 bg-[#0f1117]/80 backdrop-blur-md z-10 flex-shrink-0">
          <div className="flex items-center gap-3">
            <button onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800/60 rounded-md transition-colors">
              <Menu className="w-4 h-4" />
            </button>
            <h2 className="text-sm font-semibold text-zinc-200">{TABS.find(t => t.id === activeTab)?.label}</h2>
          </div>
          <div className="flex items-center gap-2.5">
            {systemStatus ? (
              <div className={`flex items-center gap-1.5 rounded-full px-3 py-1 border text-xs font-medium ${wsConnected ? 'bg-emerald-500/10 border-emerald-900/60 text-emerald-400' : 'bg-zinc-900 border-zinc-800 text-zinc-500'}`}>
                <div className={`w-1.5 h-1.5 rounded-full ${wsConnected ? 'bg-emerald-500' : 'bg-zinc-600'}`} />
                {wsConnected ? `${systemStatus.workspace.apps_in_db} apps` : 'Not connected'}
              </div>
            ) : (
              <div className="flex items-center gap-1.5 bg-zinc-900 border border-zinc-800 rounded-full px-3 py-1">
                <div className="w-1.5 h-1.5 rounded-full bg-zinc-600 animate-pulse" />
                <span className="text-xs text-zinc-500">Connecting</span>
              </div>
            )}
            <div className="relative" data-dropdown>
              <button
                onClick={() => { setShowNotifications(p => !p); setShowProfile(false) }}
                className="relative p-2 text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800/60 rounded-md transition-colors">
                <Bell className="w-4 h-4" />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-rose-500 rounded-full" />
              </button>
              {showNotifications && (
                <NotificationsDropdown onClose={() => setShowNotifications(false)} />
              )}
            </div>
            <div className="relative" data-dropdown>
              <button
                onClick={() => { setShowProfile(p => !p); setShowNotifications(false) }}
                className="w-8 h-8 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center cursor-pointer hover:border-zinc-500 transition-colors">
                <Users className="w-4 h-4 text-zinc-400" />
              </button>
              {showProfile && (
                <ProfileDropdown
                  onDisconnect={handleDisconnect}
                  onSignOut={handleSignOut}
                  onClose={() => setShowProfile(false)}
                  wsConnected={wsConnected}
                  systemStatus={systemStatus}
                  user={user}
                />
              )}
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto bg-[#09090b]">
          <div className="max-w-[1600px] 2xl:max-w-none mx-auto p-4 sm:p-6 lg:p-8">
            {renderContent()}
          </div>
        </main>
      </div>
    </div>
  )
}

/* ─── MAIN APP ROUTES ────────────────────────────────────────── */
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/about" element={<AboutPage />} />
      <Route path="/pricing" element={<PricingPage />} />
      <Route path="/login" element={<GuestRoute><LoginPage /></GuestRoute>} />
      <Route path="/signup" element={<GuestRoute><SignupPage /></GuestRoute>} />
      <Route path="/dashboard" element={<ProtectedRoute><Navigate to="/dashboard/threats" replace /></ProtectedRoute>} />
      <Route path="/dashboard/:tab" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
