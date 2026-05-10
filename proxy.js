/**
 * Vercel Serverless Function — API 代理
 * 将前端请求转发到 vivo 蓝心大模型 API，解决浏览器 CORS 限制
 */
export default async function handler(req, res) {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const resp = await fetch('https://api-ai.vivo.com.cn/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer sk-xuanji-2026631636-d3dsS3V6dEt6bmpWQ1JzUA=='
      },
      body: JSON.stringify(req.body)
    });

    const data = await resp.json();
    return res.status(resp.status).json(data);
  } catch (err) {
    return res.status(502).json({ error: 'Proxy error: ' + err.message });
  }
}
