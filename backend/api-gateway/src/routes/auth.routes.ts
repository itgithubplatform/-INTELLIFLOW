/**
 * Auth Routes
 * ===========
 *
 * Authentication routes using Descope.
 */

import { Router, Request, Response } from 'express';
import { descopeService } from '../services/descope.service';
import { logger } from '../utils/logger';

const router = Router();

/**
 * POST /api/auth/validate
 * Validate a session token
 */
router.post('/validate', async (req: Request, res: Response) => {
    try {
        const authHeader = req.headers.authorization;

        if (!authHeader?.startsWith('Bearer ')) {
            return res.status(401).json({
                error: {
                    code: 'MISSING_TOKEN',
                    message: 'Authorization header with Bearer token required',
                },
            });
        }

        const token = authHeader.substring(7);
        const claims = await descopeService.validateToken(token);

        res.json({
            valid: true,
            claims: {
                sub: claims.sub,
                email: claims.email,
                scopes: claims.scopes,
                exp: claims.exp,
            },
        });
    } catch (error: any) {
        logger.warn('Token validation failed', { error: error.message });
        res.status(401).json({
            error: {
                code: 'INVALID_TOKEN',
                message: error.message || 'Token validation failed',
            },
        });
    }
});

/**
 * GET /api/auth/me
 * Get current user information
 */
router.get('/me', async (req: Request, res: Response) => {
    try {
        const authHeader = req.headers.authorization;

        if (!authHeader?.startsWith('Bearer ')) {
            return res.status(401).json({
                error: {
                    code: 'MISSING_TOKEN',
                    message: 'Authorization required',
                },
            });
        }

        const token = authHeader.substring(7);
        const claims = await descopeService.validateToken(token);

        res.json({
            user: {
                id: claims.sub,
                email: claims.email,
                name: claims.name,
                scopes: claims.scopes,
            },
        });
    } catch (error: any) {
        res.status(401).json({
            error: {
                code: 'UNAUTHORIZED',
                message: 'Invalid or expired session',
            },
        });
    }
});

/**
 * POST /api/auth/refresh
 * Refresh a session token
 */
router.post('/refresh', async (req: Request, res: Response) => {
    try {
        const { refreshToken } = req.body;

        if (!refreshToken) {
            return res.status(400).json({
                error: {
                    code: 'MISSING_REFRESH_TOKEN',
                    message: 'Refresh token required',
                },
            });
        }

        // Refresh token logic would go here
        // For now, return a placeholder
        res.json({
            message: 'Token refresh endpoint - implement with Descope SDK',
        });
    } catch (error: any) {
        res.status(401).json({
            error: {
                code: 'REFRESH_FAILED',
                message: 'Token refresh failed',
            },
        });
    }
});

export default router;
