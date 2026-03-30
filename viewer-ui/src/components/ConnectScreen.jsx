import { useState, useCallback } from 'react';

const LOGO_URL =
  'https://www.tulavekino.sk/wp-content/uploads/2026/02/Logo-EN-Cinema-Wandering-COLOR.svg';

export default function ConnectScreen({ status, error, onConnect }) {
  const [sessionId, setSessionId] = useState('');
  const [password, setPassword] = useState('');

  const isConnecting = status === 'connecting';

  const handleSubmit = useCallback(
    (e) => {
      e.preventDefault();
      if (!sessionId.trim() || !password.trim()) return;
      onConnect(sessionId.trim(), password.trim());
    },
    [sessionId, password, onConnect]
  );

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface px-4">
      <div className="w-full max-w-md bg-white rounded-card shadow-lg p-8">
        {/* Logo */}
        <div className="flex justify-center mb-6">
          <img src={LOGO_URL} alt="Wandering Cinema" className="h-12" />
        </div>

        {/* Title */}
        <h1 className="text-2xl font-bold text-center text-tk-black mb-8">
          Wander Remote
        </h1>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Session ID */}
          <div>
            <label
              htmlFor="sessionId"
              className="block text-sm font-medium text-tk-black-80 mb-1.5"
            >
              ID relacie
            </label>
            <input
              id="sessionId"
              type="text"
              inputMode="numeric"
              maxLength={6}
              placeholder="000000"
              value={sessionId}
              onChange={(e) => {
                const v = e.target.value.replace(/\D/g, '').slice(0, 6);
                setSessionId(v);
              }}
              disabled={isConnecting}
              className="w-full px-4 py-2.5 rounded-input border border-tk-border bg-white text-tk-black font-mono text-center text-lg tracking-widest placeholder:text-tk-black-40 focus:outline-none focus:ring-2 focus:ring-primary-ring focus:border-primary disabled:opacity-50"
            />
          </div>

          {/* Password */}
          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-tk-black-80 mb-1.5"
            >
              Heslo
            </label>
            <input
              id="password"
              type="password"
              maxLength={6}
              placeholder="******"
              value={password}
              onChange={(e) => setPassword(e.target.value.slice(0, 6))}
              disabled={isConnecting}
              className="w-full px-4 py-2.5 rounded-input border border-tk-border bg-white text-tk-black font-mono text-center text-lg tracking-widest placeholder:text-tk-black-40 focus:outline-none focus:ring-2 focus:ring-primary-ring focus:border-primary disabled:opacity-50"
            />
          </div>

          {/* Status / Error */}
          {(error || isConnecting) && (
            <div
              className={`text-sm text-center px-3 py-2 rounded-input ${
                error
                  ? 'bg-primary-light text-primary'
                  : 'bg-surface text-tk-black-60'
              }`}
            >
              {error || 'Pripajanie...'}
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={
              isConnecting || sessionId.length < 6 || password.length < 1
            }
            className="w-full py-3 rounded-btn bg-primary text-white font-semibold text-base hover:bg-primary-hover transition-colors focus:outline-none focus:ring-2 focus:ring-primary-ring focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isConnecting ? (
              <span className="flex items-center justify-center gap-2">
                <svg
                  className="animate-spin h-5 w-5"
                  viewBox="0 0 24 24"
                  fill="none"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  />
                </svg>
                Pripajanie...
              </span>
            ) : (
              'Pripojit sa'
            )}
          </button>
        </form>

        {/* Footer */}
        <p className="mt-8 text-center text-xs text-tk-black-40">
          Powered by Tulave kino
        </p>
      </div>
    </div>
  );
}
