import { useEffect } from 'react';

export default function FilePreviewModal({ file, isOpen, onClose, onDecrypt }) {
  useEffect(() => {
    // Close modal on Escape key press
    const handleEsc = (event) => {
      if (event.keyCode === 27) {
        onClose();
      }
    };

    window.addEventListener('keydown', handleEsc);

    return () => {
      window.removeEventListener('keydown', handleEsc);
    };
  }, [onClose]);

  if (!isOpen || !file) return null;

  const handleDecryptClick = () => {
    onDecrypt(file.file_id, file.original_name);
    onClose(); // Close the preview modal after initiating decrypt
  };

  const fileExtension = file.original_name.toLowerCase().split('.').pop();
  const isImage = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(fileExtension);
  const isPDF = fileExtension === 'pdf';
  const isText = ['txt', 'text', 'md', 'csv', 'json', 'xml', 'js', 'ts', 'html', 'css', 'py', 'java', 'cpp', 'c', 'sql'].includes(fileExtension);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-[#2C2C3E] rounded-xl max-w-4xl max-h-full w-full overflow-auto">
        <div className="p-4 flex justify-between items-center border-b border-gray-700">
          <h3 className="text-lg font-semibold text-white truncate max-w-xs">{file.original_name}</h3>
          <div className="flex space-x-2">
            <button 
              onClick={handleDecryptClick}
              className="text-blue-400 hover:text-blue-300"
              title="Decrypt & Download"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-white"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        <div className="p-4 flex items-center justify-center min-h-[70vh]">
          {isImage && (
            <img 
              src={`/api/preview/${file.file_id}`} 
              alt={file.original_name}
              className="max-w-full max-h-[70vh] object-contain"
              onError={(e) => {
                // If direct image access fails, we'll handle it differently
                e.target.onerror = null;
                e.target.src = "/placeholder-image.jpg";
              }}
            />
          )}
          
          {isPDF && (
            <div className="w-full h-[70vh] flex flex-col items-center justify-center text-gray-400">
              <div className="text-center mb-4">
                <div className="mx-auto h-16 w-16 flex items-center justify-center rounded-full bg-red-900/30 mb-2">
                  <span className="text-2xl">📄</span>
                </div>
                <p>PDF Preview not available in modal</p>
                <p className="text-sm mt-2">Click the download icon to decrypt and view</p>
              </div>
              <button
                onClick={handleDecryptClick}
                className="btn-primary mt-4"
              >
                Decrypt & Download
              </button>
            </div>
          )}
          
          {isText && (
            <div className="w-full h-[70vh] flex flex-col">
              <div className="bg-[#1E1E2F] p-2 rounded-t-lg">
                <div className="flex space-x-1">
                  <div className="w-3 h-3 rounded-full bg-red-500"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                  <div className="w-3 h-3 rounded-full bg-green-500"></div>
                </div>
              </div>
              <pre className="w-full h-full bg-[#1E1E2F] text-green-400 p-4 overflow-auto text-sm">
                {file.original_name} content would appear here after decryption
              </pre>
            </div>
          )}
          
          {!isImage && !isPDF && !isText && (
            <div className="text-center">
              <div className="mx-auto h-16 w-16 flex items-center justify-center rounded-full bg-gray-800 mb-4">
                <span className="text-2xl">📁</span>
              </div>
              <p className="text-gray-400">Preview not available for this file type</p>
              <p className="text-sm text-gray-500 mt-2">File: {file.original_name}</p>
              <button
                onClick={handleDecryptClick}
                className="btn-primary mt-4"
              >
                Decrypt & Download
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}