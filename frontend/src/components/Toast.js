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

  const bgColor = type === 'success' ? 'bg-green-900/80' : 'bg-red-900/80';
  const borderColor = type === 'success' ? 'border-green-700' : 'border-red-700';
  const textColor = type === 'success' ? 'text-green-300' : 'text-red-300';

  return (
    <div className={`fixed top-4 right-4 z-50 p-4 rounded-lg border ${bgColor} ${borderColor} ${textColor} min-w-[300px] shadow-lg`}>
      <div className="flex items-start">
        <div className="flex-1">
          {message}
        </div>
        <button 
          onClick={onClose}
          className="ml-4 text-gray-400 hover:text-white focus:outline-none"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </button>
      </div>
    </div>
  );
}