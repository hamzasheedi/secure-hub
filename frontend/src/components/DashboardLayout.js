'use client';

import { useAuth } from '../contexts/AuthContext';
import { useRouter, usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

export default function DashboardLayout({ children }) {
  const { token, user, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!token) {
      router.push('/');
    } else if (user?.role === 'admin' && !pathname.startsWith('/admin')) {
      router.push('/admin');
    } else if (user?.role !== 'admin' && pathname.startsWith('/admin')) {
      router.push('/dashboard');
    }
  }, [token, user, pathname, router]);

  // Listen for toggle sidebar event
  useEffect(() => {
    const handleToggleSidebar = () => {
      setSidebarOpen(prev => !prev);
    };

    window.addEventListener('toggleSidebar', handleToggleSidebar);

    return () => {
      window.removeEventListener('toggleSidebar', handleToggleSidebar);
    };
  }, []);

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
      <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
      <div className="flex flex-col flex-1 sidebar-spacer">
        <Header />
        <main className="flex-1 p-4 sm:p-6 overflow-y-auto bg-[#1a0f3d]/20 md:bg-[#1a0f3d]/10 rounded-tl-xl">
          <div className="max-w-7xl mx-auto w-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}