// api/submit.js — Vercel Serverless Function
// Saves interview transcript to Neon DB via pg (standard postgres client)

const { Client } = require('pg');

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { interview_id, messages } = req.body || {};
  if (!interview_id || !messages) {
    return res.status(400).json({ error: 'Missing interview_id or messages' });
  }

  const client = new Client({ connectionString: process.env.DATABASE_URL, ssl: { rejectUnauthorized: false } });

  try {
    await client.connect();
    const transcript = JSON.stringify(messages);

    await client.query(
      `INSERT INTO interview_feedback (interview_id, transcript, total_score)
       VALUES ($1, $2::jsonb, 0)
       ON CONFLICT (interview_id)
       DO UPDATE SET transcript = $2::jsonb, total_score = 0`,
      [interview_id, transcript]
    );

    await client.query(
      `UPDATE mock_interviews SET status = 'transcript_ready' WHERE id = $1`,
      [interview_id]
    );

    await client.end();
    return res.status(200).json({ success: true });
  } catch (err) {
    console.error('DB error:', err.message);
    try { await client.end(); } catch (_) {}
    return res.status(500).json({ error: err.message });
  }
};
