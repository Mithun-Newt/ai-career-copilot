import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { 
  LayoutDashboard, 
  FileUp, 
  Award, 
  Map, 
  User as UserIcon, 
  LogOut, 
  Menu, 
  X, 
  Compass,
  MessageSquare,
  TrendingUp
} from "lucide-react";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const navigationItems = [
    { name: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
    { name: "Resume Hub", path: "/resume", icon: FileUp },
    { name: "Skills Intelligence", path: "/skills", icon: Award },
    { name: "Career Roadmaps", path: "/roadmap", icon: Map },
    { name: "AI Career Coach", path: "/coach", icon: MessageSquare },
    { name: "ATS Match Engine", path: "/ats", icon: TrendingUp },
    { name: "My Profile", path: "/profile", icon: UserIcon },
  ];

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/login");
  };

  const currentPath = location.pathname;

  return (
    <div className="flex h-screen bg-[#030303] text-gray-100 overflow-hidden">
      {/* Sidebar - Desktop */}
      <aside className="hidden md:flex flex-col w-64 bg-[#0a0a0c]/60 backdrop-blur-xl border-r border-white/5 p-6 space-y-8 flex-shrink-0">
        {/* Brand Logo */}
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-purple-500/10 border border-purple-500/30 rounded-xl">
            <Compass className="h-6 w-6 text-purple-400 animate-pulse" />
          </div>
          <span className="font-heading font-bold text-lg bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent">
            Career Copilot
          </span>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 space-y-2">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPath === item.path;
            return (
              <Link
                key={item.name}
                to={item.path}
                className={`flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-300 ${
                  isActive 
                    ? "bg-purple-500/10 border border-purple-500/25 text-purple-300 shadow-[0_0_15px_rgba(168,85,247,0.05)]" 
                    : "text-gray-400 hover:text-gray-200 hover:bg-white/5 border border-transparent"
                }`}
              >
                <Icon className={`h-5 w-5 ${isActive ? "text-purple-400" : "text-gray-500"}`} />
                <span className="text-sm font-medium">{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Footer / Logout */}
        <div className="border-t border-white/5 pt-4">
          <button
            onClick={handleLogout}
            className="flex items-center space-x-3 w-full px-4 py-3 rounded-xl text-gray-500 hover:text-red-400 hover:bg-red-500/5 border border-transparent hover:border-red-500/10 transition-all duration-300"
          >
            <LogOut className="h-5 w-5" />
            <span className="text-sm font-medium">Log Out</span>
          </button>
        </div>
      </aside>

      {/* Sidebar - Mobile Menu */}
      {isMobileOpen && (
        <div className="fixed inset-0 z-50 flex md:hidden bg-[#030303]/80 backdrop-blur-sm">
          <aside className="w-64 bg-[#0a0a0c] border-r border-white/5 p-6 flex flex-col justify-between h-full">
            <div className="space-y-8">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Compass className="h-6 w-6 text-purple-400" />
                  <span className="font-heading font-bold text-lg text-white">Copilot</span>
                </div>
                <button 
                  onClick={() => setIsMobileOpen(false)}
                  className="p-1 bg-white/5 border border-white/10 rounded-lg text-gray-400 hover:text-white"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <nav className="space-y-2">
                {navigationItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = currentPath === item.path;
                  return (
                    <Link
                      key={item.name}
                      to={item.path}
                      onClick={() => setIsMobileOpen(false)}
                      className={`flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-300 ${
                        isActive 
                          ? "bg-purple-500/10 border border-purple-500/20 text-purple-400" 
                          : "text-gray-400 hover:text-gray-200 hover:bg-white/5"
                      }`}
                    >
                      <Icon className="h-5 w-5" />
                      <span className="text-sm font-medium">{item.name}</span>
                    </Link>
                  );
                })}
              </nav>
            </div>

            <div className="border-t border-white/5 pt-4">
              <button
                onClick={handleLogout}
                className="flex items-center space-x-3 w-full px-4 py-3 rounded-xl text-gray-500 hover:text-red-400 transition-all duration-300"
              >
                <LogOut className="h-5 w-5" />
                <span className="text-sm font-medium">Log Out</span>
              </button>
            </div>
          </aside>
          <div className="flex-1" onClick={() => setIsMobileOpen(false)}></div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Navbar */}
        <header className="h-16 border-b border-white/5 flex items-center justify-between px-6 md:px-8 bg-[#030303]/60 backdrop-blur-xl z-40">
          <div className="flex items-center space-x-4">
            <button 
              onClick={() => setIsMobileOpen(true)}
              className="md:hidden p-2 bg-white/5 border border-white/10 rounded-xl text-gray-400 hover:text-white"
            >
              <Menu className="h-5 w-5" />
            </button>
            <h1 className="font-heading font-semibold text-lg text-white capitalize">
              {navigationItems.find(item => item.path === currentPath)?.name || "Dashboard"}
            </h1>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="hidden sm:block text-right">
              <div className="text-xs text-purple-400 font-medium">System Active</div>
            </div>
            <div className="h-8 w-8 rounded-xl bg-gradient-to-tr from-purple-500 to-pink-500 flex items-center justify-between p-[1px]">
              <div className="h-full w-full bg-[#030303] rounded-[11px] flex items-center justify-center">
                <UserIcon className="h-4 w-4 text-purple-400" />
              </div>
            </div>
          </div>
        </header>

        {/* Page Content Body */}
        <main className="flex-1 overflow-y-auto bg-gradient-glow p-6 md:p-8 relative">
          <div className="max-w-6xl mx-auto space-y-8 animate-fade-in">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};
