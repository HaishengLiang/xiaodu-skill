const BAIDU_AUTH_URL = 'https://openapi.baidu.com/oauth/2.0/authorize';
const BAIDU_TOKEN_URL = 'https://openapi.baidu.com/oauth/2.0/token';

module.exports = async (req, res) => {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }

  const url = req.url;

  if (url === '/api/auth-url' && req.method === 'GET') {
    const appKey = process.env.XIAODU_APP_KEY;
    if (!appKey) {
      return res.status(500).json({ error: 'APP_KEY not configured' });
    }
    const deviceId = 'device_' + Math.random().toString(36).substring(2, 15);
    const authUrl = `${BAIDU_AUTH_URL}?response_type=code&client_id=${appKey}&redirect_uri=oob&scope=basic,dueros&device_id=${deviceId}`;
    return res.json({ auth_url: authUrl });
  }

  if (url === '/api/exchange' && req.method === 'POST') {
    const { code } = req.body || {};
    if (!code) {
      return res.status(400).json({ error: 'Authorization code required' });
    }
    const secretKey = process.env.XIAODU_SECRET_KEY;
    const appKey = process.env.XIAODU_APP_KEY;
    if (!secretKey || !appKey) {
      return res.status(500).json({ error: 'OAuth credentials not configured' });
    }
    try {
      const exchangeUrl = `${BAIDU_TOKEN_URL}?grant_type=authorization_code&code=${code}&client_id=${appKey}&client_secret=${secretKey}&redirect_uri=oob`;
      const resp = await fetch(exchangeUrl, { method: 'POST' });
      const data = await resp.json();
      if (data.error) {
        return res.status(400).json({ success: false, error: data.error, error_description: data.error_description });
      }
      return res.json({ success: true, access_token: data.access_token, refresh_token: data.refresh_token, expires_in: data.expires_in });
    } catch (e) {
      return res.status(500).json({ success: false, error: String(e) });
    }
  }

  if (url === '/api/refresh' && req.method === 'POST') {
    const { refresh_token } = req.body || {};
    if (!refresh_token) {
      return res.status(400).json({ error: 'refresh_token required' });
    }
    const secretKey = process.env.XIAODU_SECRET_KEY;
    const appKey = process.env.XIAODU_APP_KEY;
    if (!secretKey || !appKey) {
      return res.status(500).json({ error: 'OAuth credentials not configured' });
    }
    try {
      const refreshUrl = `${BAIDU_TOKEN_URL}?grant_type=refresh_token&refresh_token=${refresh_token}&client_id=${appKey}&client_secret=${secretKey}`;
      const resp = await fetch(refreshUrl, { method: 'POST' });
      const data = await resp.json();
      if (data.error) {
        return res.status(400).json({ success: false, error: data.error, error_description: data.error_description });
      }
      return res.json({ success: true, access_token: data.access_token, refresh_token: data.refresh_token, expires_in: data.expires_in });
    } catch (e) {
      return res.status(500).json({ success: false, error: String(e) });
    }
  }

  return res.status(404).json({ error: 'Not Found' });
};