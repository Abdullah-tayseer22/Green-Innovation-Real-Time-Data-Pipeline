import React, { useEffect, useState } from 'react';
import { loginAccount, registerAccount } from '../services/api';

export default function AuthPage({ initialMode = 'login', onBackHome, onComplete }) {
  const [mode, setMode] = useState(initialMode);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const isLogin = mode === 'login';

  useEffect(() => { setMode(initialMode); setError(''); }, [initialMode]);

  const submit = async (event) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    if (!isLogin && data.get('password') !== data.get('confirmPassword')) { setError('Passwords do not match.'); return; }
    setSubmitting(true); setError('');
    try {
      const result = isLogin
        ? await loginAccount({ email: data.get('email'), password: data.get('password') })
        : await registerAccount({ fullName: data.get('name'), email: data.get('email'), password: data.get('password') });
      onComplete(result);
    } catch (requestError) { setError(requestError.message || 'Authentication could not be completed.'); }
    finally { setSubmitting(false); }
  };

  return <div className="auth-page">
    <button className="auth-back" type="button" onClick={onBackHome}>← Back to Home</button>
    <section className="auth-card">
      <div className="auth-brand"><img src="/green-innovation-logo.svg" alt="Green Innovation logo"/><span>Green Innovation</span></div>
      <div className="auth-tabs" role="tablist"><button className={isLogin ? 'is-active' : ''} type="button" onClick={() => { setMode('login'); setError(''); }}>Login</button><button className={!isLogin ? 'is-active' : ''} type="button" onClick={() => { setMode('register'); setError(''); }}>Create Account</button></div>
      <div className="auth-copy"><h1>{isLogin ? 'Welcome Back' : 'Create Your Account'}</h1><p>{isLogin ? 'Log in to access your agricultural dashboard, location analyses, and recommendations.' : 'Create an account to analyze agricultural locations and access your recommendations.'}</p></div>
      <form onSubmit={submit}>
        {!isLogin && <label>Full name<input name="name" type="text" required minLength="2" autoComplete="name" placeholder="Enter your full name"/></label>}
        <label>Email address<input name="email" type="email" required autoComplete="email" placeholder="you@example.com"/></label>
        <label>Password<div className="password-field"><input name="password" type={showPassword ? 'text' : 'password'} required minLength={isLogin ? 1 : 8} autoComplete={isLogin ? 'current-password' : 'new-password'} placeholder="Enter your password"/><button type="button" onClick={() => setShowPassword(v => !v)}>{showPassword ? 'Hide' : 'Show'}</button></div></label>
        {!isLogin && <label>Confirm password<input name="confirmPassword" type={showPassword ? 'text' : 'password'} required minLength="8" autoComplete="new-password" placeholder="Confirm your password"/></label>}
        {isLogin && <div className="auth-options"><label><input type="checkbox"/> Remember me</label></div>}
        {error && <p className="auth-error">{error}</p>}
        <button className="auth-submit" type="submit" disabled={submitting}>{submitting ? 'Please wait…' : isLogin ? 'Login' : 'Create Account'}</button>
      </form>
      <p className="auth-switch">{isLogin ? 'New to Green Innovation?' : 'Already have an account?'} <button type="button" onClick={() => setMode(isLogin ? 'register' : 'login')}>{isLogin ? 'Create Account' : 'Login'}</button></p>
    </section>
  </div>;
}
