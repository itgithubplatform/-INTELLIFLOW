/**
 * API Gateway Entry Point
 * =======================
 *
 * Main entry point for the IntelliFlow API Gateway.
 * Routes requests to appropriate agents with authentication.
 */

import dotenv from 'dotenv';
dotenv.config();

import app from './app';
import { config } from './config';
import { logger } from './utils/logger';

const PORT = config.port;

app.listen(PORT, () => {
    logger.info(`🚀 API Gateway running on port ${PORT}`);
    logger.info(`Environment: ${config.nodeEnv}`);
    logger.info(`Agent A URL: ${config.agentAUrl}`);
    logger.info(`Agent B URL: ${config.agentBUrl}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    logger.info('SIGTERM received. Shutting down gracefully...');
    process.exit(0);
});

process.on('SIGINT', () => {
    logger.info('SIGINT received. Shutting down gracefully...');
    process.exit(0);
});
