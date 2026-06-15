import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Landing } from "./pages/Landing";
import { Login } from "./pages/Login";
import { Register } from "./pages/Register";
import { Dashboard } from "./pages/Dashboard";
import { ResumeUpload } from "./pages/ResumeUpload";
import { SkillsDashboard } from "./pages/SkillsDashboard";
import { RoadmapDashboard } from "./pages/RoadmapDashboard";
import { Profile } from "./pages/Profile";
import { CareerCoach } from "./pages/CareerCoach";
import { ATSAnalyzer } from "./pages/ATSAnalyzer";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { DashboardLayout } from "./layouts/DashboardLayout";

// Initialize TanStack Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          {/* Public Authentication Routes */}
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Guarded Workspaces Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <Dashboard />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/resume"
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <ResumeUpload />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/skills"
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <SkillsDashboard />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/roadmap"
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <RoadmapDashboard />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <Profile />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/coach"
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <CareerCoach />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/ats"
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <ATSAnalyzer />
                </DashboardLayout>
              </ProtectedRoute>
            }
          />

          {/* Root Redirect fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
