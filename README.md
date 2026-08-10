# German A1 Complete v4.0 Web/Mobile

1. Create a free Supabase project.
2. Open **SQL Editor** and run `supabase_schema.sql`.
3. In Supabase copy your Project URL and anon/publishable key.
4. Upload this package to GitHub.
5. Deploy in Streamlit Community Cloud with main file `app.py`.
6. In Streamlit **Settings → Secrets**, add:

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_KEY = "YOUR_ANON_OR_PUBLISHABLE_KEY"
```

Never commit your real `secrets.toml` to GitHub.

The app stores progress in three Supabase tables:
- `reading_progress`
- `vocab_srs`
- `user_stats`

RLS policies in `supabase_schema.sql` restrict each user to their own rows.

On phone, open the Streamlit URL in Chrome/Safari and use **Add to Home Screen** if desired.
