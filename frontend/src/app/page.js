'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import LoginForm from '../components/LoginForm';
import RegisterForm from '../components/RegisterForm';
import { useAuth } from '../contexts/AuthContext';

export default function HomePage() {
  const [activeTab, setActiveTab] = useState('login');
  const { user, token, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Check if user is already authenticated
    if (token && !loading) {
      if (user?.role === 'admin') {
        router.push('/admin');
      } else {
        router.push('/dashboard');
      }
    }
  }, [token, user, loading, router]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white mb-4"></div>
          <p className="text-white text-xl">Loading SecureVault 🔐</p>
        </div>
      </div>
    );
  }

  // If user is authenticated, redirect happens via useEffect above
  if (token) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-center">
          <p className="text-white text-xl">Redirecting to dashboard... 🚀</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-4xl font-extrabold gradient-text">
          SecureVault 🔐
        </h2>
        <p className="mt-2 text-center text-lg text-white/80">
          A secure file encryption and decryption system
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-card py-8 px-4 shadow-xl sm:rounded-2xl sm:px-10 border border-white/30">
          {/* Tab Navigation */}
          <div className="flex justify-between mb-6">
            <button
              onClick={() => setActiveTab('login')}
              className={`flex-1 py-3 px-4 rounded-t-xl font-bold ${
                activeTab === 'login'
                  ? 'bg-gradient-to-r from-[#ff6b81] to-[#6b5bff] text-white shadow-lg'
                  : 'bg-white/10 text-white/80 hover:bg-white/20'
              } transition-all duration-300`}
            >
              Login 🔑
            </button>
            <button
              onClick={() => setActiveTab('register')}
              className={`flex-1 py-3 px-4 rounded-t-xl font-bold ${
                activeTab === 'register'
                  ? 'bg-gradient-to-r from-[#ff6b81] to-[#6b5bff] text-white shadow-lg'
                  : 'bg-white/10 text-white/80 hover:bg-white/20'
              } transition-all duration-300`}
            >
              Register 📝
            </button>
          </div>

          {/* Tab Content */}
          <div className="mt-4">
            {activeTab === 'login' && <LoginForm />}
            {activeTab === 'register' && <RegisterForm />}
          </div>
        </div>
      </div>
    </div>
  );
}