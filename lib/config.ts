/**
 * Application configuration
 * Use this instead of process.env to ensure values are available at runtime
 */

export const config = {
  // Backend API URL - fallback to localhost if env var not set
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002',

  // For debugging
  get isProduction() {
    return process.env.NODE_ENV === 'production';
  },

  // Log config on load (only in development)
  init() {
    if (!this.isProduction) {
      console.log('🔧 Config loaded:', {
        apiUrl: this.apiUrl,
        env: process.env.NODE_ENV,
        envVar: process.env.NEXT_PUBLIC_API_URL
      });
    }
  }
};

// Auto-init
config.init();
