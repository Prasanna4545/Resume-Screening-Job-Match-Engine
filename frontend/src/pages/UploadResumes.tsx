import React, { useState } from 'react';
import { UploadCloud, FileText, CheckCircle, ArrowRight, Loader2 } from 'lucide-react';
import { uploadResumes, runMatching, Job } from '../api/client';

interface UploadResumesProps {
  selectedJob: Job | null;
  onMatchingComplete: () => void;
}

export const UploadResumes: React.FC<UploadResumesProps> = ({ selectedJob, onMatchingComplete }) => {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleUploadAndMatch = async () => {
    if (!selectedJob) {
      alert('Please select or create a job posting first!');
      return;
    }
    if (files.length === 0) {
      alert('Please select at least one PDF/DOCX resume file.');
      return;
    }

    try {
      setUploading(true);
      setStatusMsg('Parsing resumes & extracting candidate entities...');
      const uploaded = await uploadResumes(files);
      
      setStatusMsg('Executing NLP embedding vector calculations & hybrid matching engine...');
      const resumeIds = uploaded.map((r) => r.id);
      await runMatching(selectedJob.id, resumeIds);

      setStatusMsg('Matching complete!');
      setTimeout(() => {
        onMatchingComplete();
      }, 1000);
    } catch (err) {
      console.error(err);
      setStatusMsg('Error during upload or matching process.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Target Job Banner */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 flex items-center justify-between">
        <div>
          <span className="text-xs uppercase tracking-wider font-bold text-indigo-400">Target Role</span>
          <h3 className="text-lg font-bold text-white">
            {selectedJob ? selectedJob.title : 'No Job Selected'}
          </h3>
        </div>
        {selectedJob && (
          <span className="px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-semibold rounded-lg">
            {selectedJob.required_skills.length} Required Skills
          </span>
        )}
      </div>

      {/* Upload Zone */}
      <div className="glass-card rounded-2xl p-8 border border-slate-800 shadow-2xl text-center relative overflow-hidden">
        <div className="border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-xl p-12 transition-all group bg-slate-900/50">
          <UploadCloud className="w-16 h-16 text-indigo-400 mx-auto mb-4 group-hover:scale-110 transition-transform" />
          <h3 className="text-xl font-bold text-white mb-2">Upload Candidate Resumes</h3>
          <p className="text-slate-400 text-sm mb-6 max-w-md mx-auto">
            Drag & drop PDF or DOCX resume files here, or click to browse files for batch screening.
          </p>

          <input
            type="file"
            multiple
            accept=".pdf,.docx,.txt"
            onChange={handleFileChange}
            id="resume-upload"
            className="hidden"
          />
          <label
            htmlFor="resume-upload"
            className="px-6 py-3 bg-slate-800 hover:bg-slate-700 text-white font-semibold rounded-xl cursor-pointer inline-block transition-all border border-slate-700"
          >
            Select Resume Files
          </label>
        </div>

        {/* Selected File List */}
        {files.length > 0 && (
          <div className="mt-8 text-left space-y-3">
            <h4 className="text-sm font-bold text-slate-300">Selected Files ({files.length})</h4>
            <div className="max-h-48 overflow-y-auto space-y-2 pr-2">
              {files.map((file, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-slate-900 rounded-xl border border-slate-800 text-sm">
                  <div className="flex items-center space-x-3 text-slate-200">
                    <FileText className="w-4 h-4 text-indigo-400" />
                    <span className="font-medium truncate max-w-xs">{file.name}</span>
                  </div>
                  <span className="text-xs text-slate-500">{(file.size / 1024).toFixed(1)} KB</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {statusMsg && (
          <div className="mt-6 p-4 rounded-xl bg-slate-900 border border-slate-800 text-indigo-300 text-sm flex items-center justify-center space-x-2">
            {uploading ? <Loader2 className="w-4 h-4 animate-spin text-indigo-400" /> : <CheckCircle className="w-4 h-4 text-emerald-400" />}
            <span>{statusMsg}</span>
          </div>
        )}

        <button
          onClick={handleUploadAndMatch}
          disabled={uploading || files.length === 0}
          className="w-full mt-8 py-4 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 disabled:opacity-50 text-white font-bold rounded-xl shadow-lg shadow-indigo-500/25 flex items-center justify-center space-x-2 transition-all"
        >
          <span>Run AI Candidate Screening</span>
          <ArrowRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};
