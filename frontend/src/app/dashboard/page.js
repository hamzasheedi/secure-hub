'use client';

import DashboardLayout from '../../components/DashboardLayout';
import VaultDashboard from '../../components/VaultDashboard';

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <VaultDashboard />
    </DashboardLayout>
  );
}