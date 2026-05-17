import React, { createContext, useContext, useState, useEffect } from 'react';
import { supabase } from './supabaseClient';
import axios from 'axios';

export const API = import.meta.env.DEV ? 'http://localhost:3000' : '';

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
    if (data.session?.access_token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${data.session.access_token}`;
    }
    return data;
  };

  const register = async (name, email, password) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: { data: { name: name } }
    });
    if (error) throw error;
    if (data.session?.access_token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${data.session.access_token}`;
    }
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
