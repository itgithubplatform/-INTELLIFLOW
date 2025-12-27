/**
 * Rate Limit Middleware
 * =====================
 *
 * Rate limiting using express-rate-limit.
 */

import rateLimit from 'express-rate-limit';
import { config } from '../config';

export const rateLimitMiddleware = rateLimit({
    windowMs: 60 * 1000, // 1 minute
    max: config.rateLimitPerMinute,
    message: {
        error: {
            code: 'RATE_LIMIT_EXCEEDED',
            message: 'Too many requests, please try again later',
        },
    },
    standardHeaders: true,
    legacyHeaders: false,
    keyGenerator: (req) => {
        // Use user ID if authenticated, otherwise IP
        return (req as any).user?.id || req.ip || 'anonymous';
    },
});
