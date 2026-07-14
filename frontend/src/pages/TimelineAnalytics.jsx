import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { HiOutlineChevronLeft, HiOutlineTrendingUp, HiOutlineAcademicCap, HiOutlineChartPie } from 'react-icons/hi';
import { timelineAPI } from '../api/timeline';
import '../styles/Timeline.css';

const TimelineAnalytics = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const res = await timelineAPI.getTimelineHistory();
        setData(res.data);
      } catch (err) {
        console.error('Failed to fetch analytics', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  // Custom SVG Line/Area Chart Renderer
  const renderLineChart = (pointsData, color = '#818cf8', fillGradientId = 'grad1') => {
    if (!pointsData || pointsData.length === 0) {
      return (
        <div className="text-center py-5 text-muted small">
          Not enough historical records to plot growth. Check back after performing updates.
        </div>
      );
    }

    const width = 600;
    const height = 240;
    const padding = 40;

    const values = pointsData.map(p => p.score ?? p.count ?? 0);
    const maxVal = Math.max(...values, 100);
    const minVal = 0;

    const getX = (index) => {
      if (pointsData.length <= 1) return width / 2;
      return padding + (index * (width - 2 * padding)) / (pointsData.length - 1);
    };

    const getY = (val) => {
      return height - padding - ((val - minVal) * (height - 2 * padding)) / (maxVal - minVal);
    };

    let pathD = '';
    let areaD = '';

    pointsData.forEach((p, idx) => {
      const val = p.score ?? p.count ?? 0;
      const x = getX(idx);
      const y = getY(val);

      if (idx === 0) {
        pathD = `M ${x} ${y}`;
        areaD = `M ${x} ${height - padding} L ${x} ${y}`;
      } else {
        pathD += ` L ${x} ${y}`;
      }

      if (idx === pointsData.length - 1) {
        areaD += ` L ${x} ${y} L ${x} ${height - padding} Z`;
      } else if (idx > 0) {
        areaD += ` L ${x} ${y}`;
      }
    });

    return (
      <svg viewBox={`0 0 ${width} ${height}`} className="w-100 h-auto">
        <defs>
          <linearGradient id={fillGradientId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.4"/>
            <stop offset="100%" stopColor={color} stopOpacity="0.0"/>
          </linearGradient>
        </defs>

        {/* Horizontal Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio, idx) => {
          const y = padding + ratio * (height - 2 * padding);
          const gridVal = maxVal - ratio * (maxVal - minVal);
          return (
            <g key={idx}>
              <line x1={padding} y1={y} x2={width - padding} y2={y} stroke="rgba(255,255,255,0.06)" strokeDasharray="4 4" />
              <text x={padding - 10} y={y + 4} fill="#64748b" fontSize="10" textAnchor="end">{Math.round(gridVal)}</text>
            </g>
          );
        })}

        {/* Area fill */}
        {pointsData.length > 1 && <path d={areaD} fill={`url(#${fillGradientId})`} />}

        {/* Path line */}
        <path d={pathD} fill="none" stroke={color} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />

        {/* Node circles */}
        {pointsData.map((p, idx) => {
          const val = p.score ?? p.count ?? 0;
          return (
            <circle
              key={idx}
              cx={getX(idx)}
              cy={getY(val)}
              r="5"
              fill="#1e293b"
              stroke={color}
              strokeWidth="3"
            />
          );
        })}

        {/* X Axis Date labels */}
        {pointsData.map((p, idx) => {
          if (pointsData.length > 6 && idx % 2 !== 0) return null; // prevent text overlapping
          return (
            <text
              key={idx}
              x={getX(idx)}
              y={height - 15}
              fill="#64748b"
              fontSize="9"
              textAnchor="middle"
            >
              {p.date}
            </text>
          );
        })}
      </svg>
    );
  };

  // Custom SVG Radar Chart for Career Alignment Profile
  const renderRadarChart = () => {
    const size = 300;
    const center = size / 2;
    const radius = 100;

    const latestCareer = data?.career_trends?.[data.career_trends.length - 1] || {
      career_score: 70,
      growth_score: 75,
      learning_score: 80,
      market_alignment: 65
    };

    const categories = [
      { label: 'ATS Score', val: data?.ats_history?.[data.ats_history.length - 1]?.score || 50 },
      { label: 'Career Growth', val: latestCareer.growth_score },
      { label: 'Learning Progress', val: latestCareer.learning_score },
      { label: 'Market Match', val: latestCareer.market_alignment },
    ];

    const getCoordinates = (index, val) => {
      const angle = (Math.PI * 2 / categories.length) * index - Math.PI / 2;
      const x = center + radius * (val / 100) * Math.cos(angle);
      const y = center + radius * (val / 100) * Math.sin(angle);
      return { x, y };
    };

    // concentric scale circles
    const scalePolys = [25, 50, 75, 100].map((scaleVal) => {
      return categories.map((_, idx) => {
        const coords = getCoordinates(idx, scaleVal);
        return `${coords.x},${coords.y}`;
      }).join(' ');
    });

    const activePolyPoints = categories.map((cat, idx) => {
      const coords = getCoordinates(idx, cat.val);
      return `${coords.x},${coords.y}`;
    }).join(' ');

    return (
      <svg viewBox={`0 0 ${size} ${size}`} className="w-100 h-auto" style={{ maxWidth: '350px', margin: '0 auto' }}>
        {/* Scale webs */}
        {scalePolys.map((points, idx) => (
          <polygon
            key={idx}
            points={points}
            fill="none"
            stroke="rgba(255, 255, 255, 0.08)"
            strokeWidth="1"
          />
        ))}

        {/* Category axes */}
        {categories.map((cat, idx) => {
          const outerCoords = getCoordinates(idx, 100);
          const textCoords = getCoordinates(idx, 120);
          return (
            <g key={idx}>
              <line x1={center} y1={center} x2={outerCoords.x} y2={outerCoords.y} stroke="rgba(255,255,255,0.08)" />
              <text
                x={textCoords.x}
                y={textCoords.y + 4}
                fill="#94a3b8"
                fontSize="10"
                fontWeight="600"
                textAnchor="middle"
              >
                {cat.label}
              </text>
            </g>
          );
        })}

        {/* Data polygon */}
        <polygon
          points={activePolyPoints}
          fill="rgba(52, 211, 153, 0.25)"
          stroke="#34d399"
          strokeWidth="3"
        />

        {/* Axis center dot */}
        <circle cx={center} cy={center} r="4" fill="#10b981" />
      </svg>
    );
  };

  return (
    <div className="timeline-container">
      <div className="mb-4">
        <Link to="/timeline" className="btn btn-link text-decoration-none p-0 d-flex align-items-center gap-2" style={{ color: 'var(--primary, #2563eb)' }}>
          <HiOutlineChevronLeft /> Back to Career Timeline
        </Link>
      </div>

      <div className="timeline-header">
        <div>
          <h1>Growth Analytics Dashboard</h1>
          <p className="text-muted">Analyze your career progress, resume evolution, and learning metrics in detail.</p>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status"></div>
        </div>
      ) : !data ? (
        <div className="alert alert-danger">Failed to calculate growth analytics.</div>
      ) : (
        <div>
          {/* Top Level Summary Cards */}
          <div className="row g-4 mb-4">
            <div className="col-md-6 col-lg-3">
              <div className="timeline-card-panel p-4 text-center">
                <span className="text-muted small uppercase">ATS Net Growth</span>
                <h2 className="text-success mt-2 mb-0">+{data.ats_growth.toFixed(1)}</h2>
              </div>
            </div>
            <div className="col-md-6 col-lg-3">
              <div className="timeline-card-panel p-4 text-center">
                <span className="text-muted small uppercase">Total Skills Captured</span>
                <h2 className="text-info mt-2 mb-0">
                  {data.skill_trends?.[data.skill_trends.length - 1]?.count || 0}
                </h2>
              </div>
            </div>
            <div className="col-md-6 col-lg-3">
              <div className="timeline-card-panel p-4 text-center">
                <span className="text-muted small uppercase">Completed roadmaps</span>
                <h2 className="text-warning mt-2 mb-0">
                  {data.learning_progress?.filter(p => p.status === 'Completed').length || 0}
                </h2>
              </div>
            </div>
            <div className="col-md-6 col-lg-3">
              <div className="timeline-card-panel p-4 text-center">
                <span className="text-muted small uppercase">Captured Versions</span>
                <h2 className="text-primary mt-2 mb-0">{data.version_trends?.length || 0}</h2>
              </div>
            </div>
          </div>

          <div className="row g-4 mb-4">
            {/* ATS Score Progress */}
            <div className="col-lg-6">
              <div className="timeline-card-panel p-4 h-100">
                <h5 className="mb-4 d-flex align-items-center gap-2">
                  <HiOutlineTrendingUp className="text-info" /> ATS Score Evolution Trend
                </h5>
                {renderLineChart(data.ats_history, '#818cf8', 'atsGrad')}
              </div>
            </div>

            {/* Active Skills Growth */}
            <div className="col-lg-6">
              <div className="timeline-card-panel p-4 h-100">
                <h5 className="mb-4 d-flex align-items-center gap-2">
                  <HiOutlineTrendingUp className="text-success" /> Active Skills Accumulation
                </h5>
                {renderLineChart(
                  data.skill_trends.map(t => ({ date: t.date, count: t.count })), 
                  '#34d399', 
                  'skillGrad'
                )}
              </div>
            </div>
          </div>

          <div className="row g-4">
            {/* Career Radar Map */}
            <div className="col-lg-4">
              <div className="timeline-card-panel p-4 h-100 text-center">
                <h5 className="mb-4 text-start d-flex align-items-center gap-2">
                  <HiOutlineChartPie className="text-warning" /> Career Radar profile
                </h5>
                <div className="d-flex align-items-center justify-content-center h-100">
                  {renderRadarChart()}
                </div>
              </div>
            </div>

            {/* Learning History list */}
            <div className="col-lg-8">
              <div className="timeline-card-panel p-4 h-100">
                <h5 className="mb-4 d-flex align-items-center gap-2">
                  <HiOutlineAcademicCap className="text-success" /> Coursework & Roadmap History
                </h5>
                {data.learning_progress.length === 0 ? (
                  <div className="text-center py-5 text-muted small">
                    No coursework logged. Complete career roads or add certificates to populate this list.
                  </div>
                ) : (
                  <div className="table-responsive">
                    <table className="table table-hover timeline-table mb-0">
                      <thead>
                        <tr>
                          <th>Topic</th>
                          <th>Progress</th>
                          <th>Status</th>
                          <th>Date</th>
                        </tr>
                      </thead>
                      <tbody>
                        {data.learning_progress.map((item, index) => (
                          <tr key={index}>
                            <td>{item.topic}</td>
                            <td>
                              <div className="d-flex align-items-center gap-2">
                                <div className="progress flex-grow-1" style={{ height: '6px', maxWidth: '100px' }}>
                                  <div className="progress-bar bg-success" style={{ width: `${item.progress}%` }}></div>
                                </div>
                                <span>{item.progress}%</span>
                              </div>
                            </td>
                            <td>
                              <span className={`badge ${item.status === 'Completed' ? 'bg-success' : 'bg-warning'} rounded-pill`}>
                                {item.status}
                              </span>
                            </td>
                            <td>{item.date}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TimelineAnalytics;
