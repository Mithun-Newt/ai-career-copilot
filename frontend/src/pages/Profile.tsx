import React, { useState, useEffect } from "react";
import { User, Briefcase, FileText, CheckCircle, Loader2 } from "lucide-react";
import apiClient from "../api/client";
import { User as UserType, Profile as ProfileType } from "../types";

export const Profile: React.FC = () => {
  const [user, setUser] = useState<UserType | null>(null);
  const [profileExists, setProfileExists] = useState(false);
  
  // Form input states
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [title, setTitle] = useState("");
  const [bio, setBio] = useState("");
  const [experienceYears, setExperienceYears] = useState<number>(0);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 1. Fetch current user and profile details
  useEffect(() => {
    const fetchProfileData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const userRes = await apiClient.get<UserType>("/auth/me");
        const currentUser = userRes.data;
        setUser(currentUser);

        try {
          const profileRes = await apiClient.get<ProfileType>(`/profiles/${currentUser.id}`);
          const p = profileRes.data;
          setFirstName(p.first_name || "");
          setLastName(p.last_name || "");
          setTitle(p.title || "");
          setBio(p.bio || "");
          setExperienceYears(p.experience_years || 0);
          setProfileExists(true);
        } catch (pErr) {
          // Profile doesn't exist yet, which is fine
          setProfileExists(false);
        }
      } catch (err: any) {
        setError("Failed to load profile parameters.");
      } finally {
        setLoading(false);
      }
    };

    fetchProfileData();
  }, []);

  // 2. Handle form submission
  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    
    setSaving(true);
    setError(null);
    setSuccess(false);

    const profilePayload = {
      first_name: firstName,
      last_name: lastName,
      title: title,
      bio: bio,
      experience_years: Number(experienceYears),
    };

    try {
      if (profileExists) {
        // Update existing profile
        await apiClient.put(`/profiles/${user.id}`, profilePayload);
      } else {
        // Create new profile (submits user_id as query param or maps inside endpoint)
        await apiClient.post(`/profiles?user_id=${user.id}`, profilePayload);
        setProfileExists(true);
      }
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to update profile settings.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-purple-500" />
          <p className="text-gray-400 text-sm">Loading user account parameters...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Top section banner */}
      <div className="glass-card rounded-2xl p-6 relative overflow-hidden flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="h-12 w-12 bg-purple-500/10 border border-purple-500/20 text-purple-400 rounded-xl flex items-center justify-center">
            <User className="h-6 w-6" />
          </div>
          <div>
            <h2 className="font-heading font-bold text-lg text-white">Profile Workspace</h2>
            <p className="text-xs text-gray-500">{user?.email}</p>
          </div>
        </div>
      </div>

      {success && (
        <div className="p-4 bg-green-500/10 border border-green-500/20 text-green-400 text-sm rounded-xl flex items-center space-x-2">
          <CheckCircle className="h-5 w-5 flex-shrink-0" />
          <span>Profile parameters updated successfully!</span>
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 text-sm rounded-xl">
          {error}
        </div>
      )}

      {/* Profile form */}
      <form onSubmit={handleProfileSubmit} className="glass-card rounded-3xl p-8 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">First Name</label>
            <input
              type="text"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              placeholder="First Name"
              className="w-full px-4 py-3 bg-white/[0.02] border border-white/5 focus:border-purple-500/30 focus:bg-white/[0.04] outline-none rounded-xl text-sm transition-all duration-300 placeholder:text-gray-600 focus:shadow-[0_0_20px_rgba(168,85,247,0.05)]"
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Last Name</label>
            <input
              type="text"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              placeholder="Last Name"
              className="w-full px-4 py-3 bg-white/[0.02] border border-white/5 focus:border-purple-500/30 focus:bg-white/[0.04] outline-none rounded-xl text-sm transition-all duration-300 placeholder:text-gray-600 focus:shadow-[0_0_20px_rgba(168,85,247,0.05)]"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Professional Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Lead Software Architect"
              className="w-full px-4 py-3 bg-white/[0.02] border border-white/5 focus:border-purple-500/30 focus:bg-white/[0.04] outline-none rounded-xl text-sm transition-all duration-300 placeholder:text-gray-600 focus:shadow-[0_0_20px_rgba(168,85,247,0.05)]"
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Years of Experience</label>
            <input
              type="number"
              min="0"
              max="80"
              value={experienceYears}
              onChange={(e) => setExperienceYears(Number(e.target.value))}
              placeholder="e.g. 5"
              className="w-full px-4 py-3 bg-white/[0.02] border border-white/5 focus:border-purple-500/30 focus:bg-white/[0.04] outline-none rounded-xl text-sm transition-all duration-300 placeholder:text-gray-600 focus:shadow-[0_0_20px_rgba(168,85,247,0.05)]"
            />
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Biography Summary</label>
          <textarea
            rows={4}
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            placeholder="Introduce your engineering path, tech stack, and goals..."
            className="w-full px-4 py-3 bg-white/[0.02] border border-white/5 focus:border-purple-500/30 focus:bg-white/[0.04] outline-none rounded-xl text-sm transition-all duration-300 placeholder:text-gray-600 focus:shadow-[0_0_20px_rgba(168,85,247,0.05)] resize-none"
          />
        </div>

        <button
          type="submit"
          disabled={saving}
          className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-500 px-6 py-3 border border-purple-500/30 rounded-xl text-white font-medium text-sm transition-all duration-300 cursor-pointer disabled:opacity-50"
        >
          {saving && <Loader2 className="h-4 w-4 animate-spin" />}
          <span>Save Changes</span>
        </button>
      </form>
    </div>
  );
};
