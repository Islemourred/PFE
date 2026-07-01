import { createClient } from "@supabase/supabase-js";

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || "https://erwwmxppovtuzikyfakf.supabase.co";
const SUPABASE_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVyd3dteHBwb3Z0dXppa3lmYWtmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE2MjY2MjUsImV4cCI6MjA5NzIwMjYyNX0.D4cW01s4uAPUUi7c5sWCgFmykQD4JMWEwhQy9uSLeJM";

export const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);
