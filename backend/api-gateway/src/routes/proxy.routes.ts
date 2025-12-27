/**
 * Proxy Routes
 * ============
 *
 * Routes that proxy requests to the backend agents.
 */

import { Router } from 'express';
import { createProxyMiddleware, Options } from 'http-proxy-middleware';
import { config } from '../config';
import { authMiddleware } from '../middleware/auth.middleware';
import { logger } from '../utils/logger';

const router = Router();

// Proxy options for Agent A (Email Summarizer)
const agentAProxyOptions: Options = {
    target: config.agentAUrl,
    changeOrigin: true,
    pathRewrite: {
        '^/api/v1/emails': '/api/v1/emails',
    },
    onProxyReq: (proxyReq, req) => {
        logger.info('Proxying to Agent A', {
            method: req.method,
            path: req.path,
            target: config.agentAUrl,
        });
    },
    onError: (err, req, res: any) => {
        logger.error('Proxy error to Agent A', { error: err.message });
        res.status(502).json({
            error: {
                code: 'PROXY_ERROR',
                message: 'Failed to reach Agent A',
            },
        });
    },
};

// Proxy options for Agent B (Calendar Manager)
const agentBProxyOptions: Options = {
    target: config.agentBUrl,
    changeOrigin: true,
    pathRewrite: {
        '^/api/v1/calendar': '/api/v1/calendar',
    },
    onProxyReq: (proxyReq, req) => {
        logger.info('Proxying to Agent B', {
            method: req.method,
            path: req.path,
            target: config.agentBUrl,
        });
    },
    onError: (err, req, res: any) => {
        logger.error('Proxy error to Agent B', { error: err.message });
        res.status(502).json({
            error: {
                code: 'PROXY_ERROR',
                message: 'Failed to reach Agent B',
            },
        });
    },
};

// Apply auth middleware to all proxy routes
router.use(authMiddleware);

// Proxy email routes to Agent A
router.use('/emails', createProxyMiddleware(agentAProxyOptions));

// Proxy calendar routes to Agent B
router.use('/calendar', createProxyMiddleware(agentBProxyOptions));

export default router;
