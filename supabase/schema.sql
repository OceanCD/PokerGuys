-- Supabase Database Schema for PokerGuys
-- Run this in Supabase SQL Editor

-- Users table (minimal - just for community membership)
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Communities table
CREATE TABLE communities (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  code TEXT UNIQUE NOT NULL,  -- 6-character join code
  owner_id UUID REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Community members
CREATE TABLE community_members (
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  community_id UUID REFERENCES communities(id) ON DELETE CASCADE,
  role TEXT DEFAULT 'member',  -- 'owner', 'admin', 'member'
  joined_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (user_id, community_id)
);

-- Sessions
CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  community_id UUID REFERENCES communities(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  players JSONB NOT NULL,  -- Array of {name, buyIn, stack}
  total_up REAL DEFAULT 0,
  total_down REAL DEFAULT 0,
  net REAL DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  created_by UUID REFERENCES users(id)
);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE communities ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;

-- Policies

-- Users: anyone can create, but only see their own
CREATE POLICY "Users can read own profile" ON users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON users
  FOR INSERT WITH CHECK (auth.uid() = id);

-- Communities: visible to members
CREATE POLICY "Community members can read" ON communities
  FOR SELECT USING (
    id IN (SELECT community_id FROM community_members WHERE user_id = auth.uid())
  );

CREATE POLICY "Owners can insert communities" ON communities
  FOR INSERT WITH CHECK (owner_id = auth.uid());

-- Sessions: visible to community members
CREATE POLICY "Members can read sessions" ON sessions
  FOR SELECT USING (
    community_id IN (SELECT community_id FROM community_members WHERE user_id = auth.uid())
  );

CREATE POLICY "Members can insert sessions" ON sessions
  FOR INSERT WITH CHECK (
    community_id IN (SELECT community_id FROM community_members WHERE user_id = auth.uid())
  );

-- Function to join community by code
CREATE OR REPLACE FUNCTION join_community(user_id UUID, join_code TEXT)
RETURNS BOOLEAN AS $$
DECLARE
  comm_id UUID;
BEGIN
  SELECT id INTO comm_id FROM communities WHERE code = join_code;
  IF comm_id IS NULL THEN
    RETURN FALSE;
  END IF;
  
  INSERT INTO community_members (user_id, community_id, role)
  VALUES (user_id, comm_id, 'member')
  ON CONFLICT DO NOTHING;
  
  RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to create community with auto-generated code
CREATE OR REPLACE FUNCTION create_community(user_id UUID, name TEXT)
RETURNS UUID AS $$
DECLARE
  comm_id UUID;
  new_code TEXT;
BEGIN
  -- Generate 6-char alphanumeric code
  new_code := upper(substring(md5(random()::text) from 1 for 6));
  
  INSERT INTO communities (name, code, owner_id)
  VALUES (name, new_code, user_id)
  RETURNING id INTO comm_id;
  
  -- Add owner as member
  INSERT INTO community_members (user_id, community_id, role)
  VALUES (user_id, comm_id, 'owner')
  ON CONFLICT DO NOTHING;
  
  RETURN comm_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
