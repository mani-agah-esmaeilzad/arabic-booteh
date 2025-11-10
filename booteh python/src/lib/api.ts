export type BlogPost = {
  id: number;
  title: string;
  slug: string;
  summary?: string;
  createdAt?: string;
};

export type PersonalityTest = {
  id: number;
  slug: string;
  title: string;
  description?: string;
};

export type MysteryAssessment = {
  id: number;
  name: string;
  summary?: string;
};

const rawBase = import.meta.env.VITE_BACKEND_URL;
const API_BASE = (rawBase && rawBase.trim().length > 0 ? rawBase : 'http://localhost:8000').replace(/\/$/, '');
const isAbsoluteBase = /^https?:/i.test(API_BASE);

const withBase = (path: string) => {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;

  if (!API_BASE) {
    return normalizedPath;
  }

  if (!isAbsoluteBase && normalizedPath.startsWith(API_BASE)) {
    return normalizedPath;
  }

  return `${API_BASE}${normalizedPath}`;
};

export async function fetchBlogPosts(limit?: number): Promise<BlogPost[]> {
  const query = typeof limit === 'number' ? `?limit=${limit}` : '';
  const response = await fetch(withBase(`/api/blog${query}`));
  if (!response.ok) {
    throw new Error('Failed to fetch blog posts');
  }
  const data = await response.json();
  return data?.data ?? [];
}

export async function fetchPersonalityTests(): Promise<PersonalityTest[]> {
  const response = await fetch(withBase('/api/personality-tests'));
  if (!response.ok) {
    throw new Error('Failed to fetch personality tests');
  }
  const data = await response.json();
  return data?.data ?? [];
}

export async function fetchMysteryAssessments(): Promise<MysteryAssessment[]> {
  const response = await fetch(withBase('/api/mystery'));
  if (!response.ok) {
    throw new Error('Failed to fetch mystery assessments');
  }
  const data = await response.json();
  return data?.data ?? [];
}

export async function submitSelfAssessment(answers: Record<string, number>) {
  const response = await fetch(withBase('/api'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ answers })
  });
  if (!response.ok) {
    throw new Error('Failed to submit assessment');
  }
  return response.json();
}
