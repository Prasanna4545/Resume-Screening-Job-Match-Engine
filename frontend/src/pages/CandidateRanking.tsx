import React, { useEffect, useState } from 'react';
import { Trophy, ChevronRight, User, Award } from 'lucide-react';
import { getMatchResults, MatchResult, Job } from '../api/client';
import { ScoreBadge } from '../components/ScoreBadge';

interface CandidateRankingProps {
  selectedJob: Job | null;
  onSelectCandidate: (candidateId: string) => void;
}

export const CandidateRanking: React.FC<CandidateRankingProps> = ({ selectedJob, onSelectCandidate }) => {
  const [results, setResults] = useState<MatchResult[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (selectedJob) {
      setLoading(true);
      getMatchResults(selectedJob.id)
        .then((res) => setResults(res))
        .catch((err) => console.error(err))
        .finally(() => setLoading(false));
    }
  }, [selectedJob]);

  if (!selectedJob) {
    return (
      <div className="glass-card rounded-2xl p-12 text-center text-slate-400">
        <Trophy className="w-12 h-12 text-slate-600 mx-auto mb-4" />
        <h3 className="text-xl font-bold text-white mb-2">No Job Selected</h3>
        <p className="text-sm max-w-md mx-auto">Create a job posting and upload candidate resumes to view rankings.</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-xs uppercase tracking-wider font-bold text-indigo-400">Ranked Results</span>
          <h2 className="text-2xl font-bold text-white">{selectedJob.title}</h2>
          <p className="text-sm text-slate-400">Screened candidates ordered by overall weighted matching score.</p>
        </div>
        <div className="flex items-center space-x-3 bg-slate-900 px-4 py-2 rounded-xl border border-slate-800 text-sm font-semibold text-slate-300">
          <Award className="w-4 h-4 text-indigo-400" />
          <span>{results.length} Candidates Evaluated</span>
        </div>
      </div>

      {/* Leaderboard Table */}
      <div className="glass-card rounded-2xl border border-slate-800 overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900/90 border-b border-slate-800 text-xs uppercase tracking-wider text-slate-400 font-bold">
                <th className="py-4 px-6">Rank</th>
                <th className="py-4 px-6">Candidate</th>
                <th className="py-4 px-6">Overall Score</th>
                <th className="py-4 px-6">Sub-Score Breakdown</th>
                <th className="py-4 px-6">Matched Skills</th>
                <th className="py-4 px-6 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-sm">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500">
                    Loading ranked candidates...
                  </td>
                </tr>
              ) : results.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500">
                    No candidates matched yet. Upload resumes to get started.
                  </td>
                </tr>
              ) : (
                results.map((res, index) => {
                  const candidateName = res.resume?.candidate_name || `Candidate #${index + 1}`;
                  return (
                    <tr
                      key={res.id}
                      onClick={() => onSelectCandidate(res.resume_id)}
                      className="hover:bg-slate-800/40 cursor-pointer transition-colors group"
                    >
                      <td className="py-4 px-6 font-extrabold text-slate-400">
                        #{index + 1}
                      </td>
                      <td className="py-4 px-6">
                        <div className="flex items-center space-x-3">
                          <div className="p-2 rounded-lg bg-slate-800 border border-slate-700 text-indigo-400">
                            <User className="w-4 h-4" />
                          </div>
                          <div>
                            <div className="font-bold text-white group-hover:text-indigo-300 transition-colors">
                              {candidateName}
                            </div>
                            <div className="text-xs text-slate-500">
                              {res.resume?.parsed_experience_years || 0} yrs experience
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-6">
                        <ScoreBadge score={res.overall_score} size="md" />
                      </td>
                      <td className="py-4 px-6">
                        <div className="space-y-1.5 w-48">
                          <div className="flex justify-between text-xs text-slate-400">
                            <span>Semantic</span>
                            <span className="font-mono text-slate-200">{res.semantic_similarity_score.toFixed(0)}%</span>
                          </div>
                          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                            <div
                              className="bg-indigo-500 h-full rounded-full"
                              style={{ width: `${res.semantic_similarity_score}%` }}
                            />
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-6">
                        <div className="flex flex-wrap gap-1">
                          {res.matched_skills.slice(0, 3).map((skill) => (
                            <span key={skill} className="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                              {skill}
                            </span>
                          ))}
                          {res.matched_skills.length > 3 && (
                            <span className="text-[11px] text-slate-500 font-semibold self-center">
                              +{res.matched_skills.length - 3} more
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="py-4 px-6 text-right">
                        <span className="p-2 rounded-lg bg-slate-800 text-slate-300 group-hover:bg-indigo-600 group-hover:text-white transition-all inline-block">
                          <ChevronRight className="w-4 h-4" />
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
