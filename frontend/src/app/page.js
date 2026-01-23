'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import LoginForm from '../components/LoginForm';
import RegisterForm from '../components/RegisterForm';
import { useAuth } from '../contexts/AuthContext';

export default function HomePage() {
  const [activeTab, setActiveTab] = useState('login');
  const [isLoading, setIsLoading] = useState(true);
  const { user, token } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Check if user is already authenticated
    if (token) {
      if (user?.role === 'admin') {
        router.push('/admin');
      } else {
        router.push('/dashboard');
      }
    } else {
      setIsLoading(false);
    }
  }, [token, user, router]);

  if (isLoading) {
    return <div className="flex justify-center items-center h-screen bg-[#1E1E2F]">Loading...</div>;
  }

  // If user is authenticated, redirect happens via useEffect above
  if (token) {
    return <div className="flex justify-center items-center h-screen bg-[#1E1E2F]">Redirecting...</div>;
  }

  return (
    <div className="min-h-screen bg-[#1E1E2F] flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-white">
          SecureVault
        </h2>
        <p className="mt-2 text-center text-sm text-gray-400">
          A secure file encryption and decryption system
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-card py-8 px-4 shadow sm:rounded-lg sm:px-10 border border-gray-700">
          {/* Tab Navigation */}
          <div className="flex justify-between mb-6">
            <button
              onClick={() => setActiveTab('login')}
              className={`flex-1 py-2 px-4 rounded-t-md ${
                activeTab === 'login'
                  ? 'bg-gradient-to-r from-[#6C63FF] to-[#9B5DE5] text-white'
                  : 'bg-[#252536] text-gray-300 hover:bg-[#2a2a3a]'
              }`}
            >
              Login
            </button>
            <button
              onClick={() => setActiveTab('register')}
              className={`flex-1 py-2 px-4 rounded-t-md ${
                activeTab === 'register'
                  ? 'bg-gradient-to-r from-[#6C63FF] to-[#9B5DE5] text-white'
                  : 'bg-[#252536] text-gray-300 hover:bg-[#2a2a3a]'
              }`}
            >
              Register
            </button>
          </div>

          {/* Tab Content */}
          {activeTab === 'login' && <LoginForm />}
          {activeTab === 'register' && <RegisterForm />}
        </div>
      </div>
    </div>
  );
}