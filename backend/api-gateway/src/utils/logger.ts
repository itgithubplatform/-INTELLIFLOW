/**
 * Logger Utility
 * ==============
 *
 * Winston-based logger for structured logging.
 */

import winston from 'winston';
import { config } from '../config';

const { combine, timestamp, json, colorize, printf } = winston.format;

// Custom format for development
const devFormat = printf(({ level, message, timestamp, ...meta }) => {
    const metaStr = Object.keys(meta).length ? JSON.stringify(meta) : '';
    return `${timestamp} [${level}]: ${message} ${metaStr}`;
});

// Create logger
export const logger = winston.createLogger({
    level: config.logLevel,
    format: combine(
        timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
        config.nodeEnv === 'development' ? colorize() : json()
    ),
    transports: [
        new winston.transports.Console({
            format: config.nodeEnv === 'development' ? devFormat : json(),
        }),
    ],
});
