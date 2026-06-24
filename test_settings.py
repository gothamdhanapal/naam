from app.core.config import settings

print("URL Loaded:", settings.SUPABASE_URL)
print("Key Exists:", bool(settings.SUPABASE_KEY))
print("API Key Exists:", bool(settings.OPENAI_API_KEY))