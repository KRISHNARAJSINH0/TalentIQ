/**
 * AppRoutes – React Router configuration with protected routes.
 */

import { Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import ProtectedRoute from '../components/ProtectedRoute';
import AdminProtectedRoute from '../components/AdminProtectedRoute';
import AdminLayout from '../layouts/AdminLayout';
import AdminDashboard from '../pages/admin/AdminDashboard';
import AdminUsers from '../pages/admin/AdminUsers';
import AdminAnalytics from '../pages/admin/AdminAnalytics';
import AdminReports from '../pages/admin/AdminReports';
import AdminSystem from '../pages/admin/AdminSystem';
import AdminLogs from '../pages/admin/AdminLogs';
import NotificationCenter from '../pages/NotificationCenter';
import Landing from '../pages/Landing';
import Login from '../pages/Login';
import Register from '../pages/Register';
import Dashboard from '../pages/Dashboard';
import Profile from '../pages/Profile';
import EditProfile from '../pages/EditProfile';
import ProfileReview from '../pages/ProfileReview';
import Resumes from '../pages/Resumes';
import ResumeDetails from '../pages/ResumeDetails';
import ATSDashboard from '../pages/ATSDashboard';
import PortfolioDashboard from '../pages/PortfolioDashboard';
import PortfolioAnalytics from '../pages/PortfolioAnalytics';
import PortfolioPublic from '../pages/PortfolioPublic';
import CareerDashboard from '../pages/CareerDashboard';
import RoadmapUI from '../pages/RoadmapUI';
import CoverLetterUI from '../pages/CoverLetterUI';
import TimelineDashboard from '../pages/TimelineDashboard';
import TimelineCompare from '../pages/TimelineCompare';
import TimelineAnalytics from '../pages/TimelineAnalytics';
import JobDashboard from '../pages/JobDashboard';
import JDAnalyzer from '../pages/JDAnalyzer';
import ReputationDashboard from '../pages/ReputationDashboard';
import JobATSDashboard from '../pages/JobATSDashboard';
import BenchmarkDashboard from '../pages/BenchmarkDashboard';
import ExplainableATSDashboard from '../pages/ExplainableATSDashboard';
import ATSCalibrationDashboard from '../pages/admin/ATSCalibrationDashboard';



const AppRoutes = () => {
  return (
    <Routes>
      {/* Public routes with Navbar + Footer */}
      <Route element={<MainLayout />}>
        <Route path="/" element={<Landing />} />
      </Route>

      {/* Auth routes (no layout) */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Protected routes with Navbar + Footer */}
      <Route element={<MainLayout />}>
        <Route
          path="/dashboard"
          element={<ProtectedRoute><Dashboard /></ProtectedRoute>}
        />
        <Route
          path="/profile"
          element={<ProtectedRoute><Profile /></ProtectedRoute>}
        />
        <Route
          path="/profile/edit"
          element={<ProtectedRoute><EditProfile /></ProtectedRoute>}
        />
        <Route
          path="/profile/review"
          element={<ProtectedRoute><ProfileReview /></ProtectedRoute>}
        />
        <Route
          path="/portfolio"
          element={<ProtectedRoute><PortfolioDashboard /></ProtectedRoute>}
        />
        <Route
          path="/portfolio/analytics"
          element={<ProtectedRoute><PortfolioAnalytics /></ProtectedRoute>}
        />
        <Route
          path="/resumes"
          element={<ProtectedRoute><Resumes /></ProtectedRoute>}
        />
        <Route
          path="/resumes/:id"
          element={<ProtectedRoute><ResumeDetails /></ProtectedRoute>}
        />
        <Route
          path="/resumes/:id/ats"
          element={<ProtectedRoute><ATSDashboard /></ProtectedRoute>}
        />
        <Route
          path="/resumes/:id/explainable-ats"
          element={<ProtectedRoute><ExplainableATSDashboard /></ProtectedRoute>}
        />
        <Route
          path="/resumes/:id/job-ats"
          element={<ProtectedRoute><JobATSDashboard /></ProtectedRoute>}
        />
        <Route
          path="/resumes/:id/benchmark"
          element={<ProtectedRoute><BenchmarkDashboard /></ProtectedRoute>}
        />

        <Route
          path="/career"
          element={<ProtectedRoute><CareerDashboard /></ProtectedRoute>}
        />
        <Route
          path="/career/roadmap"
          element={<ProtectedRoute><RoadmapUI /></ProtectedRoute>}
        />
        <Route
          path="/career/cover-letter"
          element={<ProtectedRoute><CoverLetterUI /></ProtectedRoute>}
        />
        <Route
          path="/career/reputation"
          element={<ProtectedRoute><ReputationDashboard /></ProtectedRoute>}
        />
        <Route
          path="/timeline"
          element={<ProtectedRoute><TimelineDashboard /></ProtectedRoute>}
        />
        <Route
          path="/timeline/compare"
          element={<ProtectedRoute><TimelineCompare /></ProtectedRoute>}
        />
        <Route
          path="/timeline/analytics"
          element={<ProtectedRoute><TimelineAnalytics /></ProtectedRoute>}
        />
        <Route
          path="/jobs"
          element={<ProtectedRoute><JobDashboard /></ProtectedRoute>}
        />
        <Route
          path="/jd-analyzer"
          element={<ProtectedRoute><JDAnalyzer /></ProtectedRoute>}
        />
        <Route
          path="/notifications"
          element={<ProtectedRoute><NotificationCenter /></ProtectedRoute>}
        />
      </Route>

      {/* Admin routes wrapped in AdminProtectedRoute and AdminLayout */}
      <Route element={<AdminProtectedRoute><AdminLayout /></AdminProtectedRoute>}>
        <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />
        <Route path="/admin/dashboard" element={<AdminDashboard />} />
        <Route path="/admin/users" element={<AdminUsers />} />
        <Route path="/admin/analytics" element={<AdminAnalytics />} />
        <Route path="/admin/reports" element={<AdminReports />} />
        <Route path="/admin/system" element={<AdminSystem />} />
        <Route path="/admin/logs" element={<AdminLogs />} />
        <Route path="/admin/ats-calibration" element={<ATSCalibrationDashboard />} />
      </Route>


      {/* Standalone public portfolios (no app shell/global navbar) */}
      <Route path="/portfolio/:slug" element={<PortfolioPublic />} />
      <Route path="/u/:slug" element={<PortfolioPublic />} />
    </Routes>
  );
};

export default AppRoutes;
