import React, { useState, useEffect } from "react";
import { 
  FileUp, 
  Upload, 
  CheckCircle, 
  Loader2, 
  AlertCircle, 
  FileText, 
  Mail, 
  Phone, 
  User as UserIcon,
  BookOpen,
  Briefcase,
  Layers,
  Trash2,
  Check
} from "lucide-react";
import apiClient from "../api/client";
import { Resume } from "../types";

export const ResumeUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [parsedData, setParsedData] = useState<Resume | null>(null);
  const [uploadedResumes, setUploadedResumes] = useState<Resume[]>([]);

  const fetchResumes = async () => {
    try {
      const response = await apiClient.get("/resumes/my-resumes");
      setUploadedResumes(response.data.resumes || []);
    } catch (err) {
      console.error("Failed to fetch resumes", err);
    }
  };

  useEffect(() => {
    fetchResumes();
  }, []);

  const handleDeleteResume = async (resumeId: string) => {
    if (!window.confirm("Are you sure you want to delete this resume? This action cannot be undone.")) {
      return;
    }
    try {
      await apiClient.delete(`/resumes/${resumeId}`);
      fetchResumes();
      if (parsedData && parsedData.id === resumeId) {
        setParsedData(null);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to delete the resume.");
    }
  };

  const handleActivateResume = async (resumeId: string) => {
    try {
      await apiClient.put(`/resumes/${resumeId}/activate`);
      fetchResumes();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to activate the selected resume.");
    }
  };

  // 1. Drag handlers
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  // 2. Validate format and size
  const validateAndSetFile = (selectedFile: File) => {
    setError(null);
    const suffix = selectedFile.name.split(".").pop()?.toLowerCase();
    if (suffix !== "pdf" && suffix !== "docx") {
      setError("Unsupported format. Only PDF and DOCX documents can be parsed.");
      setFile(null);
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setError("File exceeds maximum size limit of 10 MB.");
      setFile(null);
      return;
    }

    setFile(selectedFile);
  };

  // 3. Perform upload request
  const handleUploadSubmit = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    setProgress(10);

    const formData = new FormData();
    formData.append("file", file);

    // Simulate upload progress
    const progressInterval = setInterval(() => {
      setProgress((prev) => (prev < 80 ? prev + 15 : prev));
    }, 250);

    try {
      const response = await apiClient.post("/resumes/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      clearInterval(progressInterval);
      setProgress(100);
      
      // Save parsed data from response
      setParsedData(response.data);
      fetchResumes();
    } catch (err: any) {
      clearInterval(progressInterval);
      setError(err.response?.data?.detail || "Upload process failed. Verify resume integrity.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Upload layout panel */}
      <div className="glass-card rounded-3xl p-8 relative overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-purple-500/20 to-transparent" />
        
        <div className="max-w-xl mx-auto text-center space-y-6">
          <div className="space-y-2">
            <h2 className="font-heading font-bold text-2xl text-white">Upload Resume</h2>
            <p className="text-gray-400 text-sm">
              Drag and drop your PDF or DOCX resume to extract skills and compile gap analysis.
            </p>
          </div>

          {/* Drag & drop box */}
          <div
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            className={`relative border border-dashed rounded-2xl p-10 transition-all duration-300 ${
              dragActive 
                ? "border-purple-500 bg-purple-500/5 shadow-[0_0_20px_rgba(168,85,247,0.05)]" 
                : "border-white/10 hover:border-white/20 bg-white/[0.01]"
            }`}
          >
            <input
              type="file"
              id="file-upload"
              accept=".pdf,.docx"
              onChange={handleChange}
              className="hidden"
            />
            
            <div className="flex flex-col items-center space-y-4">
              <div className="p-4 bg-purple-500/10 border border-purple-500/20 rounded-2xl">
                <FileUp className="h-8 w-8 text-purple-400" />
              </div>
              <div className="space-y-1">
                <label 
                  htmlFor="file-upload"
                  className="font-medium text-purple-400 hover:text-purple-300 cursor-pointer text-sm"
                >
                  Click to select file
                </label>
                <span className="text-gray-500 text-xs block">or drag and drop here</span>
              </div>
              <span className="text-gray-600 text-xs font-mono uppercase tracking-wider">PDF, DOCX up to 10MB</span>
            </div>

            {file && (
              <div className="mt-6 p-3 bg-white/5 border border-white/10 rounded-xl flex items-center justify-between text-left">
                <div className="flex items-center space-x-3 overflow-hidden">
                  <FileText className="h-5 w-5 text-purple-400 flex-shrink-0" />
                  <span className="text-sm font-medium truncate text-gray-200">{file.name}</span>
                </div>
                <span className="text-xs text-gray-500 font-mono ml-4 flex-shrink-0">
                  {(file.size / (1024 * 1024)).toFixed(2)} MB
                </span>
              </div>
            )}
          </div>

          {/* Progress bar */}
          {uploading && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs font-mono text-gray-500">
                <span>PARSING RESUME FIELDS...</span>
                <span>{progress}%</span>
              </div>
              <div className="w-full bg-white/5 rounded-full h-1.5 overflow-hidden">
                <div 
                  className="bg-purple-500 h-1.5 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          {/* Error display */}
          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-start space-x-3 text-left text-red-400 text-sm">
              <AlertCircle className="h-5 w-5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Submit Action */}
          {file && !uploading && (
            <button
              onClick={handleUploadSubmit}
              className="w-full flex items-center justify-center space-x-2 py-3 bg-purple-600 hover:bg-purple-500 border border-purple-500/30 rounded-xl text-white font-medium text-sm transition-all duration-300"
            >
              <Upload className="h-4 w-4" />
              <span>Upload and Parse Resume</span>
            </button>
          )}
        </div>
      </div>

      {/* Structured parsed results display */}
      {parsedData?.parsed_data && (
        <div className="space-y-8 animate-fade-in">
          {/* Header banner */}
          <div className="flex items-center space-x-3 p-4 bg-green-500/10 border border-green-500/20 rounded-2xl text-green-400">
            <CheckCircle className="h-5 w-5 flex-shrink-0" />
            <span className="text-sm font-medium">Resume successfully parsed & registered! Check structured details below.</span>
          </div>

          {/* Contact and Bio grid cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="glass-card rounded-2xl p-6 space-y-4">
              <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider flex items-center space-x-2">
                <UserIcon className="h-4 w-4 text-purple-400" />
                <span>Candidate Details</span>
              </h3>
              <div className="space-y-3 pt-2">
                <div>
                  <label className="text-[10px] uppercase text-gray-500 tracking-wider">Extracted Name</label>
                  <div className="text-white text-sm font-medium">{parsedData.parsed_data.name}</div>
                </div>
                <div>
                  <label className="text-[10px] uppercase text-gray-500 tracking-wider">Email Address</label>
                  <div className="text-white text-sm font-medium flex items-center space-x-1.5">
                    <Mail className="h-3.5 w-3.5 text-gray-500" />
                    <span>{parsedData.parsed_data.email}</span>
                  </div>
                </div>
                <div>
                  <label className="text-[10px] uppercase text-gray-500 tracking-wider">Contact Phone</label>
                  <div className="text-white text-sm font-medium flex items-center space-x-1.5">
                    <Phone className="h-3.5 w-3.5 text-gray-500" />
                    <span>{parsedData.parsed_data.phone}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Skills checklist */}
            <div className="glass-card rounded-2xl p-6 space-y-4 md:col-span-2">
              <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider flex items-center space-x-2">
                <Layers className="h-4 w-4 text-purple-400" />
                <span>Extracted Skill Tags</span>
              </h3>
              <div className="flex flex-wrap gap-2 pt-2">
                {parsedData.parsed_data.skills && parsedData.parsed_data.skills.length > 0 ? (
                  parsedData.parsed_data.skills.map((skill, index) => (
                    <span 
                      key={index} 
                      className="px-3 py-1.5 bg-purple-500/10 border border-purple-500/20 text-purple-300 text-xs rounded-xl font-medium"
                    >
                      {skill}
                    </span>
                  ))
                ) : (
                  <span className="text-gray-500 text-xs">No skill tags matched in the master directory catalog.</span>
                )}
              </div>
            </div>
          </div>

          {/* Education & Experience Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Experience timeline */}
            <div className="glass-card rounded-2xl p-6 space-y-4">
              <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider flex items-center space-x-2">
                <Briefcase className="h-4 w-4 text-purple-400" />
                <span>Professional Experience</span>
              </h3>
              <div className="space-y-4 pt-2">
                {parsedData.parsed_data.experience && parsedData.parsed_data.experience.length > 0 ? (
                  parsedData.parsed_data.experience.map((exp, idx) => (
                    <div key={idx} className="relative pl-4 border-l border-white/5 space-y-1">
                      <div className="absolute left-[-4.5px] top-1.5 h-2 w-2 rounded-full bg-purple-500/40" />
                      <p className="text-gray-300 text-xs leading-relaxed">{exp}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 text-xs">No job history parsed.</p>
                )}
              </div>
            </div>

            {/* Education timeline */}
            <div className="glass-card rounded-2xl p-6 space-y-4">
              <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider flex items-center space-x-2">
                <BookOpen className="h-4 w-4 text-purple-400" />
                <span>Education History</span>
              </h3>
              <div className="space-y-4 pt-2">
                {parsedData.parsed_data.education && parsedData.parsed_data.education.length > 0 ? (
                  parsedData.parsed_data.education.map((edu, idx) => (
                    <div key={idx} className="relative pl-4 border-l border-white/5 space-y-1">
                      <div className="absolute left-[-4.5px] top-1.5 h-2 w-2 rounded-full bg-purple-500/40" />
                      <p className="text-gray-300 text-xs leading-relaxed">{edu}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 text-xs">No academic credentials parsed.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* List of uploaded resumes */}
      <div className="glass-card rounded-3xl p-8 space-y-6">
        <div className="border-b border-white/5 pb-4">
          <h3 className="font-heading font-bold text-lg text-white">Your Uploaded Resumes</h3>
          <p className="text-xs text-gray-400 mt-1">Manage resumes uploaded to this account.</p>
        </div>

        {uploadedResumes.length === 0 ? (
          <p className="text-xs text-gray-500">No resumes uploaded yet. Upload one above to get started.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {uploadedResumes.map((res) => (
              <div 
                key={res.id} 
                className={`p-4 rounded-2xl flex items-center justify-between transition-all duration-300 border ${
                  res.is_active 
                    ? "bg-purple-500/[0.03] border-purple-500/20 shadow-[0_0_15px_rgba(168,85,247,0.02)]" 
                    : "bg-white/[0.01] border-white/5 hover:border-white/15 hover:bg-white/[0.02]"
                }`}
              >
                <div 
                  onClick={() => setParsedData(res)} 
                  className="flex items-center space-x-3 overflow-hidden cursor-pointer flex-1"
                >
                  <FileText className="h-6 w-6 text-purple-400 flex-shrink-0" />
                  <div className="overflow-hidden space-y-0.5">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-semibold text-gray-200 truncate">{res.filename}</span>
                      {res.is_active && (
                        <span className="px-1.5 py-0.5 bg-green-500/10 border border-green-500/20 text-green-400 text-[8px] rounded font-mono uppercase tracking-wider font-bold">Active</span>
                      )}
                    </div>
                    <span className="text-[10px] text-gray-500 font-mono block">
                      {(res.file_size / (1024 * 1024)).toFixed(2)} MB • {new Date(res.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <div className="flex items-center">
                  {!res.is_active && (
                    <button
                      onClick={() => handleActivateResume(res.id)}
                      className="p-2 bg-purple-500/10 border border-purple-500/20 text-purple-400 rounded-xl hover:bg-purple-500/20 hover:text-purple-300 transition-colors ml-2"
                      title="Set as Active Resume"
                    >
                      <Check className="h-4 w-4" />
                    </button>
                  )}

                  <button
                    onClick={() => handleDeleteResume(res.id)}
                    className="p-2 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl hover:bg-red-500/20 hover:text-red-300 transition-colors ml-2"
                    title="Delete Resume"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
