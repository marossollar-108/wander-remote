import { useState, useCallback } from 'react';

const LOGO_URL = '/logo.png';

export default function ConnectScreen({ status, error, onConnect }) {
  const [sessionId, setSessionId] = useState('');
  const [password, setPassword] = useState('');
  const [showDownloads, setShowDownloads] = useState(false);

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
    <div className="min-h-[100dvh] flex items-center justify-center bg-surface px-4 py-6">
      <div className="w-full max-w-md bg-white rounded-card shadow-lg p-6 sm:p-8">
        {/* Logo */}
        <div className="flex justify-center mb-4 sm:mb-6">
          <img src={LOGO_URL} alt="Wander Remote" className="h-20 sm:h-36" />
        </div>

        {/* Title */}
        <h1 className="text-xl sm:text-2xl font-bold text-center text-tk-black mb-6 sm:mb-8">
          Wander Remote
        </h1>

        <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-5">
          {/* Session ID */}
          <div>
            <label
              htmlFor="sessionId"
              className="block text-sm font-medium text-tk-black-80 mb-1.5"
            >
              Host ID
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
              autoComplete="off"
              className="w-full px-4 py-3 rounded-input border border-tk-border bg-white text-tk-black font-mono text-center text-lg tracking-widest placeholder:text-tk-black-40 focus:outline-none focus:ring-2 focus:ring-primary-ring focus:border-primary disabled:opacity-50"
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
              autoComplete="off"
              className="w-full px-4 py-3 rounded-input border border-tk-border bg-white text-tk-black font-mono text-center text-lg tracking-widest placeholder:text-tk-black-40 focus:outline-none focus:ring-2 focus:ring-primary-ring focus:border-primary disabled:opacity-50"
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
            className="w-full py-3.5 rounded-btn bg-primary text-white font-semibold text-base hover:bg-primary-hover active:scale-[0.98] transition-all focus:outline-none focus:ring-2 focus:ring-primary-ring focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
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

        {/* Download section — collapsible on mobile */}
        <div className="mt-6 sm:mt-8 pt-5 sm:pt-6 border-t border-tk-border">
          <button
            type="button"
            onClick={() => setShowDownloads(!showDownloads)}
            className="sm:hidden w-full flex items-center justify-between text-sm font-medium text-tk-black-80 mb-3"
          >
            <span>Stiahnite si Host aplikaciu</span>
            <svg
              className={`w-4 h-4 text-tk-black-40 transition-transform ${showDownloads ? 'rotate-180' : ''}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          <p className="hidden sm:block text-sm font-medium text-tk-black-80 text-center mb-3">
            Stiahnite si Host aplikaciu
          </p>

          <div className={`space-y-2 ${showDownloads ? 'block' : 'hidden'} sm:block`}>
            <a
              href="https://github.com/marossollar-108/wander-remote/releases/latest/download/Wander.Remote.Host-1.0.0-arm64.dmg"
              className="flex items-center justify-between w-full px-4 py-3 sm:py-2.5 rounded-input border border-tk-border hover:bg-surface active:bg-tk-black-20 transition-colors text-sm"
            >
              <span className="text-tk-black">macOS (Apple Silicon)</span>
              <span className="text-tk-black-40 text-xs">.dmg — M1/M2/M3/M4</span>
            </a>
            <a
              href="https://github.com/marossollar-108/wander-remote/releases/latest/download/Wander.Remote.Host-1.0.0.dmg"
              className="flex items-center justify-between w-full px-4 py-3 sm:py-2.5 rounded-input border border-tk-border hover:bg-surface active:bg-tk-black-20 transition-colors text-sm"
            >
              <span className="text-tk-black">macOS (Intel)</span>
              <span className="text-tk-black-40 text-xs">.dmg — Intel Mac</span>
            </a>
            <a
              href="https://github.com/marossollar-108/wander-remote/releases/latest/download/Wander.Remote.Host.Setup.1.0.0.exe"
              className="flex items-center justify-between w-full px-4 py-3 sm:py-2.5 rounded-input border border-tk-border hover:bg-surface active:bg-tk-black-20 transition-colors text-sm"
            >
              <span className="text-tk-black">Windows</span>
              <span className="text-tk-black-40 text-xs">.exe — Windows 10+</span>
            </a>
          </div>
        </div>

        {/* Footer */}
        <p className="mt-5 sm:mt-6 text-center text-xs text-tk-black-40">
          Powered by Tulave kino
        </p>
      </div>
    </div>
  );
}
