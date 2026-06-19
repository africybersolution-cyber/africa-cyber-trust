/**
 * JWT Token Auto-Refresh Utility
 *
 * Automatically refreshes access tokens using httpOnly refresh token cookies.
 * Call setupTokenRefresh() after login to start the refresh cycle.
 */

const REFRESH_INTERVAL = 14 * 60 * 1000; // 14 minutes (token expires in 15 min)
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

let refreshTimer: NodeJS.Timeout | null = null;

/**
 * Refresh the access token using the refresh token cookie
 */
export async function refreshAccessToken(): Promise<string | null> {
  try {
    const response = await fetch(`${API_URL}/api/auth/refresh`, {
      method: 'POST',
      credentials: 'include', // Send cookies
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      console.error('Token refresh failed:', response.status);
      stopTokenRefresh();
      // Redirect to login
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
      return null;
    }

    const data = await response.json();
    return data.access_token;
  } catch (error) {
    console.error('Token refresh error:', error);
    stopTokenRefresh();
    return null;
  }
}

/**
 * Setup automatic token refresh
 * Call this after successful login/signup
 */
export function setupTokenRefresh(onTokenRefreshed: (token: string) => void) {
  // Clear any existing timer
  stopTokenRefresh();

  // Set up recurring refresh
  refreshTimer = setInterval(async () => {
    const newToken = await refreshAccessToken();
    if (newToken) {
      onTokenRefreshed(newToken);
      console.log('[Auth] Access token refreshed');
    }
  }, REFRESH_INTERVAL);

  console.log('[Auth] Token auto-refresh enabled (every 14 minutes)');
}

/**
 * Stop automatic token refresh
 * Call this on logout
 */
export function stopTokenRefresh() {
  if (refreshTimer) {
    clearInterval(refreshTimer);
    refreshTimer = null;
    console.log('[Auth] Token auto-refresh disabled');
  }
}

/**
 * Interceptor for API calls - automatically refresh on 401
 */
export async function fetchWithAuth(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const response = await fetch(url, {
    ...options,
    credentials: 'include', // Always send cookies
  });

  // If 401, try to refresh token once and retry
  if (response.status === 401) {
    console.log('[Auth] Got 401, attempting token refresh...');
    const newToken = await refreshAccessToken();

    if (newToken) {
      // Retry the request with new token
      const retryResponse = await fetch(url, {
        ...options,
        credentials: 'include',
        headers: {
          ...options.headers,
          Authorization: `Bearer ${newToken}`,
        },
      });
      return retryResponse;
    }
  }

  return response;
}
