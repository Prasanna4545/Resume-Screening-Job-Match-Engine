import React, { useEffect, useState } from 'react';
import { ArrowLeft, CheckCircle2, XCircle, Brain, Briefcase, GraduationCap, Award, FileText } from 'lucide-react';
import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Tooltip } from 'recharts';
import { getCandidateDetail, MatchResult, Job } from '../api/client';
import { ScoreBadge } from '../components/ScoreBadge';

interface CandidateDetailProps {
  selectedJob: Job | null;
  resumeId: string;
  onBack: () => void;
}

export const CandidateDetail: React.FC<CandidateDetailProps> = ({ selectedJob, resumeId, onBack }) => {
  const [detail, setDetail] = useState<MatchResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (selectedJob && resumeId) {
      setLoading(true);
      getCandidateDetail(selectedJob.id, resumeId)
        .then((res) => setDetail(res))
        .catch((err) => console.error(err))
        .finally(() => setLoading(false));
    }
  }, [selectedJob, resumeId]);

  if (loading || !detail) {
    return (
      <div className="glass-card rounded-2xl p-12 text-center text-slate-400">
        <p>Loading candidate evaluation breakdown...</p>
      </div>
    );
  }

  const chartData = [
    { metric: 'Semantic Embeddings', score: detail.semantic_similarity_score },
    { metric: 'Skill Taxonomy', score: detail.skill_match_score },
    { metric: 'Experience Years', score: detail.experience_match_score },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="flex items-center space-x-2 px-4 py-2 bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 rounded-xl text-sm font-semibold transition-all"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Rankings</span>
        </button>

        <div className="flex items-center space-x-3">
          <span className="text-sm font-bold text-slate-400">Overall Match:</span>
          <ScoreBadge score={detail.overall_score} size="lg" />
        </div>
      </div>

      {/* Profile Header */}
      <div className="glass-card rounded-2xl p-8 border border-slate-800 shadow-2xl relative overflow-hidden">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center space-x-1.5">
              <FileText className="w-4 h-4" />
              <span>Candidate Evaluation</span>
            </span>
            <h2 className="text-3xl font-extrabold text-white mt-1">
              {detail.resume?.candidate_name || 'Candidate Details'}
            </h2>
            <p className="text-sm text-slate-400 mt-1">
              {detail.resume?.email || 'No email provided'} • {detail.resume?.parsed_experience_years || 0} Years Industry Experience
            </p>
            {detail.resume?.parsed_education && detail.resume.parsed_education.length > 0 && (
              <div className="mt-3 flex items-center space-x-2 text-xs text-slate-300">
                <GraduationCap className="w-4 h-4 text-indigo-400 shrink-0" />
                <span><strong className="text-slate-400">Education:</strong> {detail.resume.parsed_education.join(', ')}</span>
              </div>
            )}
          </div>

          <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-slate-300 space-y-1">
            <div><strong className="text-slate-400">Job:</strong> {selectedJob?.title}</div>
            <div><strong className="text-slate-400">Min Exp Required:</strong> {selectedJob?.min_experience_years} years</div>
          </div>
        </div>

        {/* Natural Language Explanation */}
        {detail.explanation && (
          <div className="mt-6 p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-200 text-sm flex items-start space-x-3">
            <Brain className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
            <div>
              <strong className="block text-white mb-0.5 font-bold">AI Screening Diagnosis</strong>
              <span>{detail.explanation}</span>
            </div>
          </div>
        )}
      </div>

      {/* Sub-Score Analytics & Radar Visualizer */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-6">
          <h3 className="text-lg font-bold text-white flex items-center space-x-2">
            <Award className="w-5 h-5 text-indigo-400" />
            <span>Matching Signals Breakdown</span>
          </h3>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="70%" data={chartData}>
                <PolarGrid stroke="#334155" />
                <PolarAngleAxis dataKey="metric" stroke="#94a3b8" fontSize={11} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#334155" fontSize={10} />
                <Radar name="Score" dataKey="score" stroke="#818cf8" fill="#6366f1" fillOpacity={0.5} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff' }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Matched vs Missing Skills */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-6">
          <h3 className="text-lg font-bold text-white flex items-center space-x-2">
            <Briefcase className="w-5 h-5 text-indigo-400" />
            <span>Skill Gap Analysis</span>
          </h3>

          <div className="space-y-4">
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400 mb-2 flex items-center space-x-1.5">
                <CheckCircle2 className="w-4 h-4" />
                <span>Matched Skills ({detail.matched_skills.length})</span>
              </h4>
              <div className="flex flex-wrap gap-2">
                {detail.matched_skills.length > 0 ? (
                  detail.matched_skills.map((skill) => (
                    <span key={skill} className="px-3 py-1 rounded-lg text-xs font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                      {skill}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-slate-500">No overlapping skills found.</span>
                )}
              </div>
            </div>

            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-rose-400 mb-2 flex items-center space-x-1.5">
                <XCircle className="w-4 h-4" />
                <span>Missing Skills ({detail.missing_skills.length})</span>
              </h4>
              <div className="flex flex-wrap gap-2">
                {detail.missing_skills.length > 0 ? (
                  detail.missing_skills.map((skill) => (
                    <span key={skill} className="px-3 py-1 rounded-lg text-xs font-semibold bg-rose-500/10 text-rose-300 border border-rose-500/20">
                      {skill}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-emerald-400">All required skills satisfied!</span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
