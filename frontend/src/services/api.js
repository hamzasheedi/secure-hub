// frontend/src/services/api.js

// Base API URL - can be configured via environment variable
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

/**
 * Generic API request function with error handling
 */
export const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  // Add authorization header if token is available
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }

  try {
    const response = await fetch(url, config);
    
    // If response is not OK, try to parse error details
    if (!response.ok) {
      let errorMessage = `HTTP error! status: ${response.status}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch (e) {
        // If we can't parse the error, use the status text
        errorMessage = response.statusText || errorMessage;
      }
      throw new Error(errorMessage);
    }
    
    // For successful responses, try to parse JSON
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    } else {
      // For non-JSON responses (e.g., file downloads), return the response object
      return response;
    }
  } catch (error) {
    console.error(`API request failed: ${endpoint}`, error);
    throw error;
  }
};

/**
 * Authentication API functions
 */
export const authAPI = {
  login: (credentials) => 
    apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    }),

  register: (userData) => 
    apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    }),

  logout: () => 
    apiRequest('/auth/logout', {
      method: 'POST',
    }),

  deleteAccount: () => 
    apiRequest('/auth/account', {
      method: 'DELETE',
    }),
};

/**
 * Vault API functions
 */
export const vaultAPI = {
  encryptFile: async (file, password) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('password', password);

    // For multipart requests, we need to remove Content-Type header
    // so the browser can set it with the correct boundary
    return apiRequest('/vault/encrypt', {
      method: 'POST',
      body: formData,
      headers: {}, // This will be handled by fetch automatically for FormData
    });
  },

  decryptFile: async (fileId, password) => {
    const url = `${API_BASE_URL}/vault/decrypt/${fileId}`;

    const config = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ password }),
    };

    // Add authorization header if token is available
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch (e) {
          // If we can't parse the error, use the status text
          errorMessage = response.statusText || errorMessage;
        }
        throw new Error(errorMessage);
      }

      // Return the response object directly for file downloads
      return response;
    } catch (error) {
      console.error(`API request failed: /vault/decrypt/${fileId}`, error);
      throw error;
    }
  },

  listFiles: () => 
    apiRequest('/vault/files'),

  deleteFile: (fileId) =>
    apiRequest(`/vault/file/${fileId}`, {
      method: 'DELETE',
    }),

  downloadEncryptedFile: async (fileId) => {
    const url = `${API_BASE_URL}/vault/download-encrypted/${fileId}`;

    const config = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    };

    // Add authorization header if token is available
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch (e) {
          // If we can't parse the error, use the status text
          errorMessage = response.statusText || errorMessage;
        }
        throw new Error(errorMessage);
      }

      // Return the response object directly for file downloads
      return response;
    } catch (error) {
      console.error(`API request failed: /vault/download-encrypted/${fileId}`, error);
      throw error;
    }
  },

  decryptLocalFile: async (file, password) => {
    const url = `${API_BASE_URL}/vault/decrypt-local`;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('password', password);

    const config = {
      method: 'POST',
      body: formData,
      // Don't set Content-Type header for FormData, let browser set it with boundary
    };

    // Add authorization header if token is available
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers = {
          ...config.headers,
          'Authorization': `Bearer ${token}`,
        };
      }
    }

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch (e) {
          // If we can't parse the error, use the status text
          errorMessage = response.statusText || errorMessage;
        }
        throw new Error(errorMessage);
      }

      // Return the response object directly for file downloads
      return response;
    } catch (error) {
      console.error(`API request failed: /vault/decrypt-local`, error);
      throw error;
    }
  },
};

/**
 * Admin API functions
 */
export const adminAPI = {
  getUsers: () => 
    apiRequest('/admin/users'),

  activateUser: (userId) => 
    apiRequest(`/admin/user/${userId}/activate`, {
      method: 'POST',
    }),

  deactivateUser: (userId) => 
    apiRequest(`/admin/user/${userId}/deactivate`, {
      method: 'POST',
    }),
};