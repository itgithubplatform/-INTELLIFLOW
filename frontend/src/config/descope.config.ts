export const descopeConfig = {
    projectId: process.env.NEXT_PUBLIC_DESCOPE_PROJECT_ID || 'demo-project',

    // Flow IDs for different auth flows
    flows: {
        signIn: 'sign-in',
        signUp: 'sign-up',
        consent: 'oauth-consent',
    },

    // Theme configuration
    theme: 'dark',

    // Locale
    locale: 'en',
};
