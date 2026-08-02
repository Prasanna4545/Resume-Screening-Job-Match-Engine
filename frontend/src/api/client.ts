import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Job {
  id: string;
  title: string;
  description: string;
  required_skills: string[];
  min_experience_years: number;
  created_at: string;
}

export interface Resume {
  id: string;
  candidate_name: string;
  email?: string;
  raw_text: string;
  parsed_skills: string[];
  parsed_experience_years: number;
  parsed_education: string[];
  file_path?: string;
  uploaded_at: string;
}

export interface MatchResult {
  id: string;
  job_id: string;
  resume_id: string;
  overall_score: number;
  skill_match_score: number;
  experience_match_score: number;
  semantic_similarity_score: number;
  matched_skills: string[];
  missing_skills: string[];
  explanation?: string;
  created_at: string;
  resume?: Resume;
}

export const fetchHealth = async () => {
  const res = await apiClient.get('/health');
  return res.data;
};

export const createJob = async (jobData: { title: string; description: string; required_skills: string[]; min_experience_years: number }) => {
  const res = await apiClient.post<Job>('/jobs', jobData);
  return res.data;
};

export const getJobs = async () => {
  const res = await apiClient.get<Job[]>('/jobs');
  return res.data;
};

export const uploadResumes = async (files: File[]) => {
  const formData = new FormData();
  files.forEach((file) => formData.append('files', file));
  const res = await apiClient.post<Resume[]>('/resumes/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
};

export const runMatching = async (job_id: string, resume_ids?: string[]) => {
  const res = await apiClient.post<MatchResult[]>('/matching/run', { job_id, resume_ids });
  return res.data;
};

export const getMatchResults = async (job_id: string) => {
  const res = await apiClient.get<MatchResult[]>(`/matching/results/${job_id}`);
  return res.data;
};

export const getCandidateDetail = async (job_id: string, resume_id: string) => {
  const res = await apiClient.get<MatchResult>(`/matching/results/${job_id}/${resume_id}`);
  return res.data;
};
