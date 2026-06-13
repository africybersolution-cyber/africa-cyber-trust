/**
 * Comprehensive Security Issues Guide
 * Detailed explanations and fix instructions for common security issues
 */

export interface SecurityIssueGuide {
  title: string;
  description: string;
  risk: string;
  impact: string[];
  fixInstructions: {
    title: string;
    steps: string[];
    code?: string;
  }[];
  references: string[];
}

export const SECURITY_ISSUES_GUIDE: Record<string, SecurityIssueGuide> = {
  'strict-transport-security': {
    title: 'Missing HSTS (HTTP Strict Transport Security) Header',
    description: 'HSTS is a security header that forces browsers to only communicate with your website over HTTPS, preventing protocol downgrade attacks and cookie hijacking.',
    risk: 'Without HSTS, attackers can intercept the first HTTP request and redirect users to a malicious site or steal sensitive data.',
    impact: [
      'Man-in-the-middle (MITM) attacks possible',
      'SSL stripping attacks can downgrade connections',
      'Session cookies can be intercepted'
    ],
    fixInstructions: [
      {
        title: 'Apache (.htaccess)',
        steps: [
          'Open your .htaccess file',
          'Add the following header directive',
          'Save and test your site'
        ],
        code: `Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"`
      },
      {
        title: 'Nginx',
        steps: [
          'Open your nginx configuration file',
          'Add the header inside your server block',
          'Reload nginx: sudo nginx -s reload'
        ],
        code: `add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;`
      },
      {
        title: 'Node.js / Express',
        steps: [
          'Install helmet: npm install helmet',
          'Add to your app configuration'
        ],
        code: `const helmet = require('helmet');
app.use(helmet.hsts({
  maxAge: 31536000,
  includeSubDomains: true,
  preload: true
}));`
      }
    ],
    references: [
      'https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security',
      'https://owasp.org/www-project-secure-headers/'
    ]
  },

  'x-frame-options': {
    title: 'Missing X-Frame-Options Header',
    description: 'This header prevents your website from being embedded in an iframe, protecting against clickjacking attacks where attackers trick users into clicking invisible elements.',
    risk: 'Attackers can embed your site in a malicious page and trick users into performing unintended actions.',
    impact: [
      'Clickjacking attacks possible',
      'Users can be tricked into revealing sensitive information',
      'Unauthorized actions can be performed on behalf of users'
    ],
    fixInstructions: [
      {
        title: 'Apache (.htaccess)',
        steps: [
          'Add to your .htaccess file',
          'Choose DENY (no iframes) or SAMEORIGIN (only your site)'
        ],
        code: `Header always set X-Frame-Options "DENY"
# OR
Header always set X-Frame-Options "SAMEORIGIN"`
      },
      {
        title: 'Nginx',
        steps: [
          'Add to your nginx server block'
        ],
        code: `add_header X-Frame-Options "DENY" always;
# OR
add_header X-Frame-Options "SAMEORIGIN" always;`
      },
      {
        title: 'Node.js / Express',
        steps: [
          'Using helmet middleware'
        ],
        code: `app.use(helmet.frameguard({ action: 'deny' }));
// OR
app.use(helmet.frameguard({ action: 'sameorigin' }));`
      }
    ],
    references: [
      'https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options',
      'https://owasp.org/www-community/attacks/Clickjacking'
    ]
  },

  'x-content-type-options': {
    title: 'Missing X-Content-Type-Options Header',
    description: 'This header prevents browsers from MIME-sniffing a response away from the declared content-type, reducing exposure to drive-by download attacks.',
    risk: 'Browsers might interpret files as a different MIME type than intended, potentially executing malicious code.',
    impact: [
      'MIME confusion attacks possible',
      'Malicious files can be executed as scripts',
      'Cross-site scripting (XSS) vulnerabilities'
    ],
    fixInstructions: [
      {
        title: 'Apache (.htaccess)',
        steps: [
          'Add this single line to your .htaccess'
        ],
        code: `Header always set X-Content-Type-Options "nosniff"`
      },
      {
        title: 'Nginx',
        steps: [
          'Add to your server configuration'
        ],
        code: `add_header X-Content-Type-Options "nosniff" always;`
      },
      {
        title: 'Node.js / Express',
        steps: [
          'Using helmet (includes this by default)'
        ],
        code: `app.use(helmet.noSniff());`
      }
    ],
    references: [
      'https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options'
    ]
  },

  'content-security-policy': {
    title: 'Missing Content Security Policy (CSP)',
    description: 'CSP is a powerful security header that helps detect and mitigate certain types of attacks including Cross-Site Scripting (XSS) and data injection attacks.',
    risk: 'Without CSP, your site is more vulnerable to XSS attacks, clickjacking, and other code injection attacks.',
    impact: [
      'Cross-site scripting (XSS) attacks easier',
      'Data injection attacks possible',
      'Unauthorized scripts can execute',
      'User data can be stolen'
    ],
    fixInstructions: [
      {
        title: 'Basic CSP (Apache)',
        steps: [
          'Start with a basic policy',
          'Gradually refine based on your needs'
        ],
        code: `Header always set Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;"`
      },
      {
        title: 'Basic CSP (Nginx)',
        steps: [
          'Add to nginx configuration'
        ],
        code: `add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data: https:;" always;`
      },
      {
        title: 'Node.js / Express (Strict)',
        steps: [
          'Use helmet with custom CSP configuration'
        ],
        code: `app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'"],
    styleSrc: ["'self'", "'unsafe-inline'"],
    imgSrc: ["'self'", "data:", "https:"],
    connectSrc: ["'self'"],
    fontSrc: ["'self'"],
    objectSrc: ["'none'"],
    upgradeInsecureRequests: []
  }
}));`
      }
    ],
    references: [
      'https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP',
      'https://content-security-policy.com/'
    ]
  },

  'x-xss-protection': {
    title: 'Missing X-XSS-Protection Header',
    description: 'This header enables the Cross-Site Scripting (XSS) filter built into most modern web browsers.',
    risk: 'Without this header, browsers may not activate their built-in XSS protection.',
    impact: [
      'XSS attacks may not be blocked by browser',
      'User data exposure risk',
      'Session hijacking possible'
    ],
    fixInstructions: [
      {
        title: 'Apache (.htaccess)',
        steps: [
          'Add this header to enable XSS protection'
        ],
        code: `Header always set X-XSS-Protection "1; mode=block"`
      },
      {
        title: 'Nginx',
        steps: [
          'Add to your nginx configuration'
        ],
        code: `add_header X-XSS-Protection "1; mode=block" always;`
      },
      {
        title: 'Node.js / Express',
        steps: [
          'Using helmet middleware'
        ],
        code: `app.use(helmet.xssFilter());`
      }
    ],
    references: [
      'https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-XSS-Protection'
    ]
  },

  'permissions-policy': {
    title: 'Missing Permissions Policy Header',
    description: 'Permissions Policy (formerly Feature-Policy) allows you to control which features and APIs can be used in the browser.',
    risk: 'Without this header, malicious third-party scripts could access sensitive browser features like camera, microphone, or geolocation.',
    impact: [
      'Unauthorized access to browser features',
      'Privacy risks (camera, microphone access)',
      'Location tracking without consent'
    ],
    fixInstructions: [
      {
        title: 'Apache (.htaccess)',
        steps: [
          'Add this header to restrict feature access'
        ],
        code: `Header always set Permissions-Policy "geolocation=(), microphone=(), camera=()"`
      },
      {
        title: 'Nginx',
        steps: [
          'Add to nginx configuration'
        ],
        code: `add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;`
      },
      {
        title: 'Node.js / Express',
        steps: [
          'Add custom header middleware'
        ],
        code: `app.use((req, res, next) => {
  res.setHeader('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');
  next();
});`
      }
    ],
    references: [
      'https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Feature-Policy'
    ]
  }
};

/**
 * Get detailed guide for a security issue
 */
export function getSecurityIssueGuide(issueKey: string): SecurityIssueGuide | null {
  // Normalize the key (remove spaces, lowercase)
  const normalizedKey = issueKey.toLowerCase().replace(/\s+/g, '-');

  // Try direct match first
  if (SECURITY_ISSUES_GUIDE[normalizedKey]) {
    return SECURITY_ISSUES_GUIDE[normalizedKey];
  }

  // Try fuzzy match
  for (const [key, guide] of Object.entries(SECURITY_ISSUES_GUIDE)) {
    if (normalizedKey.includes(key) || key.includes(normalizedKey)) {
      return guide;
    }
  }

  return null;
}

/**
 * Parse security header issues from error message
 */
export function parseSecurityHeaders(message: string): string[] {
  const headers: string[] = [];
  const lowerMessage = message.toLowerCase();

  if (lowerMessage.includes('strict-transport-security') || lowerMessage.includes('hsts')) {
    headers.push('strict-transport-security');
  }
  if (lowerMessage.includes('x-frame-options')) {
    headers.push('x-frame-options');
  }
  if (lowerMessage.includes('x-content-type-options')) {
    headers.push('x-content-type-options');
  }
  if (lowerMessage.includes('content-security-policy') || lowerMessage.includes('csp')) {
    headers.push('content-security-policy');
  }
  if (lowerMessage.includes('x-xss-protection')) {
    headers.push('x-xss-protection');
  }
  if (lowerMessage.includes('permissions-policy') || lowerMessage.includes('feature-policy')) {
    headers.push('permissions-policy');
  }

  return headers;
}
