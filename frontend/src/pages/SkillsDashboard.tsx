import React, { useState, useEffect } from "react";
import { 
  Award, 
  CheckCircle2, 
  HelpCircle, 
  Loader2, 
  Sparkles, 
  TrendingUp, 
  BookOpen,
  ArrowRight,
  Trash2,
  FileText,
  AlertCircle
} from "lucide-react";
import { motion } from "framer-motion";
import apiClient from "../api/client";
import { Skill, SkillGap, Resume } from "../types";

const POPULAR_ROLES = [
  "AI Engineer",
  "Data Scientist",
  "Backend Developer",
  "Product Manager",
  "Digital Marketing Specialist",
  "UX/UI Designer",
  "HR Manager",
  "Financial Analyst",
  "Sales Representative",
  "Content Writer",
  "Project Manager"
];

export const SkillsDashboard: React.FC = () => {
  const [selectedRole, setSelectedRole] = useState("AI Engineer");
  const [customRoleText, setCustomRoleText] = useState("");
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState<string>("");
  const [userSkills, setUserSkills] = useState<Skill[]>([]);
  const [gapAnalysis, setGapAnalysis] = useState<SkillGap | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // 1. Fetch user skills
      const userSkillsRes = await apiClient.get<Skill[]>("/skills");
      setUserSkills(userSkillsRes.data || []);

      // 2. Fetch resumes
      const resumesRes = await apiClient.get("/resumes/my-resumes");
      const list = resumesRes.data.resumes || [];
      setResumes(list);

      // 3. Initial gap analysis
      const gapRes = await apiClient.get<SkillGap>(`/skills/gap-analysis/AI Engineer`);
      setGapAnalysis(gapRes.data);
    } catch (err) {
      setError("Please upload a resume first to extract capabilities and analyze skills gap.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInitialData();
  }, []);

  const triggerAnalysis = async (role: string, resumeId: string) => {
    setAnalyzing(true);
    setError(null);
    try {
      const targetRole = role === "Custom" ? customRoleText.trim() : role;
      if (!targetRole) {
        setError("Please specify a target role for analysis.");
        setAnalyzing(false);
        return;
      }
      const url = `/skills/gap-analysis/${encodeURIComponent(targetRole)}${resumeId ? `?resume_id=${resumeId}` : ""}`;
      const response = await apiClient.get<SkillGap>(url);
      setGapAnalysis(response.data);
    } catch (err: any) {
      setError("Failed to run gap analysis for this role configuration.");
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDeleteSkill = async (skillId: string) => {
    if (!window.confirm("Are you sure you want to remove this skill from your profile catalog?")) {
      return;
    }
    try {
      await apiClient.delete(`/skills/${skillId}`);
      const userSkillsRes = await apiClient.get<Skill[]>("/skills");
      setUserSkills(userSkillsRes.data || []);
      // Re-trigger analysis using current settings
      triggerAnalysis(selectedRole, selectedResumeId);
    } catch (err) {
      setError("Failed to delete the skill.");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-purple-500" />
          <p className="text-gray-400 text-sm">Evaluating user skill catalog...</p>
        </div>
      </div>
    );
  }

  const selectedResumeName = selectedResumeId 
    ? resumes.find(r => r.id === selectedResumeId)?.filename 
    : "All Profile Skills";

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Target role selector bar */}
      <div className="glass-card rounded-3xl p-6 relative overflow-hidden space-y-6">
        <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-purple-500/20 to-transparent" />
        
        <div>
          <h2 className="font-heading font-bold text-xl text-white">Skills Intelligence Engine</h2>
          <p className="text-gray-400 text-xs mt-1">Configure your profile source and career targets to compute skill gaps.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-2">
          {/* 1. Skill Profile Source Context */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Skill Source Context</label>
            <select
              value={selectedResumeId}
              onChange={(e) => setSelectedResumeId(e.target.value)}
              className="w-full bg-[#0a0a0c] border border-white/10 rounded-xl px-4 py-3 text-xs text-gray-300 outline-none focus:border-purple-500/30 transition-colors"
            >
              <option value="">All Aggregated Profile Skills</option>
              {resumes.map((res) => (
                <option key={res.id} value={res.id}>
                  Resume: {res.filename}
                </option>
              ))}
            </select>
          </div>

          {/* 2. Target Role Dropdown */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Target Track Role</label>
            <select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
              className="w-full bg-[#0a0a0c] border border-white/10 rounded-xl px-4 py-3 text-xs text-gray-300 outline-none focus:border-purple-500/30 transition-colors"
            >
              {POPULAR_ROLES.map((role) => (
                <option key={role} value={role}>{role}</option>
              ))}
              <option value="Custom">Custom Role / Other...</option>
            </select>
          </div>

          {/* 3. Custom Input (conditional) or Trigger Button */}
          <div className="flex flex-col justify-end">
            {selectedRole === "Custom" ? (
              <div className="space-y-2 w-full">
                <label className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider">Enter Custom Role Name</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="e.g. Financial Consultant"
                    value={customRoleText}
                    onChange={(e) => setCustomRoleText(e.target.value)}
                    className="flex-1 bg-[#0a0a0c] border border-white/10 rounded-xl px-4 py-3 text-xs text-gray-300 outline-none focus:border-purple-500/30 transition-colors"
                  />
                  <button
                    onClick={() => triggerAnalysis(selectedRole, selectedResumeId)}
                    className="bg-purple-600 hover:bg-purple-500 text-white px-4 py-3 text-xs font-semibold rounded-xl transition-all duration-300"
                  >
                    Analyze
                  </button>
                </div>
              </div>
            ) : (
              <button
                onClick={() => triggerAnalysis(selectedRole, selectedResumeId)}
                className="w-full bg-purple-600 hover:bg-purple-500 text-white py-3 text-xs font-semibold rounded-xl transition-all duration-300 flex items-center justify-center space-x-2"
              >
                <Sparkles className="h-4 w-4 text-purple-300" />
                <span>Compute Skill Gap Analysis</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-yellow-500/10 border border-yellow-500/25 rounded-2xl text-yellow-400 text-sm flex items-start space-x-3">
          <AlertCircle className="h-5 w-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {analyzing ? (
        <div className="flex items-center justify-center py-20">
          <div className="flex flex-col items-center space-y-4">
            <Loader2 className="h-6 w-6 animate-spin text-purple-400" />
            <span className="text-xs text-gray-500 font-mono uppercase tracking-widest">Recalculating Skill Gaps...</span>
          </div>
        </div>
      ) : (
        gapAnalysis && (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            
            {/* Left side: Gap results & suggestions */}
            <div className="lg:col-span-3 space-y-6">
              
              {/* Score Gauge & Matched Summary Row */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                
                {/* Dial Score Gauge */}
                <div className="glass-card rounded-3xl p-6 flex flex-col items-center justify-center text-center">
                  <span className="text-[10px] text-purple-400 font-mono tracking-widest uppercase mb-4">Target Coverage</span>
                  
                  <div className="relative h-36 w-36 flex items-center justify-center mb-4">
                    <svg className="absolute transform -rotate-90 w-full h-full">
                      <circle cx="72" cy="72" r="62" className="stroke-white/[0.03]" strokeWidth="8" fill="transparent" />
                      <circle cx="72" cy="72" r="62" className="stroke-purple-500" strokeWidth="8" fill="transparent"
                        strokeDasharray={389}
                        strokeDashoffset={389 - (389 * gapAnalysis.match_percentage) / 100}
                        strokeLinecap="round"
                      />
                    </svg>
                    <div className="flex flex-col items-center">
                      <span className="text-3xl font-heading font-extrabold text-white">{gapAnalysis.match_percentage}%</span>
                      <span className="text-[9px] text-gray-500 font-mono">COVERAGE</span>
                    </div>
                  </div>
                  
                  <p className="text-[10px] text-gray-500 leading-relaxed">
                    Source: <span className="text-gray-300 font-medium">{selectedResumeName}</span>
                  </p>
                </div>

                {/* Matched skills */}
                <div className="glass-card rounded-3xl p-6 space-y-4 md:col-span-2">
                  <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider flex items-center space-x-2 border-b border-white/5 pb-2">
                    <CheckCircle2 className="h-4 w-4 text-green-400" />
                    <span>Matched Capabilities ({gapAnalysis.matched_skills.length})</span>
                  </h4>
                  <div className="flex flex-wrap gap-2 pt-1">
                    {gapAnalysis.matched_skills.length > 0 ? (
                      gapAnalysis.matched_skills.map((skill, idx) => (
                        <span key={idx} className="px-2.5 py-1 bg-green-500/10 border border-green-500/20 text-green-300 text-xs rounded-xl font-medium">
                          {skill}
                        </span>
                      ))
                    ) : (
                      <span className="text-gray-500 text-xs">No matching skills identified for this role yet.</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Missing skills & Focus areas */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* Missing Skills list */}
                <div className="glass-card rounded-3xl p-6 space-y-4">
                  <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider flex items-center space-x-2 border-b border-white/5 pb-2">
                    <HelpCircle className="h-4 w-4 text-purple-400" />
                    <span>Target Missing Skills ({gapAnalysis.missing_skills.length})</span>
                  </h4>
                  <div className="flex flex-wrap gap-2 pt-1">
                    {gapAnalysis.missing_skills.length > 0 ? (
                      gapAnalysis.missing_skills.map((skill, idx) => (
                        <span key={idx} className="px-2.5 py-1 bg-purple-500/10 border border-purple-500/20 text-purple-300 text-xs rounded-xl font-medium animate-pulse">
                          {skill}
                        </span>
                      ))
                    ) : (
                      <span className="text-green-400 text-xs font-medium">Perfect rating! You have 100% skill coverage.</span>
                    )}
                  </div>
                </div>

                {/* Categorized Study Focus Areas */}
                <div className="glass-card rounded-3xl p-6 space-y-4">
                  <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider flex items-center space-x-2 border-b border-white/5 pb-2">
                    <TrendingUp className="h-4 w-4 text-cyan-400" />
                    <span>Study Action Areas</span>
                  </h4>
                  <div className="space-y-3 pt-1">
                    {Object.keys(gapAnalysis.focus_areas).length > 0 ? (
                      Object.entries(gapAnalysis.focus_areas).map(([category, skills]) => (
                        <div key={category} className="p-3 bg-white/[0.01] border border-white/5 rounded-xl space-y-2">
                          <span className="text-xs font-semibold text-gray-300 block">{category}</span>
                          <div className="flex flex-wrap gap-1.5">
                            {skills.map((skill, i) => (
                              <span key={i} className="px-2 py-0.5 bg-white/5 text-gray-400 text-[10px] rounded border border-white/5">
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="text-gray-500 text-xs">No learning tasks recommended. Ready for applications!</p>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Right side: User Profile catalog management */}
            <div className="glass-card rounded-3xl p-6 space-y-6 lg:col-span-1 h-fit">
              <div className="border-b border-white/5 pb-4">
                <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Profile Skills Catalog</h3>
                <p className="text-[10px] text-gray-500 mt-1">Manually remove skills from your general profile index.</p>
              </div>

              <div className="space-y-2 max-h-[400px] overflow-y-auto pr-1">
                {userSkills.length === 0 ? (
                  <p className="text-xs text-gray-500">No skills registered yet.</p>
                ) : (
                  userSkills.map((skill) => (
                    <div 
                      key={skill.id} 
                      className="flex items-center justify-between p-2.5 bg-white/[0.01] border border-white/5 rounded-xl text-xs hover:border-white/10 transition-colors"
                    >
                      <span className="text-gray-300 font-medium">{skill.name}</span>
                      <button
                        onClick={() => handleDeleteSkill(skill.id)}
                        className="p-1 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors"
                        title="Remove Skill"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )
      )}
    </div>
  );
};
