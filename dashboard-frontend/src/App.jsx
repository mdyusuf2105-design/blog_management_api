
import { useState } from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import "./App.css";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const API_URL = "http://127.0.0.1:8000";
const DASHBOARD_URL = `${API_URL}/user/dashboard/`;
const NOTIFICATIONS_URL = `${API_URL}/notifications/`;

function App() {
  const [token, setToken] = useState("");
  const [dashboard, setDashboard] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [notificationLoading, setNotificationLoading] =
    useState(false);
  const [error, setError] = useState("");
  const [notificationError, setNotificationError] =
    useState("");
  const [showNotifications, setShowNotifications] =
    useState(false);

  const unreadCount = notifications.filter(
    (notification) => !notification.is_read
  ).length;

  async function loadDashboard() {
    if (!token.trim()) {
      setError("Please enter your JWT access token.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(DASHBOARD_URL, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token.trim()}`,
          Accept: "application/json",
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to load dashboard."
        );
      }

      setDashboard(data);
      await loadNotifications();
    } catch (err) {
      setError(
        err.message ||
          "Could not connect to the FastAPI server."
      );
    } finally {
      setLoading(false);
    }
  }

  async function loadNotifications() {
    if (!token.trim()) {
      setNotificationError(
        "Please enter your JWT access token first."
      );
      return;
    }

    setNotificationLoading(true);
    setNotificationError("");

    try {
      const response = await fetch(NOTIFICATIONS_URL, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token.trim()}`,
          Accept: "application/json",
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to load notifications."
        );
      }

      setNotifications(data);
    } catch (err) {
      setNotificationError(
        err.message || "Could not load notifications."
      );
    } finally {
      setNotificationLoading(false);
    }
  }

  async function markAsRead(notificationId) {
    setNotificationError("");

    try {
      const response = await fetch(
        `${NOTIFICATIONS_URL}${notificationId}/read`,
        {
          method: "PATCH",
          headers: {
            Authorization: `Bearer ${token.trim()}`,
            Accept: "application/json",
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to mark as read."
        );
      }

      setNotifications((previous) =>
        previous.map((notification) =>
          notification.id === notificationId
            ? { ...notification, is_read: true }
            : notification
        )
      );
    } catch (err) {
      setNotificationError(
        err.message || "Unable to update notification."
      );
    }
  }

  async function markAllAsRead() {
    setNotificationError("");

    try {
      const response = await fetch(
        `${NOTIFICATIONS_URL}read-all`,
        {
          method: "PATCH",
          headers: {
            Authorization: `Bearer ${token.trim()}`,
            Accept: "application/json",
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to mark all as read."
        );
      }

      setNotifications((previous) =>
        previous.map((notification) => ({
          ...notification,
          is_read: true,
        }))
      );
    } catch (err) {
      setNotificationError(
        err.message || "Unable to update notifications."
      );
    }
  }

  function formatTimestamp(timestamp) {
    if (!timestamp) return "";

    const date = new Date(timestamp);

    if (Number.isNaN(date.getTime())) {
      return timestamp;
    }

    return date.toLocaleString();
  }

  function getNotificationIcon(type) {
    if (type === "like") return "♥";
    if (type === "comment") return "💬";
    if (type === "subscription_renewal") return "↻";
    if (type === "subscription") return "★";

    return "●";
  }

  // Overall statistics chart
  const overviewChartData = dashboard
    ? {
        labels: [
          "Posts",
          "Comments",
          "Likes Received",
          "Views",
        ],
        datasets: [
          {
            label: "Your Activity",
            data: [
              dashboard.total_posts,
              dashboard.total_comments,
              dashboard.total_likes_received,
              dashboard.total_views,
            ],
            backgroundColor: [
              "#6366f1",
              "#06b6d4",
              "#f59e0b",
              "#10b981",
            ],
            borderRadius: 8,
          },
        ],
      }
    : null;

  // Likes and comments for each individual post
  const postChartData = dashboard
    ? {
        labels: dashboard.post_analytics.map(
          (post) => post.title
        ),
        datasets: [
          {
            label: "Likes",
            data: dashboard.post_analytics.map(
              (post) => post.likes_count
            ),
            backgroundColor: "#6366f1",
            borderRadius: 6,
          },
          {
            label: "Comments",
            data: dashboard.post_analytics.map(
              (post) => post.comments_count
            ),
            backgroundColor: "#06b6d4",
            borderRadius: 6,
          },
        ],
      }
    : null;

  const overviewOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: "Your Blog Activity",
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          precision: 0,
        },
      },
    },
  };

  const postChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: "top",
      },
      title: {
        display: true,
        text: "Likes and Comments per Post",
      },
      tooltip: {
        enabled: true,
      },
    },
    scales: {
      x: {
        ticks: {
          maxRotation: 45,
          minRotation: 0,
        },
      },
      y: {
        beginAtZero: true,
        ticks: {
          precision: 0,
        },
      },
    },
  };

  return (
    <main className="dashboard">
      <header className="dashboard-header">
        <div>
          <p className="eyebrow">BLOG MANAGEMENT</p>
          <h1>User Dashboard</h1>
          <p className="subtitle">
            Your personal blog activity at a glance.
          </p>
        </div>

        <div className="header-actions">
          <div className="notification-wrapper">
            <button
              className="notification-bell"
              onClick={() => {
                setShowNotifications((previous) => !previous);

                if (!showNotifications) {
                  loadNotifications();
                }
              }}
              aria-label="Toggle notifications"
              aria-expanded={showNotifications}
            >
              <span className="bell-icon">♧</span>
              <span className="bell-emoji">🔔</span>

              {unreadCount > 0 && (
                <span className="notification-count">
                  {unreadCount > 99 ? "99+" : unreadCount}
                </span>
              )}
            </button>

            {showNotifications && (
              <section className="notification-dropdown">
                <div className="notification-header">
                  <div>
                    <h2>Notifications</h2>
                    <p>
                      {unreadCount} unread notification
                      {unreadCount !== 1 ? "s" : ""}
                    </p>
                  </div>

                  <button
                    className="close-notifications"
                    onClick={() =>
                      setShowNotifications(false)
                    }
                    aria-label="Close notifications"
                  >
                    ×
                  </button>
                </div>

                <div className="notification-actions">
                  <button
                    onClick={loadNotifications}
                    disabled={notificationLoading}
                  >
                    {notificationLoading
                      ? "Refreshing..."
                      : "Refresh"}
                  </button>

                  <button
                    onClick={markAllAsRead}
                    disabled={unreadCount === 0}
                  >
                    Mark all as read
                  </button>
                </div>

                {notificationError && (
                  <p
                    className="notification-error"
                    role="alert"
                  >
                    {notificationError}
                  </p>
                )}

                {notificationLoading &&
                notifications.length === 0 ? (
                  <p className="notification-empty">
                    Loading notifications...
                  </p>
                ) : notifications.length === 0 ? (
                  <p className="notification-empty">
                    You’re all caught up! No notifications yet.
                  </p>
                ) : (
                  <div className="notification-list">
                    {notifications.map((notification) => (
                      <article
                        key={notification.id}
                        className={`notification-item ${
                          notification.is_read
                            ? "read"
                            : "unread"
                        }`}
                      >
                        <div className="notification-icon">
                          {getNotificationIcon(
                            notification.notification_type
                          )}
                        </div>

                        <div className="notification-content">
                          <p>{notification.message}</p>

                          <span className="notification-time">
                            {formatTimestamp(
                              notification.timestamp
                            )}
                          </span>

                          {!notification.is_read && (
                            <button
                              className="mark-read-button"
                              onClick={() =>
                                markAsRead(notification.id)
                              }
                            >
                              Mark as read
                            </button>
                          )}
                        </div>

                        {!notification.is_read && (
                          <span className="unread-dot" />
                        )}
                      </article>
                    ))}
                  </div>
                )}
              </section>
            )}
          </div>

          <div className="user-badge">
            <span>●</span> Personal Analytics
          </div>
        </div>
      </header>

      <section className="token-panel">
        <label htmlFor="token">JWT Access Token</label>

        <input
          id="token"
          type="password"
          placeholder="Paste your access token here"
          value={token}
          onChange={(event) =>
            setToken(event.target.value)
          }
        />

        <button
          onClick={loadDashboard}
          disabled={loading}
        >
          {loading
            ? "Loading..."
            : "Load My Dashboard"}
        </button>

        <p className="helper-text">
          Use your own access token. It is only used to
          request your authenticated dashboard and
          notifications.
        </p>
      </section>

      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}

      {dashboard && (
        <>
          <section className="welcome-panel">
            <div>
              <p className="eyebrow">WELCOME BACK</p>
              <h2>{dashboard.username}</h2>
              <p>Your blog statistics are ready.</p>
            </div>

            <div className="avatar">
              {dashboard.username
                ?.charAt(0)
                .toUpperCase()}
            </div>
          </section>

          <section className="stats-grid">
            <article className="stat-card">
              <div className="stat-icon purple">✍</div>
              <p>Total Posts</p>
              <h2>{dashboard.total_posts}</h2>
              <span>Posts you created</span>
            </article>

            <article className="stat-card">
              <div className="stat-icon blue">☷</div>
              <p>Total Comments</p>
              <h2>{dashboard.total_comments}</h2>
              <span>Comments you made</span>
            </article>

            <article className="stat-card">
              <div className="stat-icon orange">♥</div>
              <p>Likes Received</p>
              <h2>{dashboard.total_likes_received}</h2>
              <span>Likes on your posts</span>
            </article>

            <article className="stat-card">
              <div className="stat-icon green">◉</div>
              <p>Total Views</p>
              <h2>{dashboard.total_views}</h2>
              <span>Views tracked so far</span>
            </article>
          </section>

          <section className="chart-panel">
            <div className="chart-heading">
              <div>
                <h2>Activity Analytics</h2>
                <p>
                  Overview of your blog engagement
                </p>
              </div>

              <span className="live-badge">API DATA</span>
            </div>

            <div className="chart-container">
              <Bar
                data={overviewChartData}
                options={overviewOptions}
              />
            </div>
          </section>

          <section className="chart-panel">
            <div className="chart-heading">
              <div>
                <h2>Post Engagement</h2>
                <p>
                  Compare likes and comments on each
                  of your posts.
                </p>
              </div>

              <span className="live-badge">API DATA</span>
            </div>

            {dashboard.post_analytics.length > 0 ? (
              <div className="chart-container">
                <Bar
                  data={postChartData}
                  options={postChartOptions}
                />
              </div>
            ) : (
              <p className="empty-message">
                You have not created any posts yet.
              </p>
            )}
          </section>

          <footer>
            Blog Management Dashboard · Personal
            statistics
          </footer>
        </>
      )}
    </main>
  );
}

export default App;