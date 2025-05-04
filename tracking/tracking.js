const channel = new BroadcastChannel('session-tracker');
const tabId = crypto.randomUUID ? crypto.randomUUID() : ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c => (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16));
const liveTabs = new Set([tabId]);

// Constants
const CSRF_COOKIE_NAME = "_my_csrf_token";
const SESSION_COOKIE_NAME = "_my_session_id";

// Helper function to get cookie value by name
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

// Helper function for sending POST requests
async function sendRequest(endpoint, httpMethod='POST', data = {}) {
  try {
    // Get CSRF token from cookie before each request
    const csrfToken = getCookie(CSRF_COOKIE_NAME);

    const response = await fetch(endpoint, {
      method: httpMethod,
      credentials: 'same-origin', // Include cookies
      headers: {
        'Content-Type': 'application/json',
        ...(csrfToken && { 'X-CSRF-Token': csrfToken })
      },
      ...(Object.keys(data).length > 0 && { body: JSON.stringify(data) })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    // If status is 204 No Content, return empty object
    if (response.status === 204) {
      return {};
    }

    return await response.json();
  } catch (error) {
    console.error(`Failed to send request to ${endpoint}:`, error);
    return null;
  }
}

// Function to delete session cookies
function deleteSessionCookies() {
  document.cookie = `${SESSION_COOKIE_NAME}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; secure; samesite=lax`;
  document.cookie = `${CSRF_COOKIE_NAME}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; secure; samesite=lax`;
}

channel.onmessage = ({data}) => {
  console.log('Received message:', data);
  switch(data.type) {
    case 'who-is-there':
      // someone new wants the roster—tell them about _you_
      channel.postMessage({type:'iam-here', id:tabId});
      break;
    case 'iam-here':
      // a live tab announces itself
      liveTabs.add(data.id);
      break;
    case 'unregister':
      liveTabs.delete(data.id);
      if (liveTabs.size === 0) {
        stopSession();
      }
      break;
  }
};

// Start a new session
async function startSession() {
  try {
    await sendRequest('/_session/start', 'GET');
    console.log('Session started successfully');
  } catch (error) {
    console.error('Failed to start session:', error);
  }
}

// Send heartbeat
async function sendHeartbeat() {
  try {
    await sendRequest('/_session/heartbeat');
    console.log('Heartbeat sent');
  } catch (error) {
    console.error('Failed to send heartbeat:', error);
  }
}

// Stop the session
async function stopSession() {
  try {
    await sendRequest('/_session/stop');
    deleteSessionCookies();
    console.log('Session stopped successfully');
  } catch (error) {
    console.error('Failed to stop session:', error);
  }
}

// 1) on load: ask who's already open and start session
window.addEventListener('load', async () => {
  channel.postMessage({type:'who-is-there'});
  console.log('Tab is open, registering:', tabId);
  await startSession();
});

// 2) when _you_ close, tell everyone
window.addEventListener('beforeunload', (event) => {
  event.preventDefault();
  channel.postMessage({type:'unregister', id:tabId});
  console.log('Tab is closing, unregistering:', tabId);
  if (liveTabs.size === 1 && liveTabs.has(tabId)) {
    stopSession();
  }
});

// 3) send heartbeat every 1 minutes
const HEARTBEAT_INTERVAL = 1 * 60 * 1000; // 5 minutes in milliseconds
setInterval(() => {
  // Only send heartbeat if tab is visible
  if (document.visibilityState !== 'hidden') {
    sendHeartbeat();
  }
}, HEARTBEAT_INTERVAL);
