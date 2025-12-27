/**
 * Express Application
 * ===================
 *
 * Express app configuration with middleware and routes.
 */

import express, { Application, Request, Response, NextFunction } from 'express';
import cors from 'cors';
import helmet from 'helmet';

import { config } from './config';
import { logger } from './utils/logger';
import { authMiddleware } from './middleware/auth.middleware';
import { rateLimitMiddleware } from './middleware/rate-limit.middleware';
import { errorMiddleware } from './middleware/error.middleware';
import { requestLogger } from './middleware/request-logger.middleware';
import routes from './routes';

const app: Application = express();

// Security middleware
app.use(helmet());

// CORS
app.use(cors({
    origin: config.corsOrigins,
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Source-Agent', 'X-Delegation'],
}));

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Request logging
app.use(requestLogger);

// Rate limiting
app.use(rateLimitMiddleware);

// Health check (before auth)
app.get('/health', (req: Request, res: Response) => {
    res.json({
        status: 'healthy',
        service: 'api-gateway',
        version: '1.0.0',
        timestamp: new Date().toISOString(),
    });
});

// Root endpoint
app.get('/', (req: Request, res: Response) => {
    res.json({
        name: 'IntelliFlow API Gateway',
        version: '1.0.0',
        description: 'API Gateway for the IntelliFlow multi-agent system',
        endpoints: {
            health: '/health',
            auth: '/api/auth/*',
            emails: '/api/v1/emails/*',
            calendar: '/api/v1/calendar/*',
        },
    });
});

// API Routes
app.use('/api', routes);

// 404 handler
app.use((req: Request, res: Response) => {
    res.status(404).json({
        error: {
            code: 'NOT_FOUND',
            message: `Route ${req.method} ${req.path} not found`,
        },
    });
});

// Error handling
app.use(errorMiddleware);

export default app;
