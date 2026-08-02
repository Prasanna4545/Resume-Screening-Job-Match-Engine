import React from 'react';
import { Briefcase, FileText, Trophy, UserCheck, Sparkles } from 'lucide-react';

interface NavbarProps {
  activeTab: 'jobs' | 'resumes' | 'ranking' | 'detail';
  setActiveTab: (tab: 'jobs' | 'resumes' | 'ranking' | 'detail') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  const navItems = [
    { id: 'jobs', label: '1. Create Job', icon: Briefcase },
    { id: 'resumes', label: '2. Upload Resumes', icon: FileText },
    { id: 'ranking', label: '3. Candidate Ranking', icon: Trophy },
  ];

  return (
    <nav className="glass-nav sticky top-0 z-50 px-6 py-4 mb-8">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Brand */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('jobs')}>
          <div className="p-2.5 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 shadow-lg shadow-indigo-500/30">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-white via-slate-100 to-indigo-200 bg-clip-text text-transparent">
              TalentPulse AI
            </h1>
            <p className="text-xs text-indigo-300 font-medium">Resume Screening & Job Match Engine</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center bg-slate-900/90 p-1.5 rounded-xl border border-slate-800 shadow-inner">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id as any)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-md shadow-indigo-500/25'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>

        {/* Recruiter Badge */}
        <div className="hidden lg:flex items-center space-x-2 bg-slate-900/80 px-3.5 py-1.5 rounded-full border border-slate-800 text-xs font-medium text-slate-300">
          <UserCheck className="w-4 h-4 text-indigo-400" />
          <span>Recruiter Workspace</span>
        </div>
      </div>
    </nav>
  );
};
