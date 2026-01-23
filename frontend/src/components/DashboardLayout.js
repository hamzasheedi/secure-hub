'use client';

import { useAuth } from '../contexts/AuthContext';
import { useRouter, usePathname } from 'next/navigation';
import { useEffect } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

export default function DashboardLayout({ children }) {
  const { token, user, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!token) {
      router.push('/');
    } else if (user?.role === 'admin' && !pathname.startsWith('/admin')) {
      router.push('/admin');
    } else if (user?.role !== 'admin' && pathname.startsWith('/admin')) {
      router.push('/dashboard');
    }
  }, [token, user, pathname, router]);

  if (!token) {
    return (
      <div className="flex justify-center items-center h-screen">
        <p className="text-xl text-white">Redirecting...</p>
      </div>
    );
  }

  // Add loading state check
  if (loading || !user) {
    return (
      <div className="flex justify-center items-center h-screen">
        <p className="text-xl text-white">Loading user data...</p>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#2c184a] to-[#1a0f3d]">
      <div className="fixed inset-y-0 z-40 w-64 bg-[#1a0f3d]/50 backdrop-blur-lg border-r border-white/30">
        <Sidebar />
      </div>
      <div className="flex flex-col flex-1 ml-64">
        <Header />
        <main className="flex-1 p-4 sm:p-6 overflow-y-auto">
          <div className="max-w-7xl mx-auto w-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}