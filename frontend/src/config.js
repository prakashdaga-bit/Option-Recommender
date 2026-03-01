// configuration for the application
// logic: use environment variable if available, otherwise default to local backend
const API_URL = import.meta.env.VITE_API_URL || 'https://option-recommender.onrender.com';

export { API_URL };
