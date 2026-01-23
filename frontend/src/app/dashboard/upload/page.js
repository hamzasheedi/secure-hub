'use client';

import { useState, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../../contexts/AuthContext';
import { useToast } from '../../../contexts/ToastContext';
import { vaultAPI } from '../../../services/api';
import PasswordModal from '../../../components/PasswordModal';

export default function UploadPage() {
  const [files, setFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState({});
  const [uploading, setUploading] = useState({});
  const [passwordModal, setPasswordModal] = useState({ isOpen: false, fileId: null, fileName: '' });
  const fileInputRef = useRef(null);
  const router = useRouter();
  const { token } = useAuth();
  const { showToast } = useToast();

  if (!token) {
    router.push('/');
    return null;
  }

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
    // Validate file types and sizes
    const validFiles = selectedFiles.filter(file => {
      const validTypes = ['image/jpeg', 'image/png', 'application/pdf', 'application/zip', 'text/plain'];
      const maxSize = 10 * 1024 * 1024; // 10MB

      if (!validTypes.includes(file.type)) {
        alert(`File type not supported: ${file.type}. Only JPEG, PNG, PDF, ZIP, and TXT files are allowed.`);
        return false;
      }

      if (file.size > maxSize) {
        alert(`File too large: ${file.name}. Maximum size is 10MB.`);
        return false;
      }

      return true;
    });

    setFiles(prev => [...prev, ...validFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      name: file.name,
      size: file.size,
      type: file.type
    }))]);
  };

  const handleFileUpload = (fileId) => {
    const fileObj = files.find(f => f.id === fileId);
    if (!fileObj) return;

    setPasswordModal({ isOpen: true, fileId, fileName: fileObj.name });
  };

  const handlePasswordSubmit = async (password) => {
    const { fileId } = passwordModal;
    setPasswordModal({ isOpen: false, fileId: null, fileName: '' });

    const fileObj = files.find(f => f.id === fileId);
    if (!fileObj) return;

    if (!password) {
      showToast('Password is required to encrypt the file.', 'error');
      return;
    }

    try {
      setUploading(prev => ({ ...prev, [fileId]: true }));
      setUploadProgress(prev => ({ ...prev, [fileId]: 0 }));

      // Simulate upload progress
      const interval = setInterval(() => {
        setUploadProgress(prev => {
          const current = prev[fileId] || 0;
          if (current >= 90) {
            clearInterval(interval);
            return prev;
          }
          return { ...prev, [fileId]: current + 10 };
        });
      }, 200);

      // Perform actual upload with password
      const result = await vaultAPI.encryptFile(fileObj.file, password);

      clearInterval(interval);
      setUploadProgress(prev => ({ ...prev, [fileId]: 100 }));

      showToast(`File "${result.original_name}" encrypted successfully!`, 'success');

      // Remove uploaded file from the list after a delay
      setTimeout(() => {
        setFiles(prev => prev.filter(f => f.id !== fileId));
        setUploading(prev => {
          const newUploading = { ...prev };
          delete newUploading[fileId];
          return newUploading;
        });
        setUploadProgress(prev => {
          const newProgress = { ...prev };
          delete newProgress[fileId];
          return newProgress;
        });
      }, 1500);
    } catch (err) {
      showToast(err.message, 'error');
      setUploading(prev => {
        const newUploading = { ...prev };
        delete newUploading[fileId];
        return newUploading;
      });
      setUploadProgress(prev => {
        const newProgress = { ...prev };
        delete newProgress[fileId];
        return newProgress;
      });
    }
  };

  const removeFile = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6 sm:mb-8">
        <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">Upload & Encrypt Files 📤</h1>
        <p className="text-white/95 text-base sm:text-lg">Select files to encrypt and store in your secure vault 🔐</p>
      </div>


      <div
        className="bg-[#1a0f3d]/30 backdrop-blur-sm rounded-2xl p-4 sm:p-6 mb-8 border-2 border-dashed border-white/50 hover:border-[#ff6b81] transition-colors duration-300 hover-lift"
        onDragOver={handleDragOver}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="mb-4 sm:mb-6">
          <label className="block text-sm font-bold text-white/95 mb-2">
            Select Files 📁
          </label>
          <div
            className="p-6 sm:p-8 text-center cursor-pointer hover:bg-white/20 transition-colors duration-300 rounded-2xl"
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="flex flex-col items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-12 sm:h-16 w-12 sm:w-16 text-white/80 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p className="text-lg sm:text-xl font-bold text-white">Drag & drop files here</p>
              <p className="text-white/80 mt-2">or click to browse</p>
              <p className="text-white/70 mt-2 text-sm sm:text-base">Supports: JPEG, PNG, PDF, ZIP, TXT (Max 10MB each) 📦</p>
            </div>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              multiple
              className="hidden"
            />
          </div>
        </div>
      </div>

      {files.length > 0 && (
        <div className="bg-[#1a0f3d]/30 backdrop-blur-sm rounded-2xl p-4 sm:p-6 border border-white/20 shadow-xl">
          <h2 className="text-xl sm:text-2xl font-bold text-white mb-4">Selected Files 📁</h2>
          <div className="space-y-4">
            {files.map((fileObj) => (
              <div key={fileObj.id} className="flex flex-col sm:flex-row items-center justify-between p-4 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/30 hover-lift gap-4">
                <div className="flex items-center w-full sm:w-auto">
                  <div className="mr-4">
                    {fileObj.type.startsWith('image/') ? (
                      <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center">
                        <span className="text-white text-lg sm:text-xl">🖼️</span>
                      </div>
                    ) : fileObj.type === 'application/pdf' ? (
                      <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-r from-red-500 to-rose-500 rounded-xl flex items-center justify-center">
                        <span className="text-white text-lg sm:text-xl">📄</span>
                      </div>
                    ) : (
                      <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-r from-gray-500 to-slate-500 rounded-xl flex items-center justify-center">
                        <span className="text-white text-lg sm:text-xl">📁</span>
                      </div>
                    )}
                  </div>
                  <div className="truncate">
                    <p className="font-bold text-white truncate max-w-[150px] sm:max-w-xs">{fileObj.name}</p>
                    <p className="text-sm text-white/80">{(fileObj.size / 1024 / 1024).toFixed(2)} MB</p>
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row items-center space-y-2 sm:space-y-0 sm:space-x-3 w-full sm:w-auto">
                  {uploadProgress[fileObj.id] > 0 && uploadProgress[fileObj.id] < 100 && (
                    <div className="w-full sm:w-32">
                      <div className="w-full bg-white/30 rounded-full h-2.5">
                        <div
                          className="bg-gradient-to-r from-[#ff6b81] to-[#6b5bff] h-2.5 rounded-full transition-all duration-300"
                          style={{ width: `${uploadProgress[fileObj.id]}%` }}
                        ></div>
                      </div>
                      <p className="text-xs text-white/80 mt-1 text-right">{Math.round(uploadProgress[fileObj.id])}%</p>
                    </div>
                  )}

                  {!uploading[fileObj.id] && uploadProgress[fileObj.id] !== 100 ? (
                    <>
                      <button
                        onClick={() => handleFileUpload(fileObj.id)}
                        className="btn-primary text-sm sm:text-base font-bold px-4 py-2 sm:px-6 sm:py-2.5 hover-lift w-full sm:w-auto"
                      >
                        Encrypt 🔐
                      </button>
                      <button
                        onClick={() => removeFile(fileObj.id)}
                        className="btn-secondary text-sm sm:text-base font-bold px-4 py-2 sm:px-6 sm:py-2.5 hover-lift w-full sm:w-auto"
                      >
                        Remove 🗑️
                      </button>
                    </>
                  ) : uploading[fileObj.id] ? (
                    <button
                      disabled
                      className="btn-primary text-sm sm:text-base font-bold px-4 py-2 sm:px-6 sm:py-2.5 opacity-70 w-full sm:w-auto"
                    >
                      Encrypting... 🔓
                    </button>
                  ) : (
                    <span className="text-green-400 text-sm sm:text-base font-bold w-full sm:w-auto text-center">✓ Encrypted ✅</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Password Modal */}
      <PasswordModal
        isOpen={passwordModal.isOpen}
        onClose={() => setPasswordModal({ isOpen: false, fileId: null, fileName: '' })}
        onSubmit={handlePasswordSubmit}
        action="encrypt"
      />
    </div>
  );
}