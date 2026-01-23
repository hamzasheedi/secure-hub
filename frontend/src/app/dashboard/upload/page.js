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
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Upload & Encrypt Files</h1>
        <p className="text-gray-400">Select files to encrypt and store in your secure vault</p>
      </div>


      <div
        className="bg-card rounded-xl p-6 mb-8 border-2 border-dashed border-gray-600 hover:border-[#6C63FF] transition-colors duration-200"
        onDragOver={handleDragOver}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Select Files
          </label>
          <div
            className="p-8 text-center cursor-pointer hover:bg-[#2a2a3a] transition-colors duration-200 rounded-lg"
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="flex flex-col items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-gray-500 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p className="text-lg font-medium text-gray-300">Drag & drop files here</p>
              <p className="text-gray-500 mt-1">or click to browse</p>
              <p className="text-sm text-gray-600 mt-2">Supports: JPEG, PNG, PDF, ZIP, TXT (Max 10MB each)</p>
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
        <div className="bg-card rounded-xl p-6 border border-gray-700">
          <h2 className="text-xl font-semibold text-white mb-4">Selected Files</h2>
          <div className="space-y-4">
            {files.map((fileObj) => (
              <div key={fileObj.id} className="flex items-center justify-between p-4 bg-[#252536] rounded-lg border border-gray-700">
                <div className="flex items-center">
                  <div className="mr-4">
                    {fileObj.type.startsWith('image/') ? (
                      <div className="w-10 h-10 bg-blue-900/30 rounded flex items-center justify-center">
                        <span className="text-blue-400">🖼️</span>
                      </div>
                    ) : fileObj.type === 'application/pdf' ? (
                      <div className="w-10 h-10 bg-red-900/30 rounded flex items-center justify-center">
                        <span className="text-red-400">📄</span>
                      </div>
                    ) : (
                      <div className="w-10 h-10 bg-gray-700 rounded flex items-center justify-center">
                        <span className="text-gray-400">📁</span>
                      </div>
                    )}
                  </div>
                  <div>
                    <p className="font-medium text-white truncate max-w-xs">{fileObj.name}</p>
                    <p className="text-sm text-gray-400">{(fileObj.size / 1024 / 1024).toFixed(2)} MB</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  {uploadProgress[fileObj.id] > 0 && uploadProgress[fileObj.id] < 100 && (
                    <div className="w-32">
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-[#6C63FF] to-[#9B5DE5] h-2 rounded-full transition-all duration-300"
                          style={{ width: `${uploadProgress[fileObj.id]}%` }}
                        ></div>
                      </div>
                      <p className="text-xs text-gray-400 mt-1 text-right">{Math.round(uploadProgress[fileObj.id])}%</p>
                    </div>
                  )}

                  {!uploading[fileObj.id] && uploadProgress[fileObj.id] !== 100 ? (
                    <>
                      <button
                        onClick={() => handleFileUpload(fileObj.id)}
                        className="btn-primary text-sm px-4 py-2"
                      >
                        Encrypt
                      </button>
                      <button
                        onClick={() => removeFile(fileObj.id)}
                        className="btn-secondary text-sm px-4 py-2"
                      >
                        Remove
                      </button>
                    </>
                  ) : uploading[fileObj.id] ? (
                    <button
                      disabled
                      className="btn-primary text-sm px-4 py-2 opacity-70"
                    >
                      Encrypting...
                    </button>
                  ) : (
                    <span className="text-green-400 text-sm">✓ Encrypted</span>
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