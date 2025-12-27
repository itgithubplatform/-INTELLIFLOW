export const apiConfig = {
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001',

    // API endpoints
    endpoints: {
        auth: {
            validate: '/api/auth/validate',
            me: '/api/auth/me',
            refresh: '/api/auth/refresh',
        },
        emails: {
            list: '/api/v1/emails',
            get: (id: string) => `/api/v1/emails/${id}`,
            summarize: '/api/v1/emails/summarize',
        },
        calendar: {
            events: '/api/v1/calendar/events',
            getEvent: (id: string) => `/api/v1/calendar/events/${id}`,
        },
    },
};
