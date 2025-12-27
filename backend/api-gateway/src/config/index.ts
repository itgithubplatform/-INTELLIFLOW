/**
 * Configuration
 * =============
 *
 * Environment-based configuration for the API Gateway.
 */

export const config = {
    // Server
    port: parseInt(process.env.PORT || '3000', 10),
    nodeEnv: process.env.NODE_ENV || 'development',

    // CORS
    corsOrigins: (process.env.CORS_ORIGINS || 'http://localhost:3000,http://localhost:3001').split(','),

    // Agent URLs
    agentAUrl: process.env.AGENT_A_URL || 'http://localhost:8001',
    agentBUrl: process.env.AGENT_B_URL || 'http://localhost:8002',

    // Descope
    descopeProjectId: process.env.DESCOPE_PROJECT_ID || '',

    // Rate limiting
    rateLimitPerMinute: parseInt(process.env.RATE_LIMIT_PER_MINUTE || '100', 10),

    // Logging
    logLevel: process.env.LOG_LEVEL || 'info',
};

// Validate required config
if (!config.descopeProjectId && config.nodeEnv === 'production') {
    console.error('ERROR: DESCOPE_PROJECT_ID is required in production');
    process.exit(1);
}
