'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { vaultAPI } from '../services/api';
import PasswordModal from '../components/PasswordModal';
import DecryptLocalFile from '../components/DecryptLocalFile';

export default function VaultDashboard() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [passwordModal, setPasswordModal] = useState({ isOpen: false, action: '', fileId: null, fileName: '' });
  const router = useRouter();
  const { token } = useAuth();
  const { showToast } = useToast();

  // Fetch user files
  const fetchFiles = async () => {
    try {
      setLoading(true);
      const data = await vaultAPI.listFiles();
      setFiles(data);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  // Handle file download/decryption
  const handleDownload = (fileId, fileName) => {
    setPasswordModal({ isOpen: true, action: 'download', fileId, fileName });
  };

  // Handle encrypted file download
  const handleEncryptedDownload = async (fileId, fileName) => {
    try {
      // Disable the button during operation
      const btn = document.querySelector(`[data-file-id="${fileId}"][data-action="download-encrypted"]`);
      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mx-auto"></div>';
      }

      // Get the encrypted file from the API
      const response = await vaultAPI.downloadEncryptedFile(fileId);

      // Get the blob from the response
      const blob = await response.blob();

      // Create a download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${fileName}.enc`; // Add .enc extension to distinguish from original
      document.body.appendChild(link);
      link.click();

      // Clean up
      window.URL.revokeObjectURL(url);
      document.body.removeChild(link);

      showToast(`Encrypted file "${fileName}.enc" downloaded successfully!`, 'success');
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      // Re-enable the button after operation
      const btn = document.querySelector(`[data-file-id="${fileId}"][data-action="download-encrypted"]`);
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = `
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        `;
      }
    }
  };

  // Handle file preview
  const handlePreview = (fileId, fileName) => {
    setPasswordModal({ isOpen: true, action: 'preview', fileId, fileName });
  };

  // Handle password submission
  const handlePasswordSubmit = async (password) => {
    const { action, fileId, fileName } = passwordModal;
    setPasswordModal({ isOpen: false, action: '', fileId: null, fileName: '' });

    if (!password) {
      showToast('Password is required to decrypt the file.', 'error');
      return;
    }

    try {
      // Disable the button during operation
      const btn = document.querySelector(`[data-file-id="${fileId}"][data-action="${action}"]`);
      if (btn) {
        btn.disabled = true;
        if (action === 'download') {
          btn.innerHTML = '<div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mx-auto"></div>';
        } else {
          btn.innerHTML = '<div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mx-auto"></div>';
        }
      }

      // Get the response from the API
      const response = await vaultAPI.decryptFile(fileId, password);

      if (action === 'download') {
        // Handle download
        // The response should be a Response object, get the blob
        const blob = await response.blob();

        // Create a download link
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = fileName; // Use the original filename
        document.body.appendChild(link);
        link.click();

        // Clean up
        window.URL.revokeObjectURL(url);
        document.body.removeChild(link);

        showToast(`File "${fileName}" downloaded successfully!`, 'success');
      } else if (action === 'preview') {
        // Handle preview
        // Determine file type for appropriate preview
        const fileExtension = fileName.split('.').pop().toLowerCase();

        if (['txt', 'text', 'md', 'csv'].includes(fileExtension)) {
          // For text files, read the content and display in a modal
          const text = await response.text();
          // Create a simple modal to display text content
          const textWindow = window.open('', '_blank', 'width=800,height=600');
          textWindow.document.write(`
            <html>
              <head><title>Preview: ${fileName}</title></head>
              <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #fff; background: #2C2C3E; padding: 10px; border-radius: 4px;">${fileName}</h2>
                <pre style="white-space: pre-wrap; background: #1E1E2F; padding: 15px; border-radius: 4px; color: #E0E0E0; overflow: auto; max-height: 80%;">${text}</pre>
              </body>
            </html>
          `);
        } else if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(fileExtension)) {
          // For image files, create a blob URL and display in a new window
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);

          const imgWindow = window.open('', '_blank', 'width=800,height=600');
          imgWindow.document.write(`
            <html>
              <head><title>Preview: ${fileName}</title></head>
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
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);

          const pdfWindow = window.open('', '_blank', 'width=800,height=600');
          pdfWindow.document.write(`
            <html>
              <head><title>Preview: ${fileName}</title></head>
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
      }
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      // Re-enable the button after operation
      const btn = document.querySelector(`[data-file-id="${fileId}"][data-action="${action}"]`);
      if (btn) {
        btn.disabled = false;
        if (action === 'download') {
          btn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          `;
        } else {
          btn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
              <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
            </svg>
          `;
        }
      }
    }
  };


  // Handle file deletion
  const handleDelete = async (fileId, fileName) => {
    if (!confirm(`Are you sure you want to delete "${fileName}"?`)) {
      return;
    }

    try {
      await vaultAPI.deleteFile(fileId);

      showToast(`File "${fileName}" deleted successfully!`, 'success');
      // Refresh the file list
      fetchFiles();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  // Load files on component mount
  useEffect(() => {
    if (token) {
      fetchFiles();
    }
  }, [token]);

  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="w-full">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Your Secure Vault</h1>
        <p className="text-gray-400">Manage your encrypted files securely</p>
      </div>


      <DecryptLocalFile />

      <div className="bg-card rounded-xl p-6 border border-gray-700">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-white">Encrypted Files</h2>
          <button
            onClick={() => router.push('/dashboard/upload')}
            className="btn-primary px-4 py-2"
          >
            + Upload File
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#6C63FF]"></div>
          </div>
        ) : files.length === 0 ? (
          <div className="text-center py-12">
            <div className="mx-auto h-16 w-16 flex items-center justify-center rounded-full bg-gray-800 mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-white mb-1">No files yet</h3>
            <p className="text-gray-400 mb-4">Get started by uploading your first encrypted file</p>
            <button
              onClick={() => router.push('/dashboard/upload')}
              className="btn-primary"
            >
              Upload a File
            </button>
          </div>
        ) : (
          <div className="overflow-hidden border border-gray-700 rounded-lg">
            <table className="min-w-full divide-y divide-gray-700">
              <thead className="bg-[#252536]">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Filename
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Size
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Encrypted At
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Actions - Original
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Actions - Encrypted
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Delete
                  </th>
                </tr>
              </thead>
              <tbody className="bg-[#252536] divide-y divide-gray-700">
                {files.map((file) => (
                  <tr key={file.file_id} className="hover:bg-[#2a2a3a] transition-colors duration-150">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10 flex items-center justify-center rounded-md bg-gray-800">
                          {file.original_name.toLowerCase().endsWith('.pdf') ? (
                            <span className="text-red-400">📄</span>
                          ) : file.original_name.toLowerCase().endsWith('.jpg') ||
                               file.original_name.toLowerCase().endsWith('.jpeg') ||
                               file.original_name.toLowerCase().endsWith('.png') ? (
                            <span className="text-blue-400">🖼️</span>
                          ) : file.original_name.toLowerCase().endsWith('.txt') ? (
                            <span className="text-green-400">📝</span>
                          ) : (
                            <span className="text-gray-400">📁</span>
                          )}
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-white truncate max-w-xs">
                            {file.original_name}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      {formatFileSize(file.size)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      {new Date(file.encrypted_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-900 text-green-100">
                        ✅ Encrypted
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleDownload(file.file_id, file.original_name)}
                          className="text-green-400 hover:text-green-300"
                          title="Decrypt & Download Original"
                          data-file-id={file.file_id}
                          data-action="download"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                          </svg>
                        </button>
                        {(file.original_name.toLowerCase().endsWith('.jpg') ||
                          file.original_name.toLowerCase().endsWith('.jpeg') ||
                          file.original_name.toLowerCase().endsWith('.png') ||
                          file.original_name.toLowerCase().endsWith('.pdf') ||
                          file.original_name.toLowerCase().endsWith('.txt')) && (
                          <button
                            onClick={() => handlePreview(file.file_id, file.original_name)}
                            className="text-blue-400 hover:text-blue-300"
                            title="Preview Original"
                            data-file-id={file.file_id}
                            data-action="preview"
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                              <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                              <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                            </svg>
                          </button>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleEncryptedDownload(file.file_id, file.original_name)}
                          className="text-purple-400 hover:text-purple-300"
                          title="Download Encrypted File"
                          data-file-id={file.file_id}
                          data-action="download-encrypted"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                          </svg>
                        </button>
                        <button
                          className="text-gray-500 cursor-not-allowed"
                          title="Encrypted file preview not available"
                          disabled
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                            <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                          </svg>
                        </button>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => handleDelete(file.file_id, file.original_name)}
                        className="text-red-400 hover:text-red-300"
                        title="Delete"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Password Modal */}
      <PasswordModal
        isOpen={passwordModal.isOpen}
        onClose={() => setPasswordModal({ isOpen: false, action: '', fileId: null, fileName: '' })}
        onSubmit={handlePasswordSubmit}
        action={passwordModal.action}
      />
    </div>
  );
}