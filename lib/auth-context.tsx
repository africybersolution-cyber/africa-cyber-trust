'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

interface Company {
  id: string;
  name: string;
  country: string;
  plan: string;
  industry?: string;
}

interface AuthContextType {
  user: User | null;
  company: Company | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name: string, account_type?: string) => Promise<void>;
  registerBusiness: (data: BusinessRegistrationData) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  loading: boolean;
}

interface BusinessRegistrationData {
  company_name: string;
  email: string;
  password: string;
  name: string;
  country: string;
  domain?: string;
  phone?: string;
  size?: string;
  industry?: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [company, setCompany] = useState<Company | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Load auth state from localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token');
    const storedUser = localStorage.getItem('auth_user');
    const storedCompany = localStorage.getItem('auth_company');

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
      if (storedCompany) {
        setCompany(JSON.parse(storedCompany));
      }
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    console.log('🔐 Attempting login to:', `${API_URL}/api/auth/login`);

    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });

    console.log('📡 Response status:', response.status);

    if (!response.ok) {
      const error = await response.json();
      console.error('❌ Login error:', error);
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    console.log('✅ Login successful!', { hasToken: !!data.access_token, hasUser: !!data.user });

    setToken(data.access_token);
    setUser(data.user);

    // Set company if it exists (for business accounts)
    if (data.company) {
      setCompany(data.company);
      localStorage.setItem('auth_company', JSON.stringify(data.company));
    }

    localStorage.setItem('auth_token', data.access_token);
    localStorage.setItem('auth_user', JSON.stringify(data.user));

    console.log('💾 Saved to localStorage');
  };

  const signup = async (email: string, password: string, name: string, account_type: string = 'personal') => {
    const response = await fetch(`${API_URL}/api/auth/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password, name, account_type }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Signup failed');
    }

    const data = await response.json();
    setToken(data.access_token);
    setUser(data.user);

    localStorage.setItem('auth_token', data.access_token);
    localStorage.setItem('auth_user', JSON.stringify(data.user));
  };

  const registerBusiness = async (data: BusinessRegistrationData) => {
    const response = await fetch(`${API_URL}/api/auth/register-business`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Business registration failed');
    }

    const result = await response.json();
    setToken(result.access_token);
    setUser(result.user);
    setCompany(result.company);

    localStorage.setItem('auth_token', result.access_token);
    localStorage.setItem('auth_user', JSON.stringify(result.user));
    localStorage.setItem('auth_company', JSON.stringify(result.company));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    setCompany(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
    localStorage.removeItem('auth_company');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        company,
        token,
        login,
        signup,
        registerBusiness,
        logout,
        isAuthenticated: !!token,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
