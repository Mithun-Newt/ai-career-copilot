import React, { useState, useEffect } from "react";
import { 
  Sparkles, 
  Loader2, 
  CheckCircle2, 
  Circle, 
  ShieldCheck,
  AlertCircle,
  Plus,
  BookOpen,
  Calendar,
  Map,
  Trash2,
  Play,
  ExternalLink
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import apiClient from "../api/client";
import { Resume, Roadmap, RoadmapTask } from "../types";

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

export const RoadmapDashboard: React.FC = () => {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [roadmaps, setRoadmaps] = useState<Roadmap[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState<string>("");
  const [selectedRole, setSelectedRole] = useState("AI Engineer");
  const [customRoleText, setCustomRoleText] = useState("");
  
  const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
  const [showGenerator, setShowGenerator] = useState(false);
  
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [updatingTaskId, setUpdatingTaskId] = useState<string | null>(null);
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

      const roadmapsRes = await apiClient.get("/roadmaps");
      const savedRoadmaps = roadmapsRes.data || [];
      setRoadmaps(savedRoadmaps);
      
      if (savedRoadmaps.length > 0 && !roadmap) {
        setRoadmap(savedRoadmaps[0]);
      } else if (savedRoadmaps.length === 0) {
        setShowGenerator(true);
      }
    } catch (err: any) {
      setError("Failed to load dashboard data. Please check connection.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleGenerateRoadmap = async () => {
    if (!selectedResumeId) {
      setError("Please upload a resume first under the Resume Hub before generating a roadmap pathway.");
      return;
    }

    const targetRole = selectedRole === "Custom" ? customRoleText.trim() : selectedRole;
    if (!targetRole) {
      setError("Please specify a target career role pathway.");
      return;
    }

    setGenerating(true);
    setError(null);
    setRoadmap(null);

    try {
      const response = await apiClient.post("/roadmaps/generate", {
        resume_id: selectedResumeId,
        target_role: targetRole,
      });
      
      const newRoadmap = response.data;
      setRoadmap(newRoadmap);
      setShowGenerator(false);
      
      const roadmapsRes = await apiClient.get("/roadmaps");
      setRoadmaps(roadmapsRes.data || []);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 
        "Roadmap generation failed. Ensure your resume has parsed details."
      );
    } finally {
      setGenerating(false);
    }
  };

  const handleDeleteRoadmap = async (e: React.MouseEvent, roadmapId: string) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this career roadmap? This action cannot be undone.")) {
      return;
    }
    try {
      await apiClient.delete(`/roadmaps/${roadmapId}`);
      const roadmapsRes = await apiClient.get("/roadmaps");
      const savedRoadmaps = roadmapsRes.data || [];
      setRoadmaps(savedRoadmaps);
      if (roadmap?.id === roadmapId) {
        if (savedRoadmaps.length > 0) {
          setRoadmap(savedRoadmaps[0]);
        } else {
          setRoadmap(null);
          setShowGenerator(true);
        }
      }
    } catch (err: any) {
      setError("Failed to delete the roadmap.");
    }
  };

  const handleToggleTaskStatus = async (task: RoadmapTask) => {
    setUpdatingTaskId(task.id);
    const newStatus = task.status === "completed" ? "pending" : "completed";
    try {
      const response = await apiClient.patch(`/roadmaps/tasks/${task.id}?status=${newStatus}`);
      
      if (roadmap) {
        const updatedTasks = roadmap.tasks.map((t) => 
          t.id === task.id ? { ...t, status: response.data.status } : t
        );
        setRoadmap({ ...roadmap, tasks: updatedTasks });
        
        setRoadmaps(prevRoadmaps => prevRoadmaps.map(r => 
          r.id === roadmap.id ? { ...r, tasks: updatedTasks } : r
        ));
      }
    } catch (err) {
      // Safe fail
    } finally {
      setUpdatingTaskId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-purple-500" />
          <p className="text-gray-400 text-sm">Compiling learning pathways...</p>
        </div>
      </div>
    );
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-3xl border border-white/5 bg-[#0a0a0c]/40 p-6 backdrop-blur-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="font-heading font-bold text-2xl text-white">Career Roadmaps</h2>
          <p className="text-gray-400 text-xs mt-1">Develop key skill milestones to unlock your targeted career transition path.</p>
        </div>
        <button
          onClick={() => {
            setRoadmap(null);
            setShowGenerator(true);
            setError(null);
          }}
          className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-500 px-4 py-2.5 rounded-xl text-white text-xs font-semibold transition-all duration-300 shadow-[0_0_15px_rgba(168,85,247,0.3)]"
        >
          <Plus className="h-4 w-4" />
          <span>New Roadmap</span>
        </button>
      </div>

      {error && (
        <motion.div initial={{ y: -10, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="p-4 bg-yellow-500/10 border border-yellow-500/25 rounded-2xl flex items-start space-x-3 text-yellow-400 text-sm">
          <AlertCircle className="h-5 w-5 flex-shrink-0" />
          <span>{error}</span>
        </motion.div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Left Side: Saved Roadmaps List */}
        <div className="glass-card rounded-3xl p-6 space-y-6 h-fit lg:col-span-1">
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Your saved roadmaps</h3>
          <div className="space-y-3">
            {roadmaps.length === 0 ? (
              <p className="text-xs text-gray-500">No roadmaps generated yet.</p>
            ) : (
              roadmaps.map((r, i) => {
                const isSelected = roadmap?.id === r.id;
                const completedCount = r.tasks.filter(t => t.status === "completed").length;
                const progressPercentage = r.tasks.length > 0 ? (completedCount / r.tasks.length) * 100 : 0;
                
                return (
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    key={r.id}
                    onClick={() => {
                      setRoadmap(r);
                      setShowGenerator(false);
                      setError(null);
                    }}
                    className={`p-3.5 rounded-2xl border transition-all duration-300 cursor-pointer ${
                      isSelected 
                        ? "bg-purple-500/10 border-purple-500/35 text-purple-300 shadow-[0_0_15px_rgba(168,85,247,0.1)]" 
                        : "bg-white/[0.01] border-white/5 hover:border-white/15 hover:bg-white/[0.02]"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="overflow-hidden flex-1">
                        <h4 className="text-xs font-semibold text-white truncate">{r.title}</h4>
                        <p className="text-[10px] text-gray-500 font-mono mt-1 uppercase tracking-wider">{r.target_role}</p>
                      </div>
                      <button
                        onClick={(e) => handleDeleteRoadmap(e, r.id)}
                        className="p-1.5 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg hover:bg-red-500/20 hover:text-red-300 transition-colors flex-shrink-0"
                        title="Delete Roadmap"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    </div>
                    
                    <div className="flex items-center justify-between mt-3 text-[10px] text-gray-400 font-mono">
                      <span>Progress</span>
                      <span>{completedCount} / {r.tasks.length} Done</span>
                    </div>
                    <div className="w-full bg-white/5 h-[3px] rounded-full mt-1.5 overflow-hidden">
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${progressPercentage}%` }}
                        transition={{ duration: 0.5 }}
                        className="bg-purple-500 h-full rounded-full"
                      />
                    </div>
                  </motion.div>
                );
              })
            )}
          </div>
        </div>

        {/* Right Side: Detail Page or Generator */}
        <div className="lg:col-span-3 space-y-6">
          <AnimatePresence mode="wait">
            {generating ? (
              <motion.div 
                key="generating"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="glass-card rounded-3xl p-12 flex flex-col items-center justify-center py-20 space-y-4"
              >
                <Loader2 className="h-8 w-8 animate-spin text-purple-500" />
                <div className="text-center space-y-1">
                  <h4 className="text-sm font-semibold text-white">AI Engine Structuring Roadmap...</h4>
                  <p className="text-xs text-gray-500">Evaluating gap lists and designing milestone sequences.</p>
                </div>
              </motion.div>
            ) : showGenerator ? (
              <motion.div 
                key="generator"
                initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                className="glass-card rounded-3xl p-8 space-y-8"
              >
                <div className="border-b border-white/5 pb-4">
                  <h3 className="font-heading font-bold text-lg text-white">Transition Pathway Generator</h3>
                  <p className="text-xs text-gray-400 mt-1">Select your resume profile and targeted career goal role to proceed.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Active Resume Profile</label>
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
                            {res.filename} ({(res.file_size / (1024 * 1024)).toFixed(2)} MB)
                          </option>
                        ))
                      )}
                    </select>
                  </div>

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

                    {selectedRole === "Custom" && (
                      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mt-2">
                        <input
                          type="text"
                          placeholder="e.g. Sales Director, Nurse, Financial Advisor"
                          value={customRoleText}
                          onChange={(e) => setCustomRoleText(e.target.value)}
                          className="w-full bg-[#0a0a0c] border border-white/10 rounded-xl px-4 py-3 text-xs text-gray-300 outline-none focus:border-purple-500/30 transition-colors"
                        />
                      </motion.div>
                    )}
                  </div>
                </div>

                <div className="flex justify-end pt-4">
                  <button
                    onClick={handleGenerateRoadmap}
                    disabled={generating}
                    className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-500 px-6 py-3 rounded-xl text-white text-xs font-semibold transition-all duration-300 disabled:opacity-50 shadow-[0_0_15px_rgba(168,85,247,0.3)]"
                  >
                    <Sparkles className="h-4 w-4 text-purple-300" />
                    <span>Generate AI Roadmap</span>
                  </button>
                </div>
              </motion.div>
            ) : roadmap ? (
              <motion.div 
                key="details"
                initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                className="grid grid-cols-1 md:grid-cols-3 gap-6"
              >
                <div className="glass-card rounded-3xl p-6 space-y-6 h-fit md:col-span-1">
                  <div className="space-y-1">
                    <span className="text-[10px] text-purple-400 font-mono tracking-widest uppercase">Active Track</span>
                    <h3 className="font-heading font-bold text-xl text-white">{roadmap.title}</h3>
                    <div className="flex items-center space-x-1.5 mt-2 text-[10px] text-gray-500 font-mono">
                      <Calendar className="h-3 w-3" />
                      <span>Created: {new Date(roadmap.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  
                  {/* Circular progress display */}
                  <div className="flex items-center space-x-4 border-t border-white/5 pt-4">
                     <div className="w-12 h-12 rounded-full border-4 border-purple-500/20 flex items-center justify-center relative">
                        <motion.svg className="absolute inset-0 w-full h-full -rotate-90">
                           <motion.circle 
                              cx="24" cy="24" r="20" stroke="currentColor" strokeWidth="4" fill="transparent" 
                              className="text-purple-500"
                              strokeDasharray="125"
                              initial={{ strokeDashoffset: 125 }}
                              animate={{ strokeDashoffset: 125 - (125 * (roadmap.tasks.filter(t => t.status === "completed").length / (roadmap.tasks.length || 1))) }}
                              transition={{ duration: 1 }}
                           />
                        </motion.svg>
                        <span className="text-[10px] font-bold text-white">
                           {Math.round((roadmap.tasks.filter(t => t.status === "completed").length / (roadmap.tasks.length || 1)) * 100)}%
                        </span>
                     </div>
                     <div className="text-xs text-gray-400">Overall Progress</div>
                  </div>

                  <p className="text-xs text-gray-400 leading-relaxed border-t border-white/5 pt-4">
                    {roadmap.description}
                  </p>
                  <div className="flex items-center space-x-2 p-3 bg-purple-500/5 border border-purple-500/10 rounded-2xl text-purple-300 text-[10px]">
                    <ShieldCheck className="h-4 w-4 flex-shrink-0 text-purple-400" />
                    <span>Mark items completed as you learn.</span>
                  </div>
                </div>

                <div className="md:col-span-2 space-y-6">
                  <div className="glass-card rounded-3xl p-8 space-y-8">
                    <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Milestone Learning Path</h3>
                    
                    <div className="relative border-l border-white/10 pl-6 space-y-8">
                      {roadmap.tasks.map((task, index) => {
                        const isCompleted = task.status === "completed";
                        const isUpdating = updatingTaskId === task.id;
                        
                        let cleanDesc = task.description || "";
                        let displayMilestoneTitle = null;
                        if (cleanDesc.startsWith("Milestone: ")) {
                          const parts = cleanDesc.split("\n\n", 2);
                          if (parts.length === 2) {
                            displayMilestoneTitle = parts[0].replace("Milestone: ", "");
                            cleanDesc = parts[1];
                          }
                        }

                        let resources: string[] = [];
                        if (cleanDesc.includes("||RESOURCES||")) {
                          const parts = cleanDesc.split("||RESOURCES||");
                          cleanDesc = parts[0].trim();
                          try {
                            resources = JSON.parse(parts[1]);
                          } catch (e) {
                            console.error("Failed to parse task resources", e);
                          }
                        }

                        if (!resources || resources.length === 0) {
                          const searchQuery = encodeURIComponent(`${roadmap.target_role} ${task.title}`);
                          resources = [
                            `https://www.youtube.com/results?search_query=${searchQuery}`,
                            `https://www.google.com/search?q=${searchQuery}`
                          ];
                        }

                        return (
                          <motion.div 
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                            key={task.id} 
                            className="relative group"
                          >
                            <div className="absolute left-[-34px] top-1.5 h-5 w-5 flex items-center justify-center">
                              {isUpdating ? (
                                <Loader2 className="h-4 w-4 animate-spin text-purple-400" />
                              ) : (
                                <button 
                                  onClick={() => handleToggleTaskStatus(task)}
                                  className="focus:outline-none transition-transform hover:scale-110"
                                >
                                  {isCompleted ? (
                                    <CheckCircle2 className="h-5 w-5 text-purple-500 fill-[#030303]" />
                                  ) : (
                                    <Circle className="h-5 w-5 text-gray-600 hover:text-purple-400 fill-[#030303]" />
                                  )}
                                </button>
                              )}
                            </div>

                            <div className={`p-4 bg-white/[0.01] border rounded-2xl space-y-2 transition-all duration-300 ${
                              isCompleted ? 'border-purple-500/20 bg-purple-500/5' : 'border-white/5 hover:bg-white/[0.02]'
                            }`}>
                              {displayMilestoneTitle && (
                                <span className="text-[10px] font-semibold text-purple-400 uppercase tracking-wider">
                                  {displayMilestoneTitle}
                                </span>
                              )}
                              <div className="flex items-center justify-between">
                                <span className="text-[10px] font-mono text-gray-500">STEP {task.sequence}</span>
                                <span className={`text-[9px] font-mono tracking-wider px-2 py-0.5 rounded-full transition-colors ${
                                  isCompleted 
                                    ? "bg-green-500/10 text-green-400" 
                                    : "bg-yellow-500/5 text-yellow-500"
                                }`}>
                                  {task.status.toUpperCase()}
                                </span>
                              </div>
                              <h4 className={`font-heading font-semibold text-xs transition-colors ${isCompleted ? "text-gray-400 line-through" : "text-white"}`}>
                                {task.title}
                              </h4>
                              <p className="text-xs text-gray-500 leading-relaxed">
                                {cleanDesc}
                              </p>

                              {resources && resources.length > 0 && (
                                <div className="pt-3 border-t border-white/5 space-y-2">
                                  <span className="text-[10px] text-purple-400 font-mono tracking-wider uppercase block">📚 Learning Resources:</span>
                                  <div className="flex flex-wrap gap-2">
                                    {resources.map((url, i) => {
                                      const isYoutube = url.includes("youtube.com") || url.includes("youtu.be");
                                      let friendlyTitle = "Study Guide";
                                      if (isYoutube) friendlyTitle = "YouTube Tutorial";
                                      else if (url.includes("wikipedia.org")) friendlyTitle = "Wikipedia Guide";
                                      else if (url.includes("docs") || url.includes("tutorial") || url.includes("python.org")) friendlyTitle = "Official Docs";
                                      
                                      return (
                                        <a
                                          key={i}
                                          href={url}
                                          target="_blank"
                                          rel="noopener noreferrer"
                                          className="inline-flex items-center space-x-1.5 px-2.5 py-1 bg-white/5 border border-white/5 rounded-lg text-[10px] text-gray-400 hover:text-white hover:bg-purple-600/10 hover:border-purple-500/20 transition-all duration-300"
                                        >
                                          {isYoutube ? (
                                            <Play className="h-3.5 w-3.5 text-red-500 flex-shrink-0" />
                                          ) : (
                                            <ExternalLink className="h-3.5 w-3.5 text-blue-400 flex-shrink-0" />
                                          )}
                                          <span>{friendlyTitle}</span>
                                        </a>
                                      );
                                    })}
                                  </div>
                                </div>
                              )}
                            </div>
                          </motion.div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </motion.div>
            ) : (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card rounded-3xl p-12 text-center text-gray-400">
                <BookOpen className="h-8 w-8 mx-auto text-gray-600 mb-3" />
                <p className="text-sm">Please generate or select a career roadmap.</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  );
};
