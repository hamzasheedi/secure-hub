/**
 * @file frontend/src/components/FileUpload.js
 * @description Component for uploading and encrypting files
 */

import { useState } from 'react';

export default function FileUpload() {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      setUploadStatus('Please select a file first');
      return;
    }

    setIsUploading(true);
    setUploadStatus('Uploading and encrypting...');

    // In a real implementation, this would connect to the backend API
    // For now, we'll simulate the process
    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setUploadStatus(`Successfully encrypted and stored: ${file.name}`);
    } catch (error) {
      setUploadStatus(`Upload failed: ${error.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="upload-container">
      <h2>Upload & Encrypt File</h2>
      <input 
        type="file" 
        onChange={handleFileChange} 
        disabled={isUploading}
      />
      <button 
        onClick={handleUpload} 
        disabled={!file || isUploading}
      >
        {isUploading ? 'Encrypting...' : 'Encrypt & Upload'}
      </button>
      {uploadStatus && <p className="status">{uploadStatus}</p>}
      
      <style jsx>{`
        .upload-container {
          margin: 20px;
          padding: 20px;
          border: 1px solid #ccc;
          border-radius: 4px;
        }
        
        h2 {
          margin-top: 0;
        }
        
        input, button {
          margin: 10px 0;
          padding: 8px;
        }
        
        button {
          background-color: #0070f3;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }
        
        button:disabled {
          background-color: #ccc;
          cursor: not-allowed;
        }
        
        .status {
          margin-top: 10px;
          padding: 10px;
          background-color: #f0f0f0;
          border-radius: 4px;
        }
      `}</style>
    </div>
  );
}