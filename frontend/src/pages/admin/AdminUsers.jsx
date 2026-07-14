import { useState, useEffect } from 'react';
import { adminAPI } from '../../api/admin';

const AdminUsers = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [search, setSearch] = useState('');
  const [role, setRole] = useState('');
  const [statusVal, setStatusVal] = useState('');

  // Pagination
  const [nextUrl, setNextUrl] = useState(null);
  const [prevUrl, setPrevUrl] = useState(null);
  const [count, setCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);

  const fetchUsers = (page = 1, searchQuery = '', roleQuery = '', statusQuery = '') => {
    setLoading(true);
    const params = {
      page,
      search: searchQuery,
      role: roleQuery,
      is_active: statusQuery
    };

    adminAPI.getUsers(params)
      .then(res => {
        setUsers(res.data.results || res.data);
        setNextUrl(res.data.next);
        setPrevUrl(res.data.previous);
        setCount(res.data.count || res.data.length);
        setLoading(false);
      })
      .catch(err => {
        setError("Failed to load users list.");
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchUsers(1, search, role, statusVal);
  }, [search, role, statusVal]);

  const handleSearchChange = (e) => setSearch(e.target.value);
  const handleRoleChange = (e) => setRole(e.target.value);
  const handleStatusChange = (e) => setStatusVal(e.target.value);

  // Toggle Suspend / Activate
  const handleToggleStatus = (user) => {
    const action = user.is_active ? adminAPI.suspendUser : adminAPI.activateUser;
    action(user.id)
      .then(() => {
        fetchUsers(currentPage, search, role, statusVal);
      })
      .catch(() => alert("Failed to change user status."));
  };

  // Reset User Profile
  const handleResetProfile = (user) => {
    if (window.confirm(`Are you sure you want to delete all resumes and reset the profile for ${user.email}?`)) {
      adminAPI.resetProfile(user.id)
        .then(() => {
          alert(`Resets completed successfully for ${user.email}.`);
          fetchUsers(currentPage, search, role, statusVal);
        })
        .catch(() => alert("Failed to reset profile."));
    }
  };

  // Delete User
  const handleDeleteUser = (user) => {
    if (window.confirm(`CRITICAL: Are you sure you want to permanently delete user ${user.email}? This action CANNOT be undone.`)) {
      adminAPI.deleteUser(user.id)
        .then(() => {
          fetchUsers(currentPage, search, role, statusVal);
        })
        .catch(() => alert("Failed to delete user."));
    }
  };

  // Export Individual JSON dump
  const handleExportData = (user) => {
    adminAPI.exportUserData(user.id)
      .then(res => {
        const jsonStr = JSON.stringify(res.data, null, 2);
        const blob = new Blob([jsonStr], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `user_export_${user.username}.json`;
        link.click();
      })
      .catch(() => alert("Failed to export user data."));
  };

  return (
    <div>
      <div className="admin-header">
        <h1 className="admin-title">User Manager</h1>
        <p className="admin-subtitle">Administrate roles, suspend accounts, and view user profiles.</p>
      </div>

      {/* Filter and search controls */}
      <div className="admin-panel" style={{ marginBottom: '24px' }}>
        <div className="admin-controls">
          <input
            type="text"
            className="admin-input"
            placeholder="Search by username or email..."
            value={search}
            onChange={handleSearchChange}
            style={{ minWidth: '280px' }}
          />

          <select className="admin-select" value={role} onChange={handleRoleChange}>
            <option value="">All Roles</option>
            <option value="admin">Admin</option>
            <option value="recruiter">Recruiter</option>
            <option value="user">User</option>
          </select>

          <select className="admin-select" value={statusVal} onChange={handleStatusChange}>
            <option value="">All Statuses</option>
            <option value="true">Active Only</option>
            <option value="false">Suspended Only</option>
          </select>
        </div>

        {/* User list table */}
        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
            <div className="spinner-border text-primary" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
        ) : error ? (
          <div className="alert alert-danger">{error}</div>
        ) : users.length === 0 ? (
          <p style={{ color: '#64748b', textAlign: 'center', padding: '20px' }}>No users match the criteria.</p>
        ) : (
          <div className="table-responsive">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Full Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Resumes</th>
                  <th>Status</th>
                  <th>Joined Date</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id}>
                    <td>
                      <strong>{u.full_name}</strong>
                      <div style={{ fontSize: '0.8rem', color: '#64748b' }}>@{u.username}</div>
                    </td>
                    <td>{u.email}</td>
                    <td>
                      <span className={`badge ${u.role === 'admin' ? 'badge-purple' : u.role === 'recruiter' ? 'badge-warning' : 'badge-primary'}`}>
                        {u.role.toUpperCase()}
                      </span>
                    </td>
                    <td>{u.resume_count}</td>
                    <td>
                      <span className={`badge ${u.is_active ? 'badge-success' : 'badge-danger'}`}>
                        {u.is_active ? 'ACTIVE' : 'SUSPENDED'}
                      </span>
                    </td>
                    <td>{new Date(u.date_joined).toLocaleDateString()}</td>
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                        <button
                          className={`admin-btn ${u.is_active ? 'admin-btn-danger' : 'admin-btn-primary'}`}
                          onClick={() => handleToggleStatus(u)}
                          style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                        >
                          {u.is_active ? 'Suspend' : 'Activate'}
                        </button>
                        <button
                          className="admin-btn admin-btn-secondary"
                          onClick={() => handleResetProfile(u)}
                          style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                        >
                          Reset
                        </button>
                        <button
                          className="admin-btn admin-btn-outline"
                          onClick={() => handleExportData(u)}
                          style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                        >
                          Export
                        </button>
                        <button
                          className="admin-btn admin-btn-danger"
                          onClick={() => handleDeleteUser(u)}
                          style={{ padding: '6px 12px', fontSize: '0.8rem', background: '#dc2626' }}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination buttons */}
        {count > 10 && (
          <div className="admin-pagination">
            <button
              className="admin-btn admin-btn-outline"
              disabled={!prevUrl}
              onClick={() => {
                const prevPage = currentPage - 1;
                setCurrentPage(prevPage);
                fetchUsers(prevPage, search, role, statusVal);
              }}
            >
              Previous
            </button>
            <span style={{ display: 'flex', alignItems: 'center', padding: '0 12px', color: '#64748b' }}>
              Page {currentPage} of {Math.ceil(count / 10)}
            </span>
            <button
              className="admin-btn admin-btn-outline"
              disabled={!nextUrl}
              onClick={() => {
                const nextPage = currentPage + 1;
                setCurrentPage(nextPage);
                fetchUsers(nextPage, search, role, statusVal);
              }}
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminUsers;
