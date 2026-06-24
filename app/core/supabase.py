from supabase import create_client

SUPABASE_URL = "https://awgizlwdpntjryjqksdk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF3Z2l6bHdkcG50anJ5anFrc2RrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MjMwNjM0MiwiZXhwIjoyMDk3ODgyMzQyfQ.fYki6gBVkIT8AcL8XJ9rM2f9oTSwyhYLwF_BqyU3oLw"

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)