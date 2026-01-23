'use client';

import { useEffect } from 'react';

export default function Toast({ message, type, isVisible, onClose }) {
  if (!isVisible) return null;

  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 5000); // Auto-hide after 5 seconds

    return () => clearTimeout(timer);
  }, [onClose]);

  const bgColor = type === 'success' ? 'bg-gradient-to-r from-green-500 to-emerald-500' :
                  type === 'error' ? 'bg-gradient-to-r from-red-500 to-rose-500' :
                  'bg-gradient-to-r from-yellow-500 to-orange-500';
  const textColor = 'text-white';

  return (
    <div className={`fixed top-4 right-4 z-50 p-4 rounded-2xl ${bgColor} ${textColor} min-w-[300px] shadow-xl backdrop-blur-sm border border-white/30 transform transition-all duration-300 hover:scale-105`}>
      <div className="flex items-start">
        <div className="flex-1 flex items-center">
          <span className="mr-2 drop-shadow-sm">
            {type === 'success' ? '✅' : type === 'error' ? '❌' : '⚠️'}
          </span>
          <span className="font-bold drop-shadow-sm">{message}</span>
        </div>
        <button
          onClick={onClose}
          className="ml-4 text-white/90 hover:text-white focus:outline-none hover:scale-110 transition-transform duration-200"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </button>
      </div>
    </div>
  );
}