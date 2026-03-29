// api/submit.js — Vercel Serverless Function
// Receives interview transcript from GitHub Pages and saves to Neon DB
// Called by: interview.html on GitHub Pages after interview completes

const { neon } = require('@neondatabase/serverless');

export default async function handler(req, res) {
  // CORS — allow GitHub Pages origin
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { interview_id, messages } = req.body;

  if (!interview_id || !messages) {
    return res.status(400).json({ error: 'Missing interview_id or messages' });
  }

  try {
    const sql = neon(process.env.DATABASE_URL);

    // Save transcript to interview_feedback (score=0 = pending evaluation)
    await sql`
      INSERT INTO interview_feedback (interview_id, transcript, total_score)
      VALUES (${interview_id}, ${JSON.stringify(messages)}, 0)
      ON CONFLICT (interview_id)
      DO UPDATE SET transcript = ${JSON.stringify(messages)}, total_score = 0
    `;

    // Mark interview as transcript_ready so Streamlit knows to poll
    await sql`
      UPDATE mock_interviews
      SET status = 'transcript_ready'
      WHERE id = ${interview_id}
    `;

    return res.status(200).json({ success: true });

  } catch (err) {
    console.error('DB error:', err);
    return res.status(500).json({ error: err.message });
  }
}
