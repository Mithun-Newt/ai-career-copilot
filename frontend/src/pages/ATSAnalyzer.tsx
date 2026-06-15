import React, { useState, useEffect } from "react";
import { 
  FileText, 
  Sparkles, 
  Loader2, 
  CheckCircle2, 
  AlertTriangle,
  Lightbulb,
  Award,
  ChevronRight,
  TrendingUp,
  Brain,
  Trash2
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import apiClient from "../api/client";
import { Resume } from "../types";

interface ATSAnalysisData {
  id: string;
  resume_id: string;
  ats_score: number;
  match_percentage: number;
  missing_skills: string[];
  missing_keywords: string[];
  strengths: string[];
  weaknesses: string[];
  recommendations: {
    improvement_suggestions: string[];
    recommended_projects: string[];
    interview_preparation_topics: string[];
  };
  created_at: string;
}

export const ATSAnalyzer: React.FC = () => {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  
  const [history, setHistory] = useState<ATSAnalysisData[]>([]);
  const [activeAnalysis, setActiveAnalysis] = useState<ATSAnalysisData | null>(null);
  
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const resumesRes = await apiClient.get("/resumes/my-resumes");
      const list = resumesRes.data.resumes || [];
      setResumes(list);
      if (list.length > 0) {
        setSelectedResumeId(list[0].id);
      }

      const historyRes = await apiClient.get<ATSAnalysisData[]>("/ats");
      const savedAnalyses = historyRes.data || [];
      setHistory(savedAnalyses);
      if (savedAnalyses.length > 0) {
        setActiveAnalysis(savedAnalyses[0]);
      }
    } catch (err: any) {
      setError("Failed to load analyzer options.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedResumeId || !jobDescription.trim()) {
      setError("Please select a resume and paste a job description.");
      return;
    }

    setAnalyzing(true);
    setError(null);
    setActiveAnalysis(null);

    try {
      const response = await apiClient.post<ATSAnalysisData>("/ats/analyze", {
        resume_id: selectedResumeId,
        job_description: jobDescription
      });
      
      const result = response.data;
      setActiveAnalysis(result);
      setJobDescription("");
      
      const historyRes = await apiClient.get<ATSAnalysisData[]>("/ats");
      setHistory(historyRes.data || []);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 
        "ATS analysis execution failed. Please ensure resume is parsed."
      );
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDeleteRecord = async (e: React.MouseEvent, recordId: string) => {
    e.stopPropagation();
    if (!confirm("Delete this analysis record?")) return;
    try {
      await apiClient.delete(`/ats/${recordId}`);
      if (activeAnalysis?.id === recordId) {
        setActiveAnalysis(null);
      }
      setHistory(prev => prev.filter(item => item.id !== recordId));
    } catch (err: any) {
      setError("Failed to delete record.");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-purple-500" />
          <p className="text-gray-400 text-sm">Compiling analyzer options...</p>
        </div>
      </div>
    );
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
      {/* Header Info */}
      <div className="relative overflow-hidden rounded-3xl border border-white/5 bg-[#0a0a0c]/40 p-6 backdrop-blur-xl">
        <div className="absolute top-0 right-0 w-[30%] h-[100%] bg-gradient-to-l from-purple-500/5 to-transparent blur-[50px] pointer-events-none" />
        <div className="max-w-2xl relative space-y-1">
          <div className="inline-flex items-center space-x-2 px-3 py-1 bg-purple-500/10 border border-purple-500/20 rounded-full text-xs text-purple-300">
            <Sparkles className="h-3 w-3 text-purple-400" />
            <span>ATS Parser & Keyword Match Active</span>
          </div>
          <h2 className="font-heading font-bold text-2xl text-white">ATS Resume Analyzer</h2>
          <p className="text-gray-400 text-xs mt-1">
            Compare your resume against any job description to compute compatibility score, missing keywords, and interview topics.
          </p>
        </div>
      </div>

      {error && (
        <motion.div initial={{ y: -10, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="p-4 bg-yellow-500/10 border border-yellow-500/25 rounded-2xl flex items-start space-x-3 text-yellow-400 text-sm">
          <AlertTriangle className="h-5 w-5 flex-shrink-0" />
          <span>{error}</span>
        </motion.div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Left Side: Saved evaluations sidebar list */}
        <div className="glass-card rounded-3xl p-6 space-y-6 h-fit lg:col-span-1">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Saved Matches</h3>
            <button
              onClick={() => {
                setActiveAnalysis(null);
                setError(null);
              }}
              className="text-[10px] text-purple-400 hover:text-purple-300 font-medium"
            >
              Analyze New
            </button>
          </div>
          <div className="space-y-3">
            {history.length === 0 ? (
              <p className="text-xs text-gray-500">No evaluations yet.</p>
            ) : (
              <AnimatePresence>
                {history.map((h, i) => {
                  const isSelected = activeAnalysis?.id === h.id;
                  return (
                    <motion.div
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, scale: 0.9 }}
                      transition={{ delay: i * 0.05 }}
                      key={h.id}
                      onClick={() => {
                        setActiveAnalysis(h);
                        setError(null);
                      }}
                      className={`p-3 rounded-2xl border transition-all duration-300 cursor-pointer flex items-center justify-between group ${
                        isSelected 
                          ? "bg-purple-500/10 border-purple-500/30 text-purple-300 shadow-[0_0_15px_rgba(168,85,247,0.1)]" 
                          : "bg-white/[0.01] border-white/5 hover:border-white/15 hover:bg-white/[0.02]"
                      }`}
                    >
                      <div className="min-w-0 flex-1">
                        <h4 className="text-xs font-semibold text-white truncate">Match Analysis</h4>
                        <p className="text-[9px] text-gray-500 font-mono mt-0.5">Score: {h.ats_score}% | Match: {h.match_percentage}%</p>
                      </div>
                      <button
                        onClick={(e) => handleDeleteRecord(e, h.id)}
                        className="p-1 text-gray-500 hover:text-red-400 rounded-lg hover:bg-red-500/5 transition-all duration-300 opacity-0 group-hover:opacity-100"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </motion.div>
                  );
                })}
              </AnimatePresence>
            )}
          </div>
        </div>

        {/* Right Side: Detail Page or Form */}
        <div className="lg:col-span-3 space-y-6">
          <AnimatePresence mode="wait">
            {analyzing ? (
              <motion.div 
                key="analyzing"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="glass-card rounded-3xl p-12 flex flex-col items-center justify-center py-20 space-y-4"
              >
                <Loader2 className="h-8 w-8 animate-spin text-purple-500" />
                <div className="text-center space-y-1">
                  <h4 className="text-sm font-semibold text-white">AI Recruiting Engine Evaluating Match...</h4>
                  <p className="text-xs text-gray-500">Parsing keyword densities and scanning skills alignment.</p>
                </div>
              </motion.div>
            ) : !activeAnalysis ? (
              <motion.form 
                key="form"
                initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                onSubmit={handleAnalyze} 
                className="glass-card rounded-3xl p-8 space-y-6"
              >
                <div className="border-b border-white/5 pb-4">
                  <h3 className="font-heading font-bold text-lg text-white">Job Match Parser</h3>
                  <p className="text-xs text-gray-400 mt-1">Select your resume and paste the target job description text to execute scanning.</p>
                </div>

                <div className="space-y-4">
                  {/* Resume selection */}
                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Select Resume Profile</label>
                    <select
                      value={selectedResumeId}
                      onChange={(e) => setSelectedResumeId(e.target.value)}
                      className="w-full bg-[#0a0a0c] border border-white/10 rounded-xl px-4 py-3 text-xs text-gray-300 outline-none focus:border-purple-500/30 transition-colors"
                    >
                      {resumes.length === 0 ? (
                        <option value="">No Resumes Found - Upload first</option>
                      ) : (
                        resumes.map((res) => (
                          <option key={res.id} value={res.id}>
                            {res.filename}
                          </option>
                        ))
                      )}
                    </select>
                  </div>

                  {/* Job description textarea */}
                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Pasted Job Description</label>
                    <textarea
                      required
                      value={jobDescription}
                      onChange={(e) => setJobDescription(e.target.value)}
                      placeholder="Paste the full job requirements or job posting description here..."
                      rows={8}
                      className="w-full bg-[#0a0a0c] border border-white/10 rounded-xl px-4 py-3.5 text-xs text-gray-300 outline-none focus:border-purple-500/30 placeholder:text-gray-600 resize-none font-sans transition-colors"
                    />
                  </div>
                </div>

                <div className="flex justify-end pt-2">
                  <button
                    type="submit"
                    disabled={analyzing}
                    className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-500 px-6 py-3 rounded-xl text-white text-xs font-semibold transition-all duration-300 disabled:opacity-50 shadow-[0_0_15px_rgba(168,85,247,0.3)]"
                  >
                    <Sparkles className="h-4 w-4 text-purple-300" />
                    <span>Analyze Compatibility</span>
                  </button>
                </div>
              </motion.form>
            ) : (
              <motion.div 
                key="results"
                initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                className="grid grid-cols-1 md:grid-cols-3 gap-6"
              >
                {/* Gauges card metrics */}
                <div className="md:col-span-1 space-y-6">
                  {/* ATS score card */}
                  <motion.div initial={{ scale: 0.95 }} animate={{ scale: 1 }} transition={{ delay: 0.1 }} className="glass-card rounded-3xl p-6 text-center space-y-4 relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-[40%] h-[100%] bg-gradient-to-l from-purple-500/5 to-transparent blur-[30px] pointer-events-none" />
                    <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">ATS Score</h4>
                    <div className="relative flex items-center justify-center">
                      <svg className="w-28 h-28 transform -rotate-90">
                        <circle cx="56" cy="56" r="48" className="text-white/5" strokeWidth="6" stroke="currentColor" fill="transparent" />
                        <motion.circle 
                          cx="56" cy="56" r="48" 
                          className="text-purple-500" 
                          strokeWidth="6" 
                          strokeDasharray={301.6} 
                          initial={{ strokeDashoffset: 301.6 }}
                          animate={{ strokeDashoffset: 301.6 - (301.6 * activeAnalysis.ats_score) / 100 }} 
                          transition={{ duration: 1.5, ease: "easeOut" }}
                          strokeLinecap="round" stroke="currentColor" fill="transparent" 
                        />
                      </svg>
                      <span className="absolute text-xl font-bold font-heading text-white">{activeAnalysis.ats_score}%</span>
                    </div>
                    <p className="text-[10px] text-gray-500 leading-relaxed">System parsing index based on matching keyword frequencies.</p>
                  </motion.div>

                  {/* Match percentage card */}
                  <motion.div initial={{ scale: 0.95 }} animate={{ scale: 1 }} transition={{ delay: 0.2 }} className="glass-card rounded-3xl p-6 text-center space-y-4 relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-[40%] h-[100%] bg-gradient-to-l from-cyan-500/5 to-transparent blur-[30px] pointer-events-none" />
                    <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Job Match</h4>
                    <div className="relative flex items-center justify-center">
                      <svg className="w-28 h-28 transform -rotate-90">
                        <circle cx="56" cy="56" r="48" className="text-white/5" strokeWidth="6" stroke="currentColor" fill="transparent" />
                        <motion.circle 
                          cx="56" cy="56" r="48" 
                          className="text-cyan-500" 
                          strokeWidth="6" 
                          strokeDasharray={301.6} 
                          initial={{ strokeDashoffset: 301.6 }}
                          animate={{ strokeDashoffset: 301.6 - (301.6 * activeAnalysis.match_percentage) / 100 }} 
                          transition={{ duration: 1.5, ease: "easeOut", delay: 0.2 }}
                          strokeLinecap="round" stroke="currentColor" fill="transparent" 
                        />
                      </svg>
                      <span className="absolute text-xl font-bold font-heading text-white">{activeAnalysis.match_percentage}%</span>
                    </div>
                    <p className="text-[10px] text-gray-500 leading-relaxed">Qualification match based on resume skills and roles requirements.</p>
                  </motion.div>
                </div>

                {/* Detail columns layout */}
                <div className="md:col-span-2 space-y-6">
                  <div className="glass-card rounded-3xl p-8 space-y-8">
                    {/* Missing keywords list */}
                    <div className="space-y-3">
                      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                        <AlertTriangle className="h-4 w-4 text-yellow-500" />
                        <span>Missing Skills & Keywords</span>
                      </h3>
                      <div className="flex flex-wrap gap-2 pt-1">
                        {activeAnalysis.missing_skills.length === 0 && activeAnalysis.missing_keywords.length === 0 ? (
                          <p className="text-xs text-green-400 flex items-center gap-1.5"><CheckCircle2 className="h-4 w-4" /> Perfect keyword match!</p>
                        ) : (
                          [...activeAnalysis.missing_skills, ...activeAnalysis.missing_keywords].map((key, i) => (
                            <motion.span 
                              initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.3 + i * 0.05 }}
                              key={i} className="text-[10px] bg-red-500/10 border border-red-500/20 text-red-400 font-mono px-2.5 py-0.5 rounded-full"
                            >
                              {key}
                            </motion.span>
                          ))
                        )}
                      </div>
                    </div>

                    {/* Strengths list */}
                    <div className="space-y-3 border-t border-white/5 pt-6">
                      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                        <TrendingUp className="h-4 w-4 text-green-500" />
                        <span>Key Strengths Identified</span>
                      </h3>
                      <ul className="space-y-2 pt-1">
                        {activeAnalysis.strengths.map((str, i) => (
                          <motion.li 
                            initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 + i * 0.05 }}
                            key={i} className="text-xs text-gray-300 flex items-start gap-2.5"
                          >
                            <CheckCircle2 className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                            <span>{str}</span>
                          </motion.li>
                        ))}
                      </ul>
                    </div>

                    {/* Weaknesses list */}
                    <div className="space-y-3 border-t border-white/5 pt-6">
                      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                        <AlertTriangle className="h-4 w-4 text-red-500" />
                        <span>Weak Areas</span>
                      </h3>
                      <ul className="space-y-2 pt-1">
                        {activeAnalysis.weaknesses.map((w, i) => (
                          <motion.li 
                            initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 + i * 0.05 }}
                            key={i} className="text-xs text-gray-400 flex items-start gap-2.5"
                          >
                            <ChevronRight className="h-4 w-4 text-purple-400 flex-shrink-0 mt-0.5" />
                            <span>{w}</span>
                          </motion.li>
                        ))}
                      </ul>
                    </div>

                    {/* Actionable recommendations list */}
                    <div className="space-y-4 border-t border-white/5 pt-6">
                      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                        <Lightbulb className="h-4 w-4 text-purple-400" />
                        <span>Resume Improvement & Recommended Projects</span>
                      </h3>
                      
                      <div className="space-y-3">
                        <h4 className="text-[11px] font-semibold text-white">Suggestions:</h4>
                        <ul className="space-y-1.5 pl-4 list-disc text-xs text-gray-400">
                          {activeAnalysis.recommendations.improvement_suggestions.map((sug, i) => (
                            <motion.li initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 + i * 0.1 }} key={i}>{sug}</motion.li>
                          ))}
                        </ul>
                      </div>

                      <div className="space-y-3 pt-2">
                        <h4 className="text-[11px] font-semibold text-white">Bridging Projects:</h4>
                        <ul className="space-y-1.5 pl-4 list-disc text-xs text-gray-400">
                          {activeAnalysis.recommendations.recommended_projects.map((proj, i) => (
                            <motion.li initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.7 + i * 0.1 }} key={i}>{proj}</motion.li>
                          ))}
                        </ul>
                      </div>

                      <div className="space-y-3 pt-2">
                        <h4 className="text-[11px] font-semibold text-white flex items-center gap-1.5 text-purple-300">
                          <Brain className="h-4 w-4" />
                          <span>Interview Preparation Topics:</span>
                        </h4>
                        <div className="flex flex-wrap gap-2 pl-2">
                          {activeAnalysis.recommendations.interview_preparation_topics.map((top, i) => (
                            <motion.span 
                              initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.8 + i * 0.05 }}
                              key={i} className="text-[10px] bg-purple-500/10 border border-purple-500/15 text-purple-300 px-2 py-0.5 rounded-lg"
                            >
                              {top}
                            </motion.span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  );
};
