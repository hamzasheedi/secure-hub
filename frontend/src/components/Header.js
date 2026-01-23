'use client';

import { useAuth } from '../contexts/AuthContext';

export default function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="sticky top-0 z-40 bg-[#2C2C3E] border-b border-gray-700">
      <div className="flex items-center justify-between h-16 px-6">
        <div className="flex items-center">
          <h2 className="text-lg font-semibold text-white capitalize">
            {user?.role === 'admin' ? 'Admin Dashboard' : 'User Dashboard'}
          </h2>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-[#6C63FF] to-[#9B5DE5] flex items-center justify-center text-white font-medium">
              {user?.username?.charAt(0)?.toUpperCase() || 'U'}
            </div>
            <span className="text-white text-sm">{user?.username}</span>
          </div>
          <button
            onClick={logout}
            className="btn-secondary text-sm"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}