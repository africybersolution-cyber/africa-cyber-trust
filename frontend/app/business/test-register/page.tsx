'use client';

import { useState } from 'react';

export default function TestRegisterPage() {
  const [selected, setSelected] = useState('dns');
  const [clicks, setClicks] = useState(0);

  return (
    <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto', background: '#0A1628', minHeight: '100vh' }}>
      <h1 style={{ color: 'white', marginBottom: '20px' }}>TEST PAGE - Click Counter</h1>

      <div style={{ background: '#1E3A5F', padding: '20px', borderRadius: '10px', marginBottom: '20px', border: '2px solid #0047AB' }}>
        <p style={{ color: 'white', fontSize: '24px', fontWeight: 'bold' }}>
          Clicks: {clicks}
        </p>
        <p style={{ color: '#DAA520', fontSize: '18px' }}>
          Selected: {selected.toUpperCase()}
        </p>
      </div>

      <button
        onClick={() => {
          setClicks(clicks + 1);
          setSelected('dns');
          alert('DNS CLICKED!');
        }}
        style={{
          width: '100%',
          padding: '30px',
          marginBottom: '20px',
          background: selected === 'dns' ? '#0047AB' : '#1E3A5F',
          border: selected === 'dns' ? '4px solid #DAA520' : '2px solid #0047AB',
          borderRadius: '15px',
          color: 'white',
          fontSize: '24px',
          fontWeight: 'bold',
          cursor: 'pointer',
        }}
      >
        ✅ DNS TXT RECORD {selected === 'dns' && '← SELECTED'}
      </button>

      <button
        onClick={() => {
          setClicks(clicks + 1);
          setSelected('html');
          alert('HTML CLICKED!');
        }}
        style={{
          width: '100%',
          padding: '30px',
          marginBottom: '20px',
          background: selected === 'html' ? '#0047AB' : '#1E3A5F',
          border: selected === 'html' ? '4px solid #DAA520' : '2px solid #0047AB',
          borderRadius: '15px',
          color: 'white',
          fontSize: '24px',
          fontWeight: 'bold',
          cursor: 'pointer',
        }}
      >
        📄 HTML FILE {selected === 'html' && '← SELECTED'}
      </button>

      <button
        onClick={() => {
          setClicks(clicks + 1);
          setSelected('email');
          alert('EMAIL CLICKED!');
        }}
        style={{
          width: '100%',
          padding: '30px',
          marginBottom: '20px',
          background: selected === 'email' ? '#0047AB' : '#1E3A5F',
          border: selected === 'email' ? '4px solid #DAA520' : '2px solid #0047AB',
          borderRadius: '15px',
          color: 'white',
          fontSize: '24px',
          fontWeight: 'bold',
          cursor: 'pointer',
        }}
      >
        📧 EMAIL {selected === 'email' && '← SELECTED'}
      </button>

      <div style={{ background: '#1E3A5F', padding: '20px', borderRadius: '10px', marginTop: '40px' }}>
        <p style={{ color: '#10B981', fontSize: '16px', fontWeight: 'bold' }}>
          ✅ If you can click these buttons and see alerts, JavaScript is working!
        </p>
        <p style={{ color: '#8FA3C4', fontSize: '14px', marginTop: '10px' }}>
          If this page works but /business/register doesn't, there's a specific issue with that page.
        </p>
      </div>

      <a
        href="/business/register?company_name=Test&domain=ktravo.net"
        style={{
          display: 'block',
          marginTop: '30px',
          padding: '20px',
          background: '#DAA520',
          color: '#0A1628',
          textAlign: 'center',
          borderRadius: '10px',
          textDecoration: 'none',
          fontWeight: 'bold',
          fontSize: '18px',
        }}
      >
        → Go to Real Register Page
      </a>
    </div>
  );
}
