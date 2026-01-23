'use client';

import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function RegisterForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    // Basic validation
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      setLoading(false);
      return;
    }

    const result = await register(username, password);

    if (result.success) {
      setSuccess(result.message || 'Registration successful! Please log in.');
      setUsername('');
      setPassword('');
      setConfirmPassword('');
    } else {
      setError(result.message);
    }

    setLoading(false);
  };

  return (
    <form className="space-y-6" onSubmit={handleSubmit}>
      {error && (
        <div className="p-3 bg-red-500/20 border border-red-400 rounded-xl text-red-200 flex items-center">
          <span className="mr-2">⚠️</span> {error}
        </div>
      )}

      {success && (
        <div className="p-3 bg-green-500/20 border border-green-400 rounded-xl text-green-200 flex items-center">
          <span className="mr-2">✅</span> {success}
        </div>
      )}

      <div>
        <label htmlFor="reg-username" className="block text-sm font-bold text-white/95 mb-2 drop-shadow-sm">
          Username 🧑‍💼
        </label>
        <div className="mt-1">
          <input
            id="reg-username"
            name="username"
            type="text"
            required
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-4 py-3 bg-white/20 border border-white/40 rounded-xl text-white placeholder-white/80 focus:outline-none focus:ring-2 focus:ring-[#ff6b81] focus:border-transparent transition-all duration-300 backdrop-blur-sm"
            placeholder="Choose a username..."
          />
        </div>
      </div>

      <div>
        <label htmlFor="reg-password" className="block text-sm font-bold text-white/95 mb-2 drop-shadow-sm">
          Password 🔐
        </label>
        <div className="mt-1">
          <input
            id="reg-password"
            name="password"
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-3 bg-white/20 border border-white/40 rounded-xl text-white placeholder-white/80 focus:outline-none focus:ring-2 focus:ring-[#ff6b81] focus:border-transparent transition-all duration-300 backdrop-blur-sm"
            placeholder="Create a strong password..."
          />
        </div>
        <p className="mt-2 text-xs text-white/80 drop-shadow-sm">
          Password must be at least 8 characters with uppercase, lowercase, number, and special character
        </p>
      </div>

      <div>
        <label htmlFor="reg-confirm-password" className="block text-sm font-bold text-white/95 mb-2 drop-shadow-sm">
          Confirm Password 🔄
        </label>
        <div className="mt-1">
          <input
            id="reg-confirm-password"
            name="confirm-password"
            type="password"
            required
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="w-full px-4 py-3 bg-white/20 border border-white/40 rounded-xl text-white placeholder-white/80 focus:outline-none focus:ring-2 focus:ring-[#ff6b81] focus:border-transparent transition-all duration-300 backdrop-blur-sm"
            placeholder="Confirm your password..."
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
              Registering...
            </span>
          ) : (
            'Register 📝'
          )}
        </button>
      </div>
    </form>
  );
}