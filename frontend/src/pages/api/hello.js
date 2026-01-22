/**
 * @file frontend/pages/api/hello.js
 * @description Basic API route for testing
 */

export default function handler(req, res) {
  res.status(200).json({ message: 'Hello from SecureVault API!' });
}