// src/supabaseClient.js
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://supabase.com/dashboard/project/aqokcjsmajnpfkladubp'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxb2tjanNtYWpucGZrbGFkdWJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEzOTg4OTUsImV4cCI6MjA2Njk3NDg5NX0.f2Z4aRkTlUExrpir4fqIpn0TkzpS5B0WPuAHAb26YFM'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
