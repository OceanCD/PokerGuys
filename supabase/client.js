// PokerGuys - Supabase Client Configuration
// Replace with your Supabase credentials

const SUPABASE_URL = 'YOUR_SUPABASE_URL';
const SUPABASE_ANON_KEY = 'YOUR_SUPABASE_ANON_KEY';

// Initialize Supabase client
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Auth helpers - using community code as simple "auth"
// No email needed - just enter name + community code

async function loginOrCreateUser(name, communityCode) {
  // Try to find existing community
  const { data: community } = await supabase
    .from('communities')
    .select('*')
    .eq('code', communityCode.toUpperCase())
    .single();
  
  let userId;
  let isNewUser = false;
  
  if (community) {
    // Community exists - check if user is member, if not add them
    const { data: existingMember } = await supabase
      .from('community_members')
      .select('*')
      .eq('community_id', community.id)
      .eq('user_name', name)
      .single();
    
    if (!existingMember) {
      // Add as member (store name instead of user_id for simplicity)
      await supabase
        .from('community_members')
        .insert({ community_id: community.id, user_name: name, role: 'member' });
    }
    
    userId = community.id; // Use community as the "session" key
    isNewUser = false;
  } else {
    // Create new community with this code
    const { data: newCommunity, error } = await supabase
      .from('communities')
      .insert({ 
        name: name + "'s Community", 
        code: communityCode.toUpperCase(),
        owner_name: name
      })
      .select()
      .single();
    
    if (error) throw error;
    
    // Add creator as owner
    await supabase
      .from('community_members')
      .insert({ community_id: newCommunity.id, user_name: name, role: 'owner' });
    
    userId = newCommunity.id;
    isNewUser = true;
  }
  
  return { userId, communityCode: communityCode.toUpperCase(), userName: name, isNewUser };
}

async function loadCommunitySessions(communityId) {
  const { data, error } = await supabase
    .from('sessions')
    .select('*')
    .eq('community_id', communityId)
    .order('date', { ascending: false });
  
  if (error) throw error;
  return data || [];
}

async function saveSessionToCloud(communityId, sessionData) {
  const { data, error } = await supabase
    .from('sessions')
    .insert({
      community_id: communityId,
      date: sessionData.date,
      players: sessionData.players,
      total_up: sessionData.totalUp,
      total_down: sessionData.totalDown,
      net: sessionData.net
    })
    .select()
    .single();
  
  if (error) throw error;
  return data;
}

async function deleteSessionFromCloud(communityId, sessionId) {
  const { error } = await supabase
    .from('sessions')
    .delete()
    .eq('id', sessionId)
    .eq('community_id', communityId);
  
  if (error) throw error;
}

async function updateSessionInCloud(communityId, sessionId, sessionData) {
  const { error } = await supabase
    .from('sessions')
    .update({
      date: sessionData.date,
      players: sessionData.players,
      total_up: sessionData.totalUp,
      total_down: sessionData.totalDown,
      net: sessionData.net
    })
    .eq('id', sessionId)
    .eq('community_id', communityId);
  
  if (error) throw error;
}
