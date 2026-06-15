import React, { useState, useEffect, useRef } from "react";
import { 
  MessageSquare, 
  Send, 
  Sparkles, 
  Plus, 
  Trash2, 
  User, 
  Bot, 
  Loader2, 
  AlertCircle,
  ArrowRight,
  MessageCircle
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import apiClient from "../api/client";
import { ChatMessage, ChatSession } from "../types";

const SUGGESTED_PROMPTS = [
  "Can you review my recent ATS score?",
  "What skills am I missing for a Data Scientist role?",
  "Help me prepare for an AI Engineer interview.",
  "Which roadmap tasks should I prioritize first?"
];

export const CareerCoach: React.FC = () => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSession, setActiveSession] = useState<ChatSession | null>(null);
  
  const [messageText, setMessageText] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [aiProvider, setAiProvider] = useState("Resolving AI Model...");
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchDebugInfo = async () => {
      try {
        const res = await apiClient.get("/career/debug");
        if (res.data && res.data.provider) {
          const names: Record<string, string> = {
            google: "Google Gemini",
            openai: "OpenAI GPT",
            groq: "Groq Llama",
            none: "Mock/Offline Mode"
          };
          setAiProvider(names[res.data.provider] || res.data.provider);
        }
      } catch (err) {
        setAiProvider("Mock/Offline Mode");
      }
    };
    fetchDebugInfo();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [activeSession?.messages, submitting]);

  const fetchSessions = async (selectLatest = true) => {
    try {
      setLoading(true);
      setError(null);
      const res = await apiClient.get<ChatSession[]>("/career/chat");
      const list = res.data || [];
      setSessions(list);
      
      if (selectLatest && list.length > 0) {
        const sessionRes = await apiClient.get<ChatSession>(`/career/chat/${list[0].id}`);
        setActiveSession(sessionRes.data);
      }
    } catch (err: any) {
      setError("Failed to compile chat session history. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  const handleSelectSession = async (session: ChatSession) => {
    setError(null);
    try {
      setSubmitting(true);
      const res = await apiClient.get<ChatSession>(`/career/chat/${session.id}`);
      setActiveSession(res.data);
    } catch (err: any) {
      setError("Failed to load conversation thread.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleNewSession = () => {
    setActiveSession(null);
    setMessageText("");
    setError(null);
  };

  const handleDeleteSession = async (e: React.MouseEvent, session: ChatSession) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this chat thread?")) return;
    
    try {
      await apiClient.delete(`/career/chat/${session.id}`);
      if (activeSession?.id === session.id) {
        setActiveSession(null);
      }
      fetchSessions(false);
    } catch (err: any) {
      setError("Failed to delete chat thread.");
    }
  };

  const sendText = async (text: string) => {
    if (!text.trim() || submitting) return;

    setMessageText("");
    setSubmitting(true);
    setError(null);

    const tempUserMsg: ChatMessage = {
      id: Math.random().toString(),
      role: "user",
      content: text,
      created_at: new Date().toISOString()
    };

    if (activeSession) {
      setActiveSession({
        ...activeSession,
        messages: [...activeSession.messages, tempUserMsg]
      });
    } else {
      setActiveSession({
        id: "temp",
        title: text.slice(0, 40),
        created_at: new Date().toISOString(),
        messages: [tempUserMsg]
      });
    }

    try {
      const response = await apiClient.post("/career/chat", {
        message: text,
        chat_id: activeSession && activeSession.id !== "temp" ? activeSession.id : null
      });

      const { chat_id: returnedChatId } = response.data;
      const sessionRes = await apiClient.get<ChatSession>(`/career/chat/${returnedChatId}`);
      setActiveSession(sessionRes.data);

      const listRes = await apiClient.get<ChatSession[]>("/career/chat");
      setSessions(listRes.data || []);
    } catch (err: any) {
      setError("AI Response failed. Please verify system connection.");
      if (activeSession) {
        setActiveSession({
          ...activeSession,
          messages: activeSession.messages.filter(m => m.id !== tempUserMsg.id)
        });
      } else {
        setActiveSession(null);
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    sendText(messageText);
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
      {/* Welcome Coach Header */}
      <div className="relative overflow-hidden rounded-3xl border border-white/5 bg-[#0a0a0c]/40 p-6 backdrop-blur-xl">
        <div className="absolute top-0 right-0 w-[30%] h-[100%] bg-gradient-to-l from-purple-500/5 to-transparent blur-[50px] pointer-events-none" />
        <div className="max-w-2xl relative space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <div className="inline-flex items-center space-x-2 px-3 py-1 bg-purple-500/10 border border-purple-500/20 rounded-full text-xs text-purple-300">
              <Sparkles className="h-3 w-3 text-purple-400" />
              <span>Encouraging AI Mentor Engaged</span>
            </div>
            <div className="inline-flex items-center space-x-1.5 px-3 py-1 bg-white/5 border border-white/10 rounded-full text-xs text-gray-400">
              <span className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
              <span>Active Model: {aiProvider}</span>
            </div>
          </div>
          <h2 className="font-heading font-bold text-2xl text-white">AI Career Coach</h2>
          <p className="text-gray-400 text-xs mt-1">
            Ask transition questions, request learning strategies, or receive feedback aligned with your profile and roadmaps.
          </p>
        </div>
      </div>

      {error && (
        <motion.div initial={{ y: -10, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="p-4 bg-yellow-500/10 border border-yellow-500/25 rounded-2xl flex items-start space-x-3 text-yellow-400 text-sm">
          <AlertCircle className="h-5 w-5 flex-shrink-0" />
          <span>{error}</span>
        </motion.div>
      )}

      {/* Main Workspace Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 min-h-[60vh] h-[65vh]">
        {/* Left Column: Saved Sessions List */}
        <div className="glass-card rounded-3xl p-6 flex flex-col justify-between lg:col-span-1 h-full overflow-hidden">
          <div className="space-y-6 flex-1 flex flex-col overflow-hidden">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Coach Sessions</h3>
              <button
                onClick={handleNewSession}
                className="p-1.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-gray-400 hover:text-white transition-all duration-300"
                title="New Chat Session"
              >
                <Plus className="h-4 w-4" />
              </button>
            </div>

            {/* Scrollable list */}
            <div className="flex-1 overflow-y-auto space-y-2 pr-1.5">
              {loading && sessions.length === 0 ? (
                <div className="flex justify-center py-6">
                  <Loader2 className="h-5 w-5 animate-spin text-purple-500" />
                </div>
              ) : sessions.length === 0 ? (
                <p className="text-xs text-gray-500">No previous sessions.</p>
              ) : (
                <AnimatePresence>
                  {sessions.map((s, i) => {
                    const isActive = activeSession?.id === s.id;
                    return (
                      <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        transition={{ delay: i * 0.05 }}
                        key={s.id}
                        onClick={() => handleSelectSession(s)}
                        className={`flex items-center justify-between p-3 rounded-2xl border transition-all duration-300 cursor-pointer ${
                          isActive 
                            ? "bg-purple-500/10 border-purple-500/35 text-purple-300 shadow-[0_0_15px_rgba(168,85,247,0.1)]" 
                            : "bg-white/[0.01] border-white/5 hover:border-white/15 hover:bg-white/[0.02]"
                        }`}
                      >
                        <div className="flex items-center space-x-2.5 min-w-0 flex-1">
                          <MessageSquare className={`h-4 w-4 flex-shrink-0 ${isActive ? "text-purple-400" : "text-gray-500"}`} />
                          <span className="text-xs font-medium text-white truncate">{s.title}</span>
                        </div>
                        <button
                          onClick={(e) => handleDeleteSession(e, s)}
                          className="p-1 text-gray-500 hover:text-red-400 rounded-lg hover:bg-red-500/5 transition-all duration-300 ml-1.5"
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
        </div>

        {/* Right Column: Chat Window Feed */}
        <div className="lg:col-span-3 glass-card rounded-3xl p-6 flex flex-col justify-between h-full overflow-hidden">
          {/* Messages Feed View */}
          <div className="flex-1 overflow-y-auto space-y-6 pr-2 mb-6">
            {!activeSession ? (
              <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="h-full flex flex-col items-center justify-center text-center max-w-xl mx-auto space-y-6">
                <div className="p-4 bg-purple-500/10 border border-purple-500/25 rounded-3xl">
                  <Bot className="h-10 w-10 text-purple-400 animate-pulse" />
                </div>
                <div>
                  <h4 className="font-heading font-semibold text-white text-lg">Start a Conversation</h4>
                  <p className="text-sm text-gray-400 mt-2 leading-relaxed">
                    Ask how you can close skill gaps, what roles fit your profile, or build custom learning milestones.
                  </p>
                </div>
                
                {/* Suggested Prompts */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full mt-6">
                  {SUGGESTED_PROMPTS.map((prompt, index) => (
                    <motion.button
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      onClick={() => sendText(prompt)}
                      className="text-left text-xs bg-white/5 hover:bg-white/10 border border-white/10 p-3 rounded-xl text-gray-300 hover:text-white transition-all flex items-center justify-between group"
                    >
                      <span className="truncate mr-2">{prompt}</span>
                      <MessageCircle className="h-3 w-3 text-purple-400 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            ) : (
              <div className="space-y-6">
                <AnimatePresence>
                  {activeSession.messages.map((msg) => {
                    const isUser = msg.role === "user";
                    return (
                      <motion.div 
                        initial={{ opacity: 0, y: 10, scale: 0.98 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        key={msg.id} 
                        className={`flex items-start gap-4 ${isUser ? "flex-row-reverse" : ""}`}
                      >
                        {/* Avatar */}
                        <div className={`p-2 rounded-xl flex-shrink-0 border ${
                          isUser 
                            ? "bg-purple-500/10 border-purple-500/20 text-purple-300" 
                            : "bg-white/5 border-white/10 text-gray-400"
                        }`}>
                          {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                        </div>

                        {/* Content block */}
                        <div className={`max-w-[75%] p-4 rounded-2xl text-xs leading-relaxed ${
                          isUser 
                            ? "bg-purple-600 text-white rounded-tr-none shadow-[0_0_15px_rgba(168,85,247,0.2)]" 
                            : "bg-white/[0.02] border border-white/5 text-gray-300 rounded-tl-none font-sans"
                        }`}>
                          {msg.content.split("\n").map((para, i) => (
                            <p key={i} className={i > 0 ? "mt-2" : ""}>{para}</p>
                          ))}
                        </div>
                      </motion.div>
                    );
                  })}
                </AnimatePresence>

                {/* Submitting typing indicator loader */}
                {submitting && (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-start gap-4">
                    <div className="p-2 bg-white/5 border border-white/10 rounded-xl text-gray-400">
                      <Bot className="h-4 w-4 animate-bounce" />
                    </div>
                    <div className="p-4 bg-white/[0.01] border border-white/5 rounded-2xl rounded-tl-none">
                      <Loader2 className="h-4 w-4 animate-spin text-purple-400" />
                    </div>
                  </motion.div>
                )}
                
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Form Text Area Input */}
          <form onSubmit={handleSendMessage} className="relative flex items-center bg-[#0a0a0c] border border-white/10 rounded-2xl overflow-hidden focus-within:border-purple-500/35 transition-all duration-300 shadow-lg">
            <input
              type="text"
              required={!activeSession}
              value={messageText}
              onChange={(e) => setMessageText(e.target.value)}
              placeholder="Ask the AI Career Coach a question..."
              className="flex-1 bg-transparent px-4 py-3.5 text-xs text-gray-300 outline-none placeholder:text-gray-600 pr-14"
              disabled={submitting}
            />
            <button
              type="submit"
              disabled={submitting || (!messageText.trim() && !activeSession)}
              className="absolute right-2.5 p-2 bg-purple-600 hover:bg-purple-500 rounded-xl text-white transition-all duration-300 disabled:opacity-30 disabled:bg-purple-600/50"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      </div>
    </motion.div>
  );
};
