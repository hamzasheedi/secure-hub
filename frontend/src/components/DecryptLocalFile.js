'use client';

import { useState, useRef, useCallback } from 'react';
import { useToast } from '../contexts/ToastContext';
import { vaultAPI } from '../services/api';

export default function DecryptLocalFile() {
  const [file, setFile] = useState(null);
  const [password, setPassword] = useState('');
  const [decryptionProgress, setDecryptionProgress] = useState(0);
  const [decrypting, setDecrypting] = useState(false);
  const [decryptedBlob, setDecryptedBlob] = useState(null);
  const [originalFilename, setOriginalFilename] = useState('');
  const fileInputRef = useRef(null);
  const { showToast } = useToast();

  // Drag and drop handlers
  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragEnter = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();

    const droppedFiles = Array.from(e.dataTransfer.files);
    processFiles(droppedFiles);
  }, []);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    processFiles(selectedFiles);
  };

  const processFiles = (selectedFiles) => {
    // Filter for .enc files only
    const encFiles = selectedFiles.filter(file => {
      if (!file.name.toLowerCase().endsWith('.enc')) {
        showToast(`File type not supported: ${file.name}. Only .enc files are allowed.`, 'error');
        return false;
      }

      const maxSize = 10 * 1024 * 1024; // 10MB
      if (file.size > maxSize) {
        showToast(`File too large: ${file.name}. Maximum size is 10MB.`, 'error');
        return false;
      }

      return true;
    });

    if (encFiles.length > 0) {
      const encFile = encFiles[0]; // Only allow one file at a time
      setFile({
        name: encFile.name,
        size: encFile.size,
        file: encFile
      });
    }
  };

  const handleDecrypt = async () => {
    if (!file) {
      showToast('Please select an encrypted file first.', 'error');
      return;
    }

    if (!password) {
      showToast('Please enter the password used for encryption.', 'error');
      return;
    }

    setDecrypting(true);
    setDecryptionProgress(0);

    try {
      // Simulate progress during decryption
      const progressInterval = setInterval(() => {
        setDecryptionProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 200);

      // Call the backend to decrypt the file
      const response = await vaultAPI.decryptLocalFile(file.file, password);

      clearInterval(progressInterval);
      setDecryptionProgress(100);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.message || `HTTP error! status: ${response.status}`);
      }

      // Get the decrypted file as blob
      const blob = await response.blob();
      
      // Extract original filename from Content-Disposition header
      const disposition = response.headers.get('Content-Disposition');
      let filename = 'decrypted_file';
      if (disposition && disposition.indexOf('filename=') !== -1) {
        filename = disposition.substring(disposition.indexOf('filename=') + 9).replace(/"/g, '');
      }
      
      setDecryptedBlob(blob);
      setOriginalFilename(filename);
      showToast('File decrypted successfully!', 'success');
    } catch (err) {
      showToast(err.message, 'error');
      setDecryptedBlob(null);
      setOriginalFilename('');
    } finally {
      setDecrypting(false);
      setTimeout(() => setDecryptionProgress(0), 1000);
    }
  };

  const handleDownload = () => {
    if (!decryptedBlob || !originalFilename) return;

    // Create a download link
    const url = window.URL.createObjectURL(decryptedBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = originalFilename;
    document.body.appendChild(link);
    link.click();

    // Clean up
    window.URL.revokeObjectURL(url);
    document.body.removeChild(link);
    showToast(`File "${originalFilename}" downloaded successfully!`, 'success');
  };

  const handlePreview = () => {
    if (!decryptedBlob || !originalFilename) return;

    // Determine file type for appropriate preview
    const fileExtension = originalFilename.split('.').pop().toLowerCase();

    if (['txt', 'text', 'md', 'csv'].includes(fileExtension)) {
      // For text files, read the content and display in a modal
      const reader = new FileReader();
      reader.onload = function(e) {
        const text = e.target.result;
        // Create a simple modal to display text content
        const textWindow = window.open('', '_blank', 'width=800,height=600');
        textWindow.document.write(`
          <html>
            <head><title>Preview: ${originalFilename}</title></head>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
              <h2 style="color: #fff; background: #2C2C3E; padding: 10px; border-radius: 4px;">${originalFilename}</h2>
              <pre style="white-space: pre-wrap; background: #1E1E2F; padding: 15px; border-radius: 4px; color: #E0E0E0; overflow: auto; max-height: 80%;">${text}</pre>
            </body>
          </html>
        `);
      };
      reader.readAsText(decryptedBlob);
    } else if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(fileExtension)) {
      // For image files, create a blob URL and display in a new window
      const url = window.URL.createObjectURL(decryptedBlob);

      const imgWindow = window.open('', '_blank', 'width=800,height=600');
      imgWindow.document.write(`
        <html>
          <head><title>Preview: ${originalFilename}</title></head>
          <body style="margin:0; padding:20px; background:#000; display:flex; justify-content:center; align-items:center; min-height:100vh;">
            <img src="${url}" alt="Preview" style="max-width:100%; max-height:90vh; border-radius:4px;" />
            <script>
              window.addEventListener('beforeunload', function() {
                URL.revokeObjectURL('${url}');
              });
            </script>
          </body>
        </html>
      `);
    } else if (fileExtension === 'pdf') {
      // For PDF files, create a blob URL and embed in a new window
      const url = window.URL.createObjectURL(decryptedBlob);

      const pdfWindow = window.open('', '_blank', 'width=800,height=600');
      pdfWindow.document.write(`
        <html>
          <head><title>Preview: ${originalFilename}</title></head>
          <body style="margin:0; padding:0; height:100%;">
            <embed src="${url}" type="application/pdf" width="100%" height="100%" />
            <script>
              window.addEventListener('beforeunload', function() {
                URL.revokeObjectURL('${url}');
              });
            </script>
          </body>
        </html>
      `);
    } else {
      // For other file types that can't be previewed, notify the user
      showToast(`Preview not available for ${fileExtension.toUpperCase()} files. Please download to view.`, 'info');
    }
  };

  const resetForm = () => {
    setFile(null);
    setPassword('');
    setDecryptionProgress(0);
    setDecrypting(false);
    setDecryptedBlob(null);
    setOriginalFilename('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="bg-card rounded-xl p-6 border border-gray-700 mb-8">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-white mb-2">Decrypt Local File</h2>
        <p className="text-gray-400">Upload an encrypted file (.enc) to decrypt it locally</p>
      </div>

      <div
        className="mb-6 p-6 border-2 border-dashed border-gray-600 rounded-lg hover:border-[#6C63FF] transition-colors duration-200"
        onDragOver={handleDragOver}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="text-center">
          <div
            className="cursor-pointer hover:bg-[#2a2a3a] transition-colors duration-200 rounded-lg p-4"
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="flex flex-col items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-gray-500 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p className="text-lg font-medium text-gray-300">Drag & drop encrypted file here</p>
              <p className="text-gray-500 mt-1">or click to browse</p>
              <p className="text-sm text-gray-600 mt-2">Supports: .enc files (Max 10MB)</p>
            </div>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".enc"
              className="hidden"
            />
          </div>
        </div>
      </div>

      {file && (
        <div className="mb-6 p-4 bg-[#252536] rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="mr-4">
                <div className="w-10 h-10 bg-purple-900/30 rounded flex items-center justify-center">
                  <span className="text-purple-400">🔒</span>
                </div>
              </div>
              <div>
                <p className="font-medium text-white truncate max-w-xs">{file.name}</p>
                <p className="text-sm text-gray-400">{formatFileSize(file.size)}</p>
              </div>
            </div>
            <button
              onClick={resetForm}
              className="text-red-400 hover:text-red-300"
              title="Remove file"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {file && (
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter the password used for encryption"
            className="w-full px-4 py-2 bg-[#252536] border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] text-white"
          />
        </div>
      )}

      {decryptionProgress > 0 && decryptionProgress < 100 && (
        <div className="mb-6">
          <div className="w-full bg-gray-700 rounded-full h-2.5">
            <div
              className="bg-gradient-to-r from-[#6C63FF] to-[#9B5DE5] h-2.5 rounded-full transition-all duration-300"
              style={{ width: `${decryptionProgress}%` }}
            ></div>
          </div>
          <p className="text-xs text-gray-400 mt-1 text-right">{Math.round(decryptionProgress)}%</p>
        </div>
      )}

      {file && (
        <div className="flex space-x-4 mb-6">
          <button
            onClick={handleDecrypt}
            disabled={decrypting || !password}
            className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors duration-200 ${
              decrypting || !password
                ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                : 'bg-[#6C63FF] text-white hover:bg-[#5a52e0]'
            }`}
          >
            {decrypting ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Decrypting...
              </span>
            ) : (
              'Decrypt File'
            )}
          </button>
          
          <button
            onClick={resetForm}
            className="py-2 px-4 bg-gray-700 text-white rounded-lg font-medium hover:bg-gray-600 transition-colors duration-200"
          >
            Reset
          </button>
        </div>
      )}

      {decryptedBlob && (
        <div className="mt-6 p-4 bg-[#252536] rounded-lg border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-white">Decryption Successful!</h3>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-900 text-green-100">
              ✅ Decrypted
            </span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={handlePreview}
              className="flex items-center justify-center py-2 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-500 transition-colors duration-200"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
              </svg>
              Preview File
            </button>
            
            <button
              onClick={handleDownload}
              className="flex items-center justify-center py-2 px-4 bg-green-600 text-white rounded-lg font-medium hover:bg-green-500 transition-colors duration-200"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
              Download Original
            </button>
          </div>
        </div>
      )}
    </div>
  );
}