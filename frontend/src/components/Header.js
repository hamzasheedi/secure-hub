'use client';

import { useAuth } from '../contexts/AuthContext';

export default function Header() {
  const { user, logout } = useAuth();

  // Function to toggle sidebar - this will trigger the event listener in DashboardLayout
  const toggleSidebar = () => {
    // Dispatch custom event to toggle sidebar
    window.dispatchEvent(new CustomEvent('toggleSidebar'));
  };

  return (
    <header className="sticky top-0 z-40 bg-[#1a0f3d]/50 backdrop-blur-lg border-b border-white/30">
      <div className="flex items-center justify-between h-16 px-4 sm:px-6">
        <div className="flex items-center">
          {/* Hamburger menu button for mobile */}
          <button
            className="md:hidden mr-3 p-2 rounded-lg bg-[#1a0f3d]/50 backdrop-blur-lg text-white border border-white/30"
            onClick={toggleSidebar}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <h2 className="text-lg sm:text-xl font-bold text-white capitalize">
            {user?.role === 'admin' ? 'Admin Dashboard 🛠️' : 'User Dashboard 🗂️'}
          </h2>
        </div>
        <div className="flex items-center space-x-2 sm:space-x-3">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-gradient-to-r from-[#ff6b81] to-[#6b5bff] flex items-center justify-center text-white font-bold text-sm sm:text-base">
              {user?.username?.charAt(0)?.toUpperCase() || 'U'}
            </div>
            <div className="hidden md:block">
              <p className="text-white font-medium text-sm sm:text-base">{user?.username}</p>
              <p className="text-xs text-white/80">{user?.role === 'admin' ? 'Admin 👑' : 'User 👤'}</p>
            </div>
          </div>
          <button
            onClick={logout}
            className="btn-secondary text-xs sm:text-sm font-bold hover-lift px-2 py-1 sm:px-3 sm:py-1.5"
          >
            Logout 🚪
          </button>
        </div>
      </div>
    </header>
  );
}