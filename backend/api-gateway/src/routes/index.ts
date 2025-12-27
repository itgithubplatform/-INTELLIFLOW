/**
 * API Routes
 * ==========
 *
 * Main router combining all API routes.
 */

import { Router } from 'express';
import authRoutes from './auth.routes';
import proxyRoutes from './proxy.routes';

const router = Router();

// Auth routes (handled locally)
router.use('/auth', authRoutes);

// Proxy routes to agents
router.use('/v1', proxyRoutes);

export default router;
