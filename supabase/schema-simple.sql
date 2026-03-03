-- Simple PokerGuys Schema (No Auth Required)
-- Just community code + name to join

-- Communities table
CREATE TABLE communities (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  code TEXT UNIQUE NOT NULL,  -- 6-character join code
  owner_name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Community members (who joined)
CREATE TABLE community_members (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  community_id UUID REFERENCES communities(id) ON DELETE CASCADE,
  user_name TEXT NOT NULL,
  role TEXT DEFAULT 'member',  -- 'owner', 'member'
  joined_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(community_id, user_name)
);

-- Sessions with player data
CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  community_id UUID REFERENCES communities(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  players JSONB NOT NULL,  -- Array of {name, buyIn, stack, hands}
  total_up REAL DEFAULT 0,
  total_down REAL DEFAULT 0,
  net REAL DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE communities ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;

-- Allow public read/write (community code acts as password)
CREATE POLICY "Anyone with code can read community" ON communities
  FOR SELECT USING (code IS NOT NULL);

CREATE POLICY "Anyone can create community" ON communities
  FOR INSERT WITH CHECK (true);

-- Members can read their community
CREATE POLICY "Members can read" ON community_members
  FOR SELECT USING (true);

CREATE POLICY "Anyone can join" ON community_members
  FOR INSERT WITH CHECK (true);

-- Community members can read/write sessions
CREATE POLICY "Members can read sessions" ON sessions
  FOR SELECT USING (true);

CREATE POLICY "Members can insert sessions" ON sessions
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Members can update sessions" ON sessions
  FOR UPDATE USING (true);

CREATE POLICY "Members can delete sessions" ON sessions
  FOR DELETE USING (true);
