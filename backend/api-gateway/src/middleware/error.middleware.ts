/**
 * Error Middleware
 * ================
 *
 * Global error handling middleware.
 */

import { Request, Response, NextFunction } from 'express';
import { logger } from '../utils/logger';

export const errorMiddleware = (
    error: Error,
    req: Request,
    res: Response,
    next: NextFunction
): void => {
    logger.error('Unhandled error', {
        error: error.message,
        stack: error.stack,
        path: req.path,
        method: req.method,
    });

    res.status(500).json({
        error: {
            code: 'INTERNAL_SERVER_ERROR',
            message: process.env.NODE_ENV === 'development'
                ? error.message
                : 'An unexpected error occurred',
        },
    });
};
