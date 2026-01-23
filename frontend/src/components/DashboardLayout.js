'use client';

import { useAuth } from '../contexts/AuthContext';
import { useRouter, usePathname } from 'next/navigation';
import { useEffect } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

export default function DashboardLayout({ children }) {
  const { token, user } = useAuth();
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
        <p>Redirecting...</p>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-[#1E1E2F]">
      <Sidebar />
      <div className="flex flex-col flex-1 ml-64">
        <Header />
        <main className="flex-1 p-6 bg-[#1E1E2F] overflow-y-auto">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}