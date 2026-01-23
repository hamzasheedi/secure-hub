'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '../contexts/AuthContext';

export default function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuth();

  const navItems = [
    { name: 'Vault', href: '/dashboard', icon: '📁' },
    { name: 'Upload', href: '/dashboard/upload', icon: '⬆️' },
  ];

  // Add admin panel if user is admin
  if (user?.role === 'admin') {
    navItems.push({ name: 'Admin Panel', href: '/admin', icon: '⚙️' });
  }

  return (
    <div className="fixed inset-y-0 z-50 w-64 bg-[#2C2C3E] border-r border-gray-700">
      <div className="flex items-center justify-center h-16 border-b border-gray-700">
        <h1 className="text-xl font-bold text-white">SecureVault</h1>
      </div>
      <nav className="mt-5 px-2">
        <div className="space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`${
                pathname === item.href
                  ? 'bg-gray-800 text-white'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              } group flex items-center px-4 py-3 text-base font-medium rounded-md transition-colors duration-200`}
            >
              <span className="mr-3">{item.icon}</span>
              {item.name}
            </Link>
          ))}
        </div>
      </nav>
    </div>
  );
}