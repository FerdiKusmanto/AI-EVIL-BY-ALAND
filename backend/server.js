const express = require('express');
const path = require('path');

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, '../frontend')));

const ALAND_AI = 'http://127.0.0.1:11435';

app.post('/api/chat', async (req, res) => {
  const { messages, model } = req.body;

  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  try {
    const response = await fetch(`${ALAND_AI}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model, messages, stream: true }),
    });

    if (!response.ok) {
      res.write(`data: ${JSON.stringify({ error: `aland-ai error: ${response.statusText}` })}\n\n`);
      return res.end();
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const lines = decoder.decode(value).split('\n').filter(Boolean);
      for (const line of lines) {
        try {
          const json = JSON.parse(line);
          const text = json.message?.content || '';
          if (text) res.write(`data: ${JSON.stringify({ text })}\n\n`);
          if (json.done) res.write('data: [DONE]\n\n');
          if (json.error) res.write(`data: ${JSON.stringify({ error: json.error })}\n\n`);
        } catch {}
      }
    }
  } catch {
    res.write(`data: ${JSON.stringify({ error: 'aland-ai tidak berjalan. Jalankan: aland-ai serve' })}\n\n`);
  }

  res.end();
});

app.get('/api/models', async (_req, res) => {
  try {
    const r = await fetch(`${ALAND_AI}/api/tags`);
    const data = await r.json();
    res.json((data.models || []).map(m => m.name));
  } catch {
    res.json([]);
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`ALand-Evil AI → http://localhost:${PORT}`));
