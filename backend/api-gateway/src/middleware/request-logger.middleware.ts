/**
 * Request Logger Middleware
 * =========================
 *
 * Logs all incoming requests.
 */

import { Request, Response, NextFunction } from 'express';
import { logger } from '../utils/logger';
import { v4 as uuidv4 } from 'uuid';

export const requestLogger = (
    req: Request,
    res: Response,
    next: NextFunction
): void => {
    const requestId = uuidv4().substring(0, 8);
    const startTime = Date.now();

    // Add request ID to headers
    res.setHeader('X-Request-ID', requestId);

    // Log incoming request
    logger.info('Incoming request', {
        requestId,
        method: req.method,
        path: req.path,
        query: Object.keys(req.query).length > 0 ? req.query : undefined,
        userAgent: req.headers['user-agent'],
        ip: req.ip,
    });

    // Log response when finished
    res.on('finish', () => {
        const duration = Date.now() - startTime;

        const logLevel = res.statusCode >= 500 ? 'error'
            : res.statusCode >= 400 ? 'warn'
                : 'info';

        logger[logLevel]('Request completed', {
            requestId,
            method: req.method,
            path: req.path,
            statusCode: res.statusCode,
            duration: `${duration}ms`,
        });
    });

    next();
};
