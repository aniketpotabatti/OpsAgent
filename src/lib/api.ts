export const fetchAPI = async (endpoint: string, options: RequestInit = {}) => {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ''}/api${endpoint}`, options);
  return res.json();
};