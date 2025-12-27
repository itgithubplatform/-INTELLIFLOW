/**
 * Descope Service
 * ===============
 *
 * Service for interacting with Descope for token validation.
 */

import * as jose from 'jose';
import { config } from '../config';
import { logger } from '../utils/logger';

interface TokenClaims {
    sub: string;
    email?: string;
    name?: string;
    scopes: string[];
    exp: number;
    iat: number;
    iss: string;
    aud?: string;
}

class DescopeService {
    private jwks: jose.JWTVerifyGetKey | null = null;
    private projectId: string;

    constructor() {
        this.projectId = config.descopeProjectId;
    }

    /**
     * Get or create JWKS client
     */
    private async getJWKS(): Promise<jose.JWTVerifyGetKey> {
        if (!this.jwks) {
            const jwksUri = `https://api.descope.com/${this.projectId}/.well-known/jwks.json`;
            this.jwks = jose.createRemoteJWKSet(new URL(jwksUri));
        }
        return this.jwks;
    }

    /**
     * Validate a JWT token
     */
    async validateToken(token: string): Promise<TokenClaims> {
        try {
            // For development without Descope, return mock claims
            if (!this.projectId || config.nodeEnv === 'development') {
                logger.debug('Using mock token validation (development mode)');
                return this.getMockClaims(token);
            }

            const jwks = await this.getJWKS();

            const { payload } = await jose.jwtVerify(token, jwks, {
                issuer: `https://api.descope.com/${this.projectId}`,
                audience: this.projectId,
            });

            // Extract scopes
            let scopes: string[] = [];
            if (payload.scopes) {
                scopes = payload.scopes as string[];
            } else if (payload.scope) {
                const scope = payload.scope as string;
                scopes = scope.split(' ');
            } else if (payload.permissions) {
                scopes = payload.permissions as string[];
            }

            return {
                sub: payload.sub || '',
                email: payload.email as string | undefined,
                name: payload.name as string | undefined,
                scopes,
                exp: payload.exp || 0,
                iat: payload.iat || 0,
                iss: payload.iss || '',
                aud: payload.aud as string | undefined,
            };
        } catch (error: any) {
            logger.error('Token validation failed', { error: error.message });
            throw new Error(`Token validation failed: ${error.message}`);
        }
    }

    /**
     * Get mock claims for development
     */
    private getMockClaims(token: string): TokenClaims {
        return {
            sub: 'dev_user_123',
            email: 'dev@intelliflow.local',
            name: 'Development User',
            scopes: ['email.read', 'email.summarize', 'calendar.read', 'calendar.write'],
            exp: Math.floor(Date.now() / 1000) + 3600,
            iat: Math.floor(Date.now() / 1000),
            iss: 'intelliflow-dev',
        };
    }
}

export const descopeService = new DescopeService();
