'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../contexts/AuthContext';

export default function LoginForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(username, password);

    if (result.success) {
      router.push('/dashboard');
    } else {
      setError(result.message);
    }

    setLoading(false);
  };

  return (
    <form className="space-y-6" onSubmit={handleSubmit}>
      {error && (
        <div className="p-3 bg-red-500/20 border border-red-400 rounded-xl text-red-200 flex items-center">
          <span className="mr-2">❌</span> {error}
        </div>
      )}

      <div>
        <label htmlFor="username" className="block text-sm font-bold text-white/95 mb-2 drop-shadow-sm">
          Username 🧑‍💼
        </label>
        <div className="mt-1">
          <input
            id="username"
            name="username"
            type="text"
            autoComplete="username"
            required
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-4 py-3 bg-white/20 border border-white/40 rounded-xl text-white placeholder-white/80 focus:outline-none focus:ring-2 focus:ring-[#ff6b81] focus:border-transparent transition-all duration-300 backdrop-blur-sm"
            placeholder="Enter your username..."
          />
        </div>
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-bold text-white/95 mb-2 drop-shadow-sm">
          Password 🔐
        </label>
        <div className="mt-1">
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-3 bg-white/20 border border-white/40 rounded-xl text-white placeholder-white/80 focus:outline-none focus:ring-2 focus:ring-[#ff6b81] focus:border-transparent transition-all duration-300 backdrop-blur-sm"
            placeholder="Enter your password..."
          />
        </div>
      </div>

      <div className="pt-2">
        <button
          type="submit"
          disabled={loading}
          className="w-full btn-primary py-3.5 text-base font-bold hover-lift"
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Signing in...
            </span>
          ) : (
            'Sign in 🔐'
          )}
        </button>
      </div>
    </form>
  );
}