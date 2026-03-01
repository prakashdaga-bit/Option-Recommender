// configuration for the application
// logic: use environment variable if available, otherwise default to local backend
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export { API_URL };
