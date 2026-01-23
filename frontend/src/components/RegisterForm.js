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
        <div className="p-3 bg-red-900/30 border border-red-700 rounded-lg text-red-300">
          {error}
        </div>
      )}

      {success && (
        <div className="p-3 bg-green-900/30 border border-green-700 rounded-lg text-green-300">
          {success}
        </div>
      )}

      <div>
        <label htmlFor="reg-username" className="block text-sm font-medium text-gray-300 mb-1">
          Username
        </label>
        <div className="mt-1">
          <input
            id="reg-username"
            name="username"
            type="text"
            required
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-3 py-2 bg-[#252536] border border-gray-600 rounded-md text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#6C63FF] focus:border-transparent"
          />
        </div>
      </div>

      <div>
        <label htmlFor="reg-password" className="block text-sm font-medium text-gray-300 mb-1">
          Password
        </label>
        <div className="mt-1">
          <input
            id="reg-password"
            name="password"
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 bg-[#252536] border border-gray-600 rounded-md text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#6C63FF] focus:border-transparent"
          />
        </div>
        <p className="mt-1 text-xs text-gray-500">
          Password must be at least 8 characters long and contain uppercase, lowercase, number, and special character
        </p>
      </div>

      <div>
        <label htmlFor="reg-confirm-password" className="block text-sm font-medium text-gray-300 mb-1">
          Confirm Password
        </label>
        <div className="mt-1">
          <input
            id="reg-confirm-password"
            name="confirm-password"
            type="password"
            required
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="w-full px-3 py-2 bg-[#252536] border border-gray-600 rounded-md text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#6C63FF] focus:border-transparent"
          />
        </div>
      </div>

      <div>
        <button
          type="submit"
          disabled={loading}
          className="w-full btn-primary py-2.5 text-sm font-medium"
        >
          {loading ? 'Registering...' : 'Register'}
        </button>
      </div>
    </form>
  );
}