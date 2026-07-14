import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import ReputationDashboard from '../pages/ReputationDashboard';
import { resumesAPI } from '../api/resumes';
import { reputationAPI } from '../api/reputation';

// Mock Recharts ResponsiveContainer to avoid JSDOM height/width 0 issues
vi.mock('recharts', async (importOriginal) => {
  const original = await importOriginal();
  return {
    ...original,
    ResponsiveContainer: ({ children }) => (
      <div data-testid="responsive-container" style={{ width: 800, height: 600 }}>
        {children}
      </div>
    ),
  };
});

// Mock the APIs called by ReputationDashboard
vi.mock('../api/resumes', () => ({
  resumesAPI: {
    getResumes: vi.fn()
  }
}));

vi.mock('../api/reputation', () => ({
  reputationAPI: {
    getReputation: vi.fn(),
    calculateReputation: vi.fn()
  }
}));

describe('ReputationDashboard Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders correctly with valid reputation data', async () => {
    resumesAPI.getResumes.mockResolvedValue({
      data: [{ id: '1', resume_title: 'Software Engineer', is_active: true }]
    });

    reputationAPI.getReputation.mockResolvedValue({
      data: {
        score: 85,
        tier: 'Strong',
        details_json: {
          sub_scores: { ats: 80, skills: 85, projects: 90, portfolio: 75, experience: 80, consistency: 85, career: 80, demand: 75, growth: 85, learning: 90 },
          industry_rank: { rank: 15, pool_size: 200, statement: 'Ranked in the top 7.5% of software engineers' },
          benchmarks: [
            { category: 'Candidate', score: 85, type: 'candidate' },
            { category: 'Average', score: 65, type: 'average' }
          ],
          badges: [{ name: 'ATS Master', description: 'Exceptional ATS formatting' }],
          strengths: ['Great project depth'],
          weaknesses: ['Add a portfolio link'],
          suggestions: [{ category: 'Portfolio', text: 'Add a portfolio link', priority: 'High', points: 15 }]
        }
      }
    });

    render(
      <BrowserRouter>
        <ReputationDashboard />
      </BrowserRouter>
    );

    expect(await screen.findByText('Resume Reputation System')).toBeInTheDocument();
    expect(await screen.findByText('85')).toBeInTheDocument();
    expect(await screen.findByText('Strong Stature')).toBeInTheDocument();
    expect(await screen.findByText('Great project depth')).toBeInTheDocument();
  });

  it('renders gracefully when API returns empty data', async () => {
    resumesAPI.getResumes.mockResolvedValue({
      data: [{ id: '1', resume_title: 'Software Engineer', is_active: true }]
    });

    reputationAPI.getReputation.mockResolvedValue({
      data: {}
    });

    render(
      <BrowserRouter>
        <ReputationDashboard />
      </BrowserRouter>
    );

    expect(await screen.findByText('Resume Reputation System')).toBeInTheDocument();
    expect(await screen.findByText('0')).toBeInTheDocument();
    expect(await screen.findByText('Average Stature')).toBeInTheDocument();
  });

  it('renders error message when API fails', async () => {
    resumesAPI.getResumes.mockResolvedValue({
      data: [{ id: '1', resume_title: 'Software Engineer', is_active: true }]
    });

    reputationAPI.getReputation.mockRejectedValue({
      response: {
        status: 500,
        data: { error: 'Failed to compute reputation: Database issue' }
      }
    });

    render(
      <BrowserRouter>
        <ReputationDashboard />
      </BrowserRouter>
    );

    expect(await screen.findByText('Failed to compute reputation: Database issue')).toBeInTheDocument();
  });
});
