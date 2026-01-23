'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '../contexts/AuthContext';

export default function Sidebar() {
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

  return (
    <div className="fixed inset-y-0 z-50 w-64 bg-[#1a0f3d]/50 backdrop-blur-lg border-r border-white/30">
      <div className="flex items-center justify-center h-16 border-b border-white/30">
        <h1 className="text-xl sm:text-2xl font-bold text-white">SecureVault 🔐</h1>
      </div>
      <nav className="mt-5 px-2">
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
            >
              <span className="mr-3 text-lg">{item.icon}</span>
              <span>{item.name}</span>
            </Link>
          ))}
        </div>
      </nav>
    </div>
  );
}