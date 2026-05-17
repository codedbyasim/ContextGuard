with open('frontend/src/auth.jsx', 'w', encoding='utf-8') as f:
    f.write("""import React, { createContext, useContext, useState, useEffect } from 'react';
import { supabase } from './supabaseClient';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
      if (session?.access_token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${session.access_token}`;
      }
      setLoading(false);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
      if (session?.access_token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${session.access_token}`;
      } else {
        delete axios.defaults.headers.common['Authorization'];
      }
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const login = async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw error;
    return data;
  };

  const register = async (name, email, password) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: { data: { name: name } }
    });
    if (error) throw error;
    return data;
  };

  const logout = async () => {
    try {
      await axios.post('/api/auth/logout');
    } catch(e) {}
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
  };

  const value = { user, loading, login, register, logout };

  return <AuthContext.Provider value={value}>{!loading && children}</AuthContext.Provider>;
};
""")

with open('frontend/src/AuthPages.jsx', 'w', encoding='utf-8') as f:
    f.write("""import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from './auth';

const AuthShell = ({ title, subtitle, children }) => (
  <div className="flex min-h-screen bg-neutral-900 border-t border-indigo-500/20">
    <div className="hidden lg:flex w-1/2 bg-neutral-950 flex-col items-center justify-center p-12 relative overflow-hidden bg-gradient-to-b from-neutral-900 to-neutral-950">
      <div className="absolute top-0 left-0 w-full h-[600px] bg-indigo-500/10 rounded-full blur-[120px] -translate-y-1/2"></div>
      <div className="z-10 text-center max-w-lg">
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-white mb-6">
          <span className="text-indigo-400">Context</span>Guard
        </h1>
        <p className="text-lg text-neutral-400">
          The next-generation framework and runtime layer for LLM application security.
        </p>
      </div>
    </div>
    <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
      <div className="w-full max-w-md bg-neutral-950/80 backdrop-blur-2xl border border-white/5 rounded-2xl p-8 sm:p-10 shadow-2xl relative">
        <div className="mb-10">
          <h2 className="text-3xl font-bold text-white mb-3">{title}</h2>
          <p className="text-neutral-400 font-medium">{subtitle}</p>
        </div>
        {children}
      </div>
    </div>
  </div>
);

export const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) return setError('Email and password are required.');
    
    setLoading(true);
    setError(null);
    try {
      await login(email, password);
      navigate('/dashboard/threats', { replace: true });
    } catch (err) {
      setError(err.message || 'Failed to login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthShell title="Welcome back" subtitle="Log in to access your security dashboard.">
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="p-4 bg-rose-500/10 border border-rose-500/50 rounded-lg text-rose-400 text-sm font-medium">
            {error}
          </div>
        )}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-neutral-300 mb-2">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="w-full px-4 py-3 bg-neutral-900 border border-neutral-800 rounded-xl focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 text-white transition-colors"
              placeholder="admin@company.com"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-300 mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="w-full px-4 py-3 bg-neutral-900 border border-neutral-800 rounded-xl focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 text-white transition-colors"
              placeholder="••••••••"
              required
            />
          </div>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full py-3.5 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white font-semibold rounded-xl transition-all disabled:opacity-50"
        >
          {loading ? 'Logging in...' : 'Log In'}
        </button>
        <p className="text-center text-sm text-neutral-500 mt-6">
          Don't have an account?{' '}
          <Link to="/signup" className="text-indigo-400 hover:text-indigo-300 font-semibold transition-colors">
            Sign up
          </Link>
        </p>
      </form>
    </AuthShell>
  );
};

export const SignupPage = () => {
  const [formData, setFormData] = useState({ name: '', email: '', password: '', confirm: '' });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirm) {
      return setError('Passwords do not match');
    }
    if (formData.password.length < 8) {
      return setError('Password must be at least 8 characters');
    }
    
    setLoading(true);
    setError(null);
    try {
      await register(formData.name, formData.email, formData.password);
      // Supabase may require email confirmation, but assuming it logs in or redirects
      navigate('/dashboard/threats', { replace: true });
    } catch (err) {
      setError(err.message || 'Failed to create account');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthShell title="Create an account" subtitle="Join ContextGuard to secure your AI apps.">
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
            <div className="p-4 bg-rose-500/10 border border-rose-500/50 rounded-lg text-rose-400 text-sm font-medium">
              {error}
            </div>
        )}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-neutral-300 mb-2">Full Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={e => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-3 bg-neutral-900 border border-neutral-800 rounded-xl focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 text-white transition-colors"
              placeholder="Jane Doe"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-300 mb-2">Email Address</label>
            <input
              type="email"
              value={formData.email}
              onChange={e => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-4 py-3 bg-neutral-900 border border-neutral-800 rounded-xl focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 text-white transition-colors"
              placeholder="jane@company.com"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-300 mb-2">Password</label>
            <input
              type="password"
              value={formData.password}
              onChange={e => setFormData({ ...formData, password: e.target.value })}
              className="w-full px-4 py-3 bg-neutral-900 border border-neutral-800 rounded-xl focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 text-white transition-colors"
              placeholder="••••••••"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-300 mb-2">Confirm Password</label>
            <input
              type="password"
              value={formData.confirm}
              onChange={e => setFormData({ ...formData, confirm: e.target.value })}
              className="w-full px-4 py-3 bg-neutral-900 border border-neutral-800 rounded-xl focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 text-white transition-colors"
              placeholder="••••••••"
              required
            />
          </div>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full py-3.5 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white font-semibold rounded-xl transition-all disabled:opacity-50"
        >
          {loading ? 'Creating account...' : 'Create Account'}
        </button>
        <p className="text-center text-sm text-neutral-500 mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-indigo-400 hover:text-indigo-300 font-semibold transition-colors">
            Log in
          </Link>
        </p>
      </form>
    </AuthShell>
  );
};
""")
