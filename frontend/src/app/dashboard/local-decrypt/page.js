'use client';

import DashboardLayout from '../../../components/DashboardLayout';
import DecryptLocalFile from '../../../components/DecryptLocalFile';

export default function LocalDecryptPage() {
  return (
    <DashboardLayout>
      <div className="w-full">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Decrypt Local File</h1>
          <p className="text-gray-400">Upload an encrypted file (.enc) to decrypt it locally</p>
        </div>
        
        <DecryptLocalFile />
      </div>
    </DashboardLayout>
  );
}