import React from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";

export const Landing: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-900 text-white font-sans overflow-hidden">
      {/* Navbar */}
      <nav className="flex justify-between items-center px-8 py-6 z-10 relative">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-indigo-500 rounded-lg flex items-center justify-center font-bold text-xl">
            C
          </div>
          <span className="text-xl font-semibold tracking-wide">
            Career Copilot
          </span>
        </div>
        <div className="space-x-4">
          <Link
            to="/login"
            className="text-gray-300 hover:text-white transition-colors"
          >
            Log in
          </Link>
          <Link
            to="/register"
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-full font-medium transition-all"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative flex flex-col items-center justify-center text-center px-4 pt-20 pb-32">
        {/* Background decorations */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl -z-10"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-3xl -z-10"></div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-5xl md:text-7xl font-bold max-w-4xl leading-tight mb-6"
        >
          Navigate your career with <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">AI precision</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-xl text-gray-400 max-w-2xl mb-10"
        >
          Upload your resume, analyze your ATS score, and generate a personalized
          learning roadmap to land your dream job faster.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <Link
            to="/register"
            className="bg-white text-slate-900 px-8 py-4 rounded-full font-bold text-lg hover:bg-gray-100 transition-all shadow-[0_0_40px_rgba(255,255,255,0.3)] hover:shadow-[0_0_60px_rgba(255,255,255,0.4)]"
          >
            Start Your Journey Free
          </Link>
        </motion.div>

        {/* Feature Cards Showcase */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-32 max-w-6xl w-full px-4">
          {[
            {
              title: "Smart ATS Analyzer",
              desc: "Compare your resume against job descriptions and uncover hidden skill gaps instantly.",
              icon: "📊"
            },
            {
              title: "Dynamic Roadmaps",
              desc: "Get a customized, step-by-step learning path tailored specifically to your target role.",
              icon: "🗺️"
            },
            {
              title: "AI Career Coach",
              desc: "Chat with an intelligent coach that knows your background and guides your next moves.",
              icon: "🤖"
            }
          ].map((feature, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.1 + 0.3 }}
              className="bg-white/5 border border-white/10 p-8 rounded-3xl backdrop-blur-md text-left hover:bg-white/10 transition-colors"
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p className="text-gray-400">{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </main>
    </div>
  );
};
