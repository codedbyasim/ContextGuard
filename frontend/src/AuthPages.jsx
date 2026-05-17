import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { Shield, Mail, Lock, User, ArrowRight, Eye, EyeOff, AlertCircle } from 'lucide-react'
import { useAuth } from './auth'

function AuthShell({ title, subtitle, children, footer }) {
  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-100 font-sans flex">
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden border-r border-zinc-800/60">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/10 via-[#09090b] to-[#09090b]" />
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[420px] h-[420px] bg-blue-600/10 blur-[120px] rounded-full" />
        <div className="relative z-10 flex flex-col justify-between p-12 xl:p-16 w-full">
          <Link to="/" className="flex items-center gap-2.5 w-fit">
            <Shield className="w-7 h-7 text-blue-500" />
            <span className="font-semibold text-lg tracking-tight">ContextGuard</span>
          </Link>
          <div>
            <p className="text-sm font-medium text-blue-400 mb-4">Enterprise AI security</p>
            <h1 className="text-3xl xl:text-4xl font-bold leading-tight text-zinc-100 mb-4">
              Secure access to your security command center
            </h1>
            <p className="text-zinc-400 leading-relaxed max-w-md">
              Monitor OAuth apps, inspect AI traffic, and respond to threats — only for registered team members.
            </p>
          </div>
          <p className="text-xs text-zinc-600">© 2025 ContextGuard. All rights reserved.</p>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-6 sm:p-10">
        <div className="w-full max-w-md">
          <div className="lg:hidden flex items-center gap-2.5 mb-8">
            <Shield className="w-6 h-6 text-blue-500" />
            <span className="font-semibold tracking-tight">ContextGuard</span>
          </div>
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-zinc-100 mb-2">{title}</h2>
            <p className="text-sm text-zinc-500">{subtitle}</p>
          </div>
          {children}
          {footer}
        </div>
      </div>
    </div>
  )
}

function Field({ label, icon: Icon, type, value, onChange, placeholder, autoComplete }) {
  return (
    <div>
      <label className="block text-xs font-medium text-zinc-400 mb-1.5">{label}</label>
      <div className="relative">
        <Icon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
        <input
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          autoComplete={autoComplete}
          required
          className="w-full pl-10 pr-4 py-2.5 bg-zinc-900/80 border border-zinc-800 rounded-lg text-sm text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/30 transition-colors"
        />
      </div>
    </div>
  )
}

function PasswordField({ label, value, onChange, autoComplete }) {
  const [visible, setVisible] = useState(false)
  return (
    <div>
      <label className="block text-xs font-medium text-zinc-400 mb-1.5">{label}</label>
      <div className="relative">
        <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
        <input
          type={visible ? 'text' : 'password'}
          value={value}
          onChange={onChange}
          placeholder="••••••••"
          autoComplete={autoComplete}
          required
          minLength={8}
          className="w-full pl-10 pr-11 py-2.5 bg-zinc-900/80 border border-zinc-800 rounded-lg text-sm text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/30 transition-colors"
        />
        <button
          type="button"
          onClick={() => setVisible((v) => !v)}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-zinc-300 transition-colors"
          aria-label={visible ? 'Hide password' : 'Show password'}
        >
          {visible ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
        </button>
      </div>
    </div>
  )
}

function ErrorBanner({ message }) {
  if (!message) return null
  return (
    <div className="flex items-start gap-2.5 p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm mb-5">
      <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
      <span>{message}</span>
    </div>
  )
}

function parseAuthError(err) {
  const detail = err.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return 'Something went wrong. Please try again.'
}

export function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const from = location.state?.from?.pathname || '/dashboard/threats'

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await login(email.trim(), password)
      navigate(from, { replace: true })
    } catch (err) {
      setError(parseAuthError(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AuthShell
      title="Welcome back"
      subtitle="Sign in to access your ContextGuard dashboard."
      footer={
        <p className="mt-8 text-center text-sm text-zinc-500">
          Don&apos;t have an account?{' '}
          <Link to="/signup" className="text-blue-400 hover:text-blue-300 font-medium transition-colors">
            Create one
          </Link>
        </p>
      }
    >
      <ErrorBanner message={error} />
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Email" icon={Mail} type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@company.com" autoComplete="email" />
        <PasswordField label="Password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" />
        <button
          type="submit"
          disabled={submitting}
          className="w-full mt-2 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-60 disabled:cursor-not-allowed text-white rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
        >
          {submitting ? 'Signing in…' : <>Sign in <ArrowRight className="w-4 h-4" /></>}
        </button>
      </form>
      <p className="mt-6 text-center">
        <Link to="/" className="text-xs text-zinc-600 hover:text-zinc-400 transition-colors">← Back to home</Link>
      </p>
    </AuthShell>
  )
}

export function SignupPage() {
  const navigate = useNavigate()
  const { register } = useAuth()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (password !== confirm) {
      setError('Passwords do not match.')
      return
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters.')
      return
    }
    setSubmitting(true)
    try {
      await register(name.trim(), email.trim(), password)
      navigate('/dashboard/threats', { replace: true })
    } catch (err) {
      setError(parseAuthError(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AuthShell
      title="Create your account"
      subtitle="Register to get secure access to the ContextGuard dashboard."
      footer={
        <p className="mt-8 text-center text-sm text-zinc-500">
          Already have an account?{' '}
          <Link to="/login" className="text-blue-400 hover:text-blue-300 font-medium transition-colors">
            Sign in
          </Link>
        </p>
      }
    >
      <ErrorBanner message={error} />
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Full name" icon={User} type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Jane Smith" autoComplete="name" />
        <Field label="Work email" icon={Mail} type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@company.com" autoComplete="email" />
        <PasswordField label="Password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="new-password" />
        <PasswordField label="Confirm password" value={confirm} onChange={(e) => setConfirm(e.target.value)} autoComplete="new-password" />
        <button
          type="submit"
          disabled={submitting}
          className="w-full mt-2 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-60 disabled:cursor-not-allowed text-white rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
        >
          {submitting ? 'Creating account…' : <>Create account <ArrowRight className="w-4 h-4" /></>}
        </button>
      </form>
      <p className="mt-4 text-xs text-zinc-600 text-center leading-relaxed">
        By registering, you confirm this account is for authorized ContextGuard users only.
      </p>
      <p className="mt-4 text-center">
        <Link to="/" className="text-xs text-zinc-600 hover:text-zinc-400 transition-colors">← Back to home</Link>
      </p>
    </AuthShell>
  )
}
