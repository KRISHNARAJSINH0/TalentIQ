import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import NotificationBell from '../components/NotificationBell';
import { notificationsAPI } from '../api/notifications';

// Mock API helpers
vi.mock('../api/notifications', () => ({
  notificationsAPI: {
    getUnreadCount: vi.fn(),
    getNotifications: vi.fn(),
    markRead: vi.fn(),
  },
}));

describe('NotificationBell Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('initially requests unread count and renders badge if greater than zero', async () => {
    notificationsAPI.getUnreadCount.mockResolvedValue({
      data: { unread_count: 5 },
    });
    notificationsAPI.getNotifications.mockResolvedValue({
      data: [],
    });

    render(
      <BrowserRouter>
        <NotificationBell />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(notificationsAPI.getUnreadCount).toHaveBeenCalled();
    });

    const badge = await screen.findByText('5');
    expect(badge).toBeInTheDocument();
  });

  it('toggles dropdown drawer upon click on the bell container', async () => {
    notificationsAPI.getUnreadCount.mockResolvedValue({
      data: { unread_count: 2 },
    });
    notificationsAPI.getNotifications.mockResolvedValue({
      data: [
        { id: 1, title: 'Resume Parsed', message: 'Test message', read: false, created_at: new Date().toISOString(), priority: 'normal', type: 'resume_parsed', type_display: 'Resume Parsed' },
      ],
    });

    const { container } = render(
      <BrowserRouter>
        <NotificationBell />
      </BrowserRouter>
    );
    
    // Find container element
    const containerDiv = container.querySelector('.bell-container');
    expect(containerDiv).toBeInTheDocument();

    // Drawer should not be present initially
    expect(screen.queryByText('Mark all read')).not.toBeInTheDocument();

    // Click container
    fireEvent.click(containerDiv);

    // Drawer is opened
    await waitFor(() => {
      expect(screen.getByText('Mark all read')).toBeInTheDocument();
      expect(screen.getByText('Resume Parsed')).toBeInTheDocument();
    });
  });
});
