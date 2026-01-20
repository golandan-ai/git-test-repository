// Vercel Serverless Function - Liaoshi Search API
// Endpoint: /api/search?q=horses or /api/search?all=true

export default async function handler(req, res) {
    // CORS headers for cross-origin requests
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET');
    res.setHeader('Content-Type', 'application/json');

    // Configuration
    const SUPABASE_URL = 'https://skbmyruppgthmfytofvf.supabase.co';
    const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNrYm15cnVwcGd0aG1meXRvZnZmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4MDc1MjMsImV4cCI6MjA4NDM4MzUyM30.nHpeBFlXBfLY3K2jbNN_UX5h9J3IbXk7BsFhxct4xo0';
    const TABLE_NAME = 'test01';

    try {
        const { q, all } = req.query;

        let url = `${SUPABASE_URL}/rest/v1/${TABLE_NAME}?select=*`;

        // Add search filter if query provided
        if (q && q.trim() !== '') {
            url += `&key_words=ilike.*${encodeURIComponent(q)}*`;
        } else if (all !== 'true') {
            // No query and not showing all - return help
            return res.status(200).json({
                success: true,
                message: 'Liaoshi Research Database API',
                usage: {
                    search: '/api/search?q=horses',
                    showAll: '/api/search?all=true',
                    examples: ['horses', 'tribute', 'capital', 'Abaoji', 'founding']
                },
                results: []
            });
        }

        // Fetch from Supabase REST API
        const response = await fetch(url, {
            headers: {
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`
            }
        });

        if (!response.ok) {
            throw new Error(`Supabase error: ${response.status}`);
        }

        const data = await response.json();

        // Format results for chatbot readability
        const formattedResults = data.map((row, index) => ({
            id: row.id,
            chinese: row.chinese_verse,
            translation: row.translated,
            chapter: row.chapter_n,
            keywords: row.key_words
        }));

        // Return JSON response
        return res.status(200).json({
            success: true,
            query: q || (all === 'true' ? 'ALL RECORDS' : null),
            count: formattedResults.length,
            results: formattedResults,
            // Plain text summary for chatbots
            summary: formattedResults.map((r, i) =>
                `[${i + 1}] Chapter ${r.chapter}: "${r.translation}" (Keywords: ${r.keywords})`
            ).join('\n')
        });

    } catch (error) {
        return res.status(500).json({
            success: false,
            error: error.message
        });
    }
}
