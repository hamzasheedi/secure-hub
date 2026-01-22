/**
 * @file frontend/pages/index.js
 * @description Main landing page for SecureVault frontend
 */

export default function Home() {
  return (
    <div className="container">
      <h1>Welcome to SecureVault</h1>
      <p>Your secure file encryption and storage solution</p>
      <style jsx>{`
        .container {
          min-height: 100vh;
          padding: 0 0.5rem;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
        }
        
        h1 {
          margin: 0;
          line-height: 1.15;
          font-size: 4rem;
        }
        
        p {
          margin: 1rem 0;
          font-size: 1.5rem;
        }
      `}</style>
    </div>
  );
}