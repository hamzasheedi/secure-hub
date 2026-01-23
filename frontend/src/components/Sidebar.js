'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '../contexts/AuthContext';

export default function Sidebar({ sidebarOpen, setSidebarOpen }) {
  const pathname = usePathname();
  const { user } = useAuth();

  const navItems = [
    { name: 'Vault', href: '/dashboard', icon: '📁' },
    { name: 'Upload & Encrypt', href: '/dashboard/upload', icon: '⬆️' },
    { name: 'Decrypt Local File', href: '/dashboard/local-decrypt', icon: '🔓' },
  ];

  // Add admin panel if user is admin
  if (user?.role === 'admin') {
    navItems.push({ name: 'Admin Panel', href: '/admin', icon: '⚙️' });
  }

  // Close sidebar when route changes
  useEffect(() => {
    setSidebarOpen(false);
  }, [pathname, setSidebarOpen]);

  return (
    <>
      {/* Mobile menu overlay */}
      {sidebarOpen && (
        <div
          className="md:hidden fixed inset-0 z-40 bg-black/50 backdrop-blur-sm transition-opacity duration-300"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}

      {/* Sidebar - desktop and mobile */}
      <div className={`fixed inset-y-0 z-50 w-64 bg-[#1a0f3d]/50 backdrop-blur-lg border-r border-white/30 transform transition-transform duration-300 ease-in-out ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      } md:translate-x-0 md:inset-y-0 md:flex md:flex-col`}>
        <div className="flex items-center justify-between h-16 border-b border-white/30 px-4">
          <h1 className="text-xl sm:text-2xl font-bold text-white">SecureVault 🔐</h1>
          <button
            className="md:hidden text-white"
            onClick={() => setSidebarOpen(false)}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <nav className="flex-1 px-2 py-4 overflow-y-auto">
          <div className="space-y-1">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`${
                  pathname === item.href
                    ? 'bg-gradient-to-r from-[#ff6b81] to-[#6b5bff] text-white shadow-lg'
                    : 'text-white/90 hover:bg-white/20 hover:text-white'
                } group flex items-center px-4 py-3 text-sm sm:text-base font-bold rounded-xl transition-all duration-300 hover-lift`}
                onClick={() => setSidebarOpen(false)} // Close mobile menu when clicking a link
              >
                <span className="mr-3 text-lg">{item.icon}</span>
                <span>{item.name}</span>
              </Link>
            ))}
          </div>
        </nav>
      </div>
    </>
  );
}