import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { 
  ArrowUpRight, 
  ShieldAlert, 
  Briefcase, 
  Sparkles,
  Loader2,
  Map,
  CheckCircle2,
  BarChart,
  MessageSquare
} from "lucide-react";
import apiClient from "../api/client";

interface DashboardAnalyticsResponse {
  total_roadmaps: number;
  completed_tasks_percentage: number;
  average_ats_score: number;
  total_career_messages: number;
}

export const Dashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<DashboardAnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await apiClient.get<DashboardAnalyticsResponse>("/analytics/dashboard");
        setAnalytics(res.data);
      } catch (err: any) {
        setError("Failed to compile dashboard metrics. Verify database connections.");
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-purple-500" />
          <p className="text-gray-400 text-sm">Compiling workspace statistics...</p>
        </div>
      </div>
    );
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } }
  };

  return (
    <motion.div 
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-8"
    >
      {/* Welcome banner */}
      <motion.div variants={itemVariants} className="relative overflow-hidden rounded-3xl border border-white/5 bg-[#0a0a0c]/40 p-8 md:p-10 backdrop-blur-xl shadow-lg">
        <div className="absolute top-0 right-0 w-[40%] h-[100%] bg-gradient-to-l from-purple-500/10 to-transparent blur-[60px] pointer-events-none" />
        <div className="max-w-2xl space-y-4 relative">
          <div className="inline-flex items-center space-x-2 px-3 py-1 bg-purple-500/10 border border-purple-500/20 rounded-full text-xs text-purple-300">
            <Sparkles className="h-3 w-3 text-purple-400" />
            <span>AI Career Workspace Engine Active</span>
          </div>
          <h2 className="font-heading font-bold text-3xl md:text-4xl text-white">
            Welcome to your career dashboard
          </h2>
          <p className="text-gray-400 text-sm md:text-base leading-relaxed">
            Manage your resumes, analyze skill gaps, and execute generated learning pathways.
            Use our AI systems to transition into target tech roles.
          </p>
          <div className="flex flex-wrap gap-4 pt-2">
            <Link 
              to="/resume" 
              className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-500 px-5 py-2.5 rounded-xl text-white text-sm font-medium transition-all duration-300 shadow-[0_0_15px_rgba(168,85,247,0.4)]"
            >
              <span>Upload New Resume</span>
              <ArrowUpRight className="h-4 w-4" />
            </Link>
            <Link 
              to="/roadmap" 
              className="flex items-center space-x-2 bg-white/5 hover:bg-white/10 border border-white/10 px-5 py-2.5 rounded-xl text-gray-200 text-sm font-medium transition-all duration-300"
            >
              <span>View Roadmaps</span>
            </Link>
          </div>
        </div>
      </motion.div>

      {error && (
        <motion.div variants={itemVariants} className="p-4 bg-yellow-500/10 border border-yellow-500/25 rounded-2xl flex items-start space-x-3 text-yellow-400 text-sm">
          <ShieldAlert className="h-5 w-5 flex-shrink-0" />
          <span>{error}</span>
        </motion.div>
      )}

      {/* Grid metrics widgets */}
      <motion.div variants={containerVariants} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        
        {/* Roadmaps count */}
        <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 rounded-2xl p-6 relative overflow-hidden flex flex-col justify-between hover:bg-white/10 transition-colors">
          <div>
            <Map className="h-6 w-6 text-indigo-400 mb-4" />
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Total Roadmaps</h3>
            <p className="text-3xl font-heading font-bold text-white mt-2">
              {analytics?.total_roadmaps || 0}
            </p>
          </div>
          <div className="mt-4 text-xs text-gray-500">
            Generated AI Pathways
          </div>
        </motion.div>

        {/* Task completion */}
        <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 rounded-2xl p-6 relative overflow-hidden flex flex-col justify-between hover:bg-white/10 transition-colors">
          <div>
            <CheckCircle2 className="h-6 w-6 text-green-400 mb-4" />
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Tasks Completed</h3>
            <p className="text-3xl font-heading font-bold text-white mt-2">
              {analytics?.completed_tasks_percentage || 0}%
            </p>
          </div>
          <div className="mt-4 text-xs text-gray-500">
            Across all roadmaps
          </div>
          <div className="absolute bottom-0 left-0 h-1 bg-green-500/20 w-full">
            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: `${analytics?.completed_tasks_percentage || 0}%` }}
              transition={{ duration: 1, delay: 0.5 }}
              className="h-full bg-green-500" 
            />
          </div>
        </motion.div>

        {/* ATS Score */}
        <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 rounded-2xl p-6 relative overflow-hidden flex flex-col justify-between hover:bg-white/10 transition-colors">
          <div>
            <BarChart className="h-6 w-6 text-cyan-400 mb-4" />
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Average ATS Score</h3>
            <p className="text-3xl font-heading font-bold text-white mt-2">
              {analytics?.average_ats_score || 0}
            </p>
          </div>
          <div className="mt-4 text-xs text-gray-500">
            Based on uploads
          </div>
        </motion.div>

        {/* Career Messages */}
        <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 rounded-2xl p-6 relative overflow-hidden flex flex-col justify-between hover:bg-white/10 transition-colors">
          <div>
            <MessageSquare className="h-6 w-6 text-pink-400 mb-4" />
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Coach Interactions</h3>
            <p className="text-3xl font-heading font-bold text-white mt-2">
              {analytics?.total_career_messages || 0}
            </p>
          </div>
          <div className="mt-4 text-xs text-gray-500 flex items-center space-x-1.5 text-purple-400 font-medium">
            <Link to="/coach" className="hover:text-purple-300 transition-colors flex items-center space-x-1">
              <span>Chat with Coach</span>
              <ArrowUpRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </motion.div>
      </motion.div>
    </motion.div>
  );
};
