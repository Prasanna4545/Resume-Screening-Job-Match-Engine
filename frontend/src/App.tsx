import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { UploadJob } from './pages/UploadJob';
import { UploadResumes } from './pages/UploadResumes';
import { CandidateRanking } from './pages/CandidateRanking';
import { CandidateDetail } from './pages/CandidateDetail';
import { getJobs, Job } from './api/client';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'jobs' | 'resumes' | 'ranking' | 'detail'>('jobs');
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null);

  useEffect(() => {
    getJobs()
      .then((data) => {
        setJobs(data);
        if (data.length > 0) {
          setSelectedJob(data[0]);
        }
      })
      .catch((err) => console.error('Error fetching jobs:', err));
  }, []);

  const handleJobCreated = (newJob: Job) => {
    setJobs([newJob, ...jobs]);
    setSelectedJob(newJob);
    setActiveTab('resumes');
  };

  const handleMatchingComplete = () => {
    setActiveTab('ranking');
  };

  const handleSelectCandidate = (candidateId: string) => {
    setSelectedCandidateId(candidateId);
    setActiveTab('detail');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col pb-16">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="flex-1 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
        {activeTab === 'jobs' && <UploadJob onJobCreated={handleJobCreated} />}
        {activeTab === 'resumes' && (
          <UploadResumes
            selectedJob={selectedJob}
            onMatchingComplete={handleMatchingComplete}
          />
        )}
        {activeTab === 'ranking' && (
          <CandidateRanking
            selectedJob={selectedJob}
            onSelectCandidate={handleSelectCandidate}
          />
        )}
        {activeTab === 'detail' && selectedCandidateId && (
          <CandidateDetail
            selectedJob={selectedJob}
            resumeId={selectedCandidateId}
            onBack={() => setActiveTab('ranking')}
          />
        )}
      </main>
    </div>
  );
};

export default App;
