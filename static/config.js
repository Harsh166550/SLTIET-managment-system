(() => {
  // Determine backend URL based on environment and optional IP override
  const isNative = typeof Capacitor !== 'undefined' && Capacitor.isNative;
  const port = '5000';
  const urlParams = new URLSearchParams(window.location.search);
  const apiIp = urlParams.get('api_ip');

  // If an IP is provided via query parameter, use it and persist
  if (apiIp) {
    window.API_BASE_URL = `http://${apiIp}:${port}`;
    localStorage.setItem('API_BASE_URL', window.API_BASE_URL);
    return;
  }

  // Use stored value if present
  const stored = localStorage.getItem('API_BASE_URL');
  if (stored) {
    window.API_BASE_URL = stored;
    return;
  }

  // Native Android (Capacitor) emulator fallback IP
  if (isNative) {
    window.API_BASE_URL = 'http://51.20.250.141:5000';
    return;
  }

  // Default to current hostname or localhost
  const defaultHost = window.location.hostname || 'localhost';
  window.API_BASE_URL = `http://${defaultHost}:${port}`;
})();
