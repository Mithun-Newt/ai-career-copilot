import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Compass, Mail, Lock, Loader2, ArrowRight } from "lucide-react";
import apiClient from "../api/client";

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.post("/auth/login", {
        email,
        password,
      });

      // Save token to local storage
      localStorage.setItem("access_token", response.data.access_token);
      
      // Navigate to dashboard
      navigate("/dashboard");
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 
        "Authentication failed. Please verify credentials."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-[#030303] text-gray-100 flex items-center justify-center p-6 overflow-hidden">
      {/* Background glow meshes */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-purple-500/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-cyan-500/5 blur-[120px] pointer-events-none" />

      {/* Main card panel */}
      <div className="w-full max-w-md glass-card rounded-3xl p-8 md:p-10 relative overflow-hidden">
        {/* Glowing top accent border */}
        <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-purple-500/40 to-transparent" />

        {/* Brand logo header */}
        <div className="flex flex-col items-center mb-8">
          <div className="p-3 bg-purple-500/10 border border-purple-500/20 rounded-2xl mb-4">
            <Compass className="h-8 w-8 text-purple-400 animate-spin-slow" />
          </div>
          <h2 className="font-heading font-bold text-2xl text-white">Welcome Back</h2>
          <p className="text-gray-400 text-sm mt-2">Log in to your AI Career Copilot account</p>
        </div>

        {/* Error notification */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 text-red-400 text-sm rounded-xl">
            {error}
          </div>
        )}

        {/* Form controls */}
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Email Address</label>
            <div className="relative flex items-center">
              <Mail className="absolute left-4 h-5 w-5 text-gray-500" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full pl-12 pr-4 py-3.5 bg-white/[0.02] border border-white/5 focus:border-purple-500/30 focus:bg-white/[0.04] outline-none rounded-xl text-sm transition-all duration-300 placeholder:text-gray-600 focus:shadow-[0_0_20px_rgba(168,85,247,0.05)]"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Password</label>
            <div className="relative flex items-center">
              <Lock className="absolute left-4 h-5 w-5 text-gray-500" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-12 pr-4 py-3.5 bg-white/[0.02] border border-white/5 focus:border-purple-500/30 focus:bg-white/[0.04] outline-none rounded-xl text-sm transition-all duration-300 placeholder:text-gray-600 focus:shadow-[0_0_20px_rgba(168,85,247,0.05)]"
              />
            </div>
          </div>

          {/* Action button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center space-x-2 py-3.5 bg-purple-600 hover:bg-purple-500 border border-purple-500/30 rounded-xl text-white font-medium text-sm transition-all duration-300 focus:shadow-[0_0_30px_rgba(168,85,247,0.3)] disabled:opacity-50"
          >
            {loading ? (
              <Loader2 className="h-5 w-5 animate-spin text-white" />
            ) : (
              <>
                <span>Secure Log In</span>
                <ArrowRight className="h-4 w-4" />
              </>
            )}
          </button>
        </form>

        {/* Link back */}
        <div className="mt-8 text-center text-sm text-gray-500">
          Don't have an account?{" "}
          <Link to="/register" className="text-purple-400 hover:text-purple-300 font-medium">
            Register Here
          </Link>
        </div>
      </div>
    </div>
  );
};
