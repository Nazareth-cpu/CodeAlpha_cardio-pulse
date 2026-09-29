import React from 'react';
import { createBrowserRouter, type RouteObject } from 'react-router-dom';
import { AppLayout } from '../components/layout/AppLayout';
import { ProtectedRoute } from '../components/layout/ProtectedRoute';
import { LandingPage } from '../pages/LandingPage';
import { LoginPage } from '../pages/LoginPage';
import { SignupPage } from '../pages/SignupPage';
import { DashboardPage } from '../pages/DashboardPage';
import { AssessmentPage } from '../pages/AssessmentPage';
import { ResultPage } from '../pages/ResultPage';
import { HistoryPage } from '../pages/HistoryPage';
import { ProfilePage } from '../pages/ProfilePage';
import { AboutModelPage } from '../pages/AboutModelPage';
import { NotFoundPage } from '../pages/NotFoundPage';

export const routes: RouteObject[] = [
  {
    path: '/',
    element: <AppLayout />,
    children: [
      // Public routes
      { index: true, element: <LandingPage /> },
      { path: 'login', element: <LoginPage /> },
      { path: 'signup', element: <SignupPage /> },
      { path: 'about-model', element: <AboutModelPage /> },

      // Protected routes requiring verified Firebase token
      {
        element: <ProtectedRoute />,
        children: [
          { path: 'dashboard', element: <DashboardPage /> },
          { path: 'assessment', element: <AssessmentPage /> },
          { path: 'result/:id', element: <ResultPage /> },
          { path: 'history', element: <HistoryPage /> },
          { path: 'profile', element: <ProfilePage /> },
        ],
      },

      // Fallback
      { path: '*', element: <NotFoundPage /> },
    ],
  },
];

// Initialize browser router safely for browser contexts
export const router =
  typeof document !== 'undefined'
    ? createBrowserRouter(routes)
    : (null as unknown as ReturnType<typeof createBrowserRouter>);
