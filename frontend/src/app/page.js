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
    <div className="min-h-screen bg-gradient-to-br from-[#2c184a] to-[#1a0f3d] flex flex-col justify-center py-6 px-4">
      <div className="w-full max-w-md mx-auto">
        <h2 className="mt-6 text-center text-3xl sm:text-4xl font-extrabold text-white">
          SecureVault 🔐
        </h2>
        <p className="mt-2 text-center text-base sm:text-lg text-white/95">
          A secure file encryption and decryption system
        </p>
      </div>

      <div className="mt-6 w-full max-w-md mx-auto">
        <div className="bg-[#1a0f3d]/30 backdrop-blur-lg py-6 px-4 sm:px-6 shadow-xl rounded-2xl border border-white/20">
          {/* Tab Navigation */}
          <div className="flex flex-col sm:flex-row justify-between mb-4 sm:mb-6 gap-2">
            <button
              onClick={() => setActiveTab('login')}
              className={`flex-1 py-3 px-3 rounded-t-xl sm:rounded-t-xl font-bold text-sm sm:text-base ${
                activeTab === 'login'
                  ? 'bg-gradient-to-r from-[#ff6b81] to-[#6b5bff] text-white shadow-lg'
                  : 'bg-white/10 text-white/80 hover:bg-white/20'
              } transition-all duration-300`}
            >
              Login 🔑
            </button>
            <button
              onClick={() => setActiveTab('register')}
              className={`flex-1 py-3 px-3 rounded-b-xl sm:rounded-t-xl font-bold text-sm sm:text-base ${
                activeTab === 'register'
                  ? 'bg-gradient-to-r from-[#ff6b81] to-[#6b5bff] text-white shadow-lg'
                  : 'bg-white/10 text-white/80 hover:bg-white/20'
              } transition-all duration-300`}
            >
              Register 📝
            </button>
          </div>

          {/* Tab Content */}
          <div className="mt-2 sm:mt-4">
            {activeTab === 'login' && <LoginForm />}
            {activeTab === 'register' && <RegisterForm />}
          </div>
        </div>
      </div>
    </div>
  );
}