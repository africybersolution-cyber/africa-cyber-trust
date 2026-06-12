'use client';

import { useAuth } from '@/lib/auth-context';
import { useRouter, usePathname } from 'next/navigation';
import { ReactNode } from 'react';

const BLUE = '#0047AB';
const GOLD = '#DAA520';

const NAV = [
  { label: 'Overview', href: '/dashboard', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { label: 'Assets', href: '/dashboard/assets', icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10' },
  { label: 'Scans & Findings', href: '/scans', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
  { label: 'Reports', href: '/dashboard/reports', icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
  { label: 'Alerts', href: '/dashboard/alerts', icon: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9' },
  { label: 'Team', href: '/dashboard/team', icon: 'M17 20h5v-2a4 4 0 00-3-3.87M9 20H4v-2a4 4 0 013-3.87m6-9a4 4 0 11-8 0 4 4 0 018 0zm6 3a3 3 0 11-6 0 3 3 0 016 0z' },
  { label: 'Billing', href: '/dashboard/billing', icon: 'M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z' },
];

interface DashboardLayoutProps {
  children: ReactNode;
  title: string;
  subtitle?: string;
}

export default function DashboardLayout({ children, title, subtitle }: DashboardLayoutProps) {
  const { user, company, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  // Determine which nav item is active
  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return pathname === '/dashboard';
    }
    return pathname?.startsWith(href);
  };

  return (
    <main className="min-h-screen cyber-bg">
      {/* Top Navigation */}
      <nav className="border-b border-cyber bg-[#050B1A]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <a href="/dashboard" className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${BLUE} 0%, ${GOLD} 100%)` }}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <div className="font-bold text-sm text-white">{company ? company.name : user?.name}</div>
                <div className="text-xs text-cyber-muted capitalize">{company ? `${company.plan} Plan` : user?.role}</div>
              </div>
            </a>

            <div className="flex items-center gap-4">
              <button onClick={handleLogout} className="px-4 py-2 text-sm font-semibold text-cyber-muted hover:text-red-400 transition-colors">
                Logout
              </button>
              <div className="w-10 h-10 rounded-full flex items-center justify-center text-white" style={{ background: BLUE }}>
                <span className="text-sm font-bold">{user?.name?.charAt(0).toUpperCase()}</span>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-[230px_1fr] gap-8">
          {/* Sidebar Nav */}
          <aside className="hidden lg:block">
            <div className="cyber-card p-3 sticky top-24">
              <nav className="space-y-1">
                {NAV.map((item) => (
                  <a
                    key={item.label}
                    href={item.href}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                      isActive(item.href) ? 'text-white bg-white/5' : 'text-cyber-muted hover:text-white hover:bg-white/5'
                    }`}
                    style={isActive(item.href) ? { borderLeft: `3px solid ${GOLD}` } : { borderLeft: '3px solid transparent' }}
                  >
                    <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
                    </svg>
                    {item.label}
                  </a>
                ))}
              </nav>
            </div>
          </aside>

          {/* Main Content */}
          <div>
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-white mb-1">{title}</h1>
              {subtitle && <p className="text-cyber-muted">{subtitle}</p>}
            </div>

            {children}
          </div>
        </div>
      </div>
    </main>
  );
}
