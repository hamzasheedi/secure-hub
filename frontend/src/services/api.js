/**
 * @file frontend/src/services/api.js
 * @description API service for communicating with SecureVault backend
 */

class ApiService {
  constructor(baseURL) {
    this.baseURL = baseURL || process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
  }

  /**
   * Set authentication token for subsequent requests
   */
  setAuthToken(token) {
    if (token) {
      this.authToken = `Bearer ${token}`;
    } else {
      delete this.authToken;
    }
  }

  /**
   * Make an API request
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(this.authToken && { 'Authorization': this.authToken }),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  /**
   * Upload and encrypt a file
   */
  async uploadAndEncrypt(file, password) {
    const formData = new FormData();
    formData.append('file', file);
    // In a real implementation, password would be sent securely
    // For now, we're using a placeholder approach
    
    const response = await fetch(`${this.baseURL}/vault/encrypt`, {
      method: 'POST',
      headers: {
        // Don't include Content-Type header when using FormData
        // The browser will set it with the correct boundary
        'Authorization': this.authToken,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  /**
   * Get user's encrypted files
   */
  async getUserFiles() {
    return this.request('/vault/files');
  }

  /**
   * Decrypt a file
   */
  async decryptFile(fileId) {
    // This would typically return a file download
    return this.request(`/vault/decrypt/${fileId}`, {
      method: 'POST',
    });
  }

  /**
   * Delete a file
   */
  async deleteFile(fileId) {
    return this.request(`/vault/file/${fileId}`, {
      method: 'DELETE',
    });
  }

  /**
   * User registration
   */
  async register(username, password) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  /**
   * User login
   */
  async login(username, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  /**
   * User logout
   */
  async logout() {
    return this.request('/auth/logout', {
      method: 'POST',
    });
  }

  /**
   * Delete user account
   */
  async deleteAccount() {
    return this.request('/auth/account', {
      method: 'DELETE',
    });
  }

  /**
   * Get all users (admin only)
   */
  async getAllUsers() {
    return this.request('/admin/users');
  }

  /**
   * Deactivate a user (admin only)
   */
  async deactivateUser(userId) {
    return this.request(`/admin/user/${userId}/deactivate`, {
      method: 'POST',
    });
  }

  /**
   * Activate a user (admin only)
   */
  async activateUser(userId) {
    return this.request(`/admin/user/${userId}/activate`, {
      method: 'POST',
    });
  }
}

// Create a singleton instance
const apiService = new ApiService();

export default apiService;