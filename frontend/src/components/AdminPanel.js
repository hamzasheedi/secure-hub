'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { adminAPI } from '../services/api';

export default function AdminPanel() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const { token, logout } = useAuth();
  const { showToast } = useToast();

  // Fetch all users
  const fetchUsers = async () => {
    try {
      setLoading(true);
      const data = await adminAPI.getUsers();
      setUsers(data);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  // Handle user activation
  const handleActivate = async (userId) => {
    try {
      await adminAPI.activateUser(userId);

      showToast('User activated successfully!', 'success');
      // Refresh the user list
      fetchUsers();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  // Handle user deactivation
  const handleDeactivate = async (userId) => {
    try {
      await adminAPI.deactivateUser(userId);

      showToast('User deactivated successfully!', 'success');
      // Refresh the user list
      fetchUsers();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  // Handle user promotion to admin
  const handlePromote = async (userId, username) => {
    if (!confirm(`Are you sure you want to promote user "${username}" to admin?`)) {
      return;
    }

    try {
      await adminAPI.promoteUser(userId);

      showToast(`User "${username}" promoted to admin successfully!`, 'success');
      // Refresh the user list
      fetchUsers();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  // Handle user demotion from admin
  const handleDemote = async (userId, username) => {
    if (!confirm(`Are you sure you want to demote admin "${username}" to regular user?`)) {
      return;
    }

    try {
      await adminAPI.demoteUser(userId);

      showToast(`Admin "${username}" demoted to user successfully!`, 'success');
      // Refresh the user list
      fetchUsers();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  // Load users on component mount
  useEffect(() => {
    fetchUsers();
  }, []);

  return (
    <div className="w-full">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">Admin Dashboard 🛠️</h1>
        <p className="text-white/95 text-lg">Manage users and system settings 👥</p>
      </div>

      <div className="bg-[#1a0f3d]/30 backdrop-blur-sm rounded-2xl p-6 border border-white/20 shadow-xl">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
          <h2 className="text-2xl font-bold text-white">User Management 👥</h2>
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#6C63FF]"></div>
          </div>
        ) : users.length === 0 ? (
          <div className="text-center py-12">
            <div className="mx-auto h-16 w-16 flex items-center justify-center rounded-full bg-gray-800 mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-white mb-1">No users found</h3>
            <p className="text-gray-400">There are currently no users in the system</p>
          </div>
        ) : (
          <div className="overflow-hidden border border-white/30 rounded-xl">
            <table className="min-w-full divide-y divide-white/30">
              <thead className="bg-white/10 backdrop-blur-sm">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-bold text-white/95 uppercase tracking-wider drop-shadow-sm">
                    User 👤
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-bold text-white/95 uppercase tracking-wider drop-shadow-sm">
                    Role 🏷️
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-bold text-white/95 uppercase tracking-wider drop-shadow-sm">
                    Status 📊
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-bold text-white/95 uppercase tracking-wider drop-shadow-sm">
                    Created ⏰
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-bold text-white/95 uppercase tracking-wider drop-shadow-sm">
                    Actions ⚙️
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white/10 backdrop-blur-sm divide-y divide-white/30">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-white/20 transition-colors duration-300 hover-lift">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-12 w-12 flex items-center justify-center rounded-xl bg-white/10 backdrop-blur-sm">
                          <span className="text-xl">👤</span>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-bold text-white">
                            {user.username}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-white/95 font-medium drop-shadow-sm">
                      <span className={`px-3 py-1 inline-flex text-xs leading-5 font-bold rounded-full ${
                        user.role === 'admin'
                          ? 'bg-gradient-to-r from-purple-500 to-indigo-500 text-white shadow-md'
                          : 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-md'
                      }`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-white/95 font-medium drop-shadow-sm">
                      <span className={`px-3 py-1 inline-flex text-xs leading-5 font-bold rounded-full ${
                        user.status === 'active'
                          ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-md'
                          : 'bg-gradient-to-r from-red-500 to-rose-500 text-white shadow-md'
                      }`}>
                        {user.status === 'active' ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-white/95 font-medium drop-shadow-sm">
                      {new Date(user.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end space-x-3">
                        {user.role === 'admin' ? (
                          <button
                            onClick={() => handleDemote(user.id, user.username)}
                            className="text-yellow-400 hover:text-yellow-300 hover:scale-110 transition-transform duration-200"
                            title="Demote from Admin"
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          </button>
                        ) : (
                          <button
                            onClick={() => handlePromote(user.id, user.username)}
                            className="text-purple-400 hover:text-purple-300 hover:scale-110 transition-transform duration-200"
                            title="Promote to Admin"
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          </button>
                        )}

                        {user.status === 'active' ? (
                          <button
                            onClick={() => handleDeactivate(user.id)}
                            className="text-red-400 hover:text-red-300 hover:scale-110 transition-transform duration-200 ml-2"
                            title="Deactivate User"
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                            </svg>
                          </button>
                        ) : (
                          <button
                            onClick={() => handleActivate(user.id)}
                            className="text-green-400 hover:text-green-300 hover:scale-110 transition-transform duration-200 ml-2"
                            title="Activate User"
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}