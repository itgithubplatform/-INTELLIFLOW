/**
 * Auth Middleware
 * ===============
 *
 * Middleware for validating authentication tokens.
 */

import { Request, Response, NextFunction } from 'express';
import { descopeService } from '../services/descope.service';
import { logger } from '../utils/logger';

// Paths that don't require authentication
const PUBLIC_PATHS = [
    '/',
    '/health',
    '/api/auth/validate',
    '/api/auth/refresh',
];

export interface AuthenticatedRequest extends Request {
    user?: {
        id: string;
        email?: string;
        scopes: string[];
    };
}

export const authMiddleware = async (
    req: AuthenticatedRequest,
    res: Response,
    next: NextFunction
): Promise<void> => {
    try {
        // Check if path is public
        if (PUBLIC_PATHS.includes(req.path)) {
            return next();
        }

        // Get auth header
        const authHeader = req.headers.authorization;

        if (!authHeader?.startsWith('Bearer ')) {
            res.status(401).json({
                error: {
                    code: 'MISSING_TOKEN',
                    message: 'Authorization header with Bearer token required',
                },
            });
            return;
        }

        // Extract token
        const token = authHeader.substring(7);

        // Validate token
        const claims = await descopeService.validateToken(token);

        // Attach user to request
        req.user = {
            id: claims.sub,
            email: claims.email,
            scopes: claims.scopes || [],
        };

        logger.debug('User authenticated', {
            userId: req.user.id,
            path: req.path,
        });

        next();
    } catch (error: any) {
        logger.warn('Authentication failed', {
            error: error.message,
            path: req.path,
        });

        res.status(401).json({
            error: {
                code: 'UNAUTHORIZED',
                message: error.message || 'Authentication failed',
            },
        });
    }
};
