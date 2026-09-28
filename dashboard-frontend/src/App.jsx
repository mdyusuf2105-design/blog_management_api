
import { useEffect, useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";
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
  const {
    loginWithRedirect,
    getAccessTokenSilently,
    isAuthenticated,
    user,
    logout,
    isLoading,
    error: auth0Error
  } = useAuth0();

  console.log("AUTH0 STATUS:", {
    isLoading,
    isAuthenticated,
    user,
    auth0Error
  });

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
  const [showAIChat, setShowAIChat] = useState(false);
  const [aiMessage, setAiMessage] = useState("");
  const [aiMessages, setAiMessages] = useState([
    {
      sender: "ai",
      text: "Hello! 👋 I'm your Blog Management Support Assistant. How can I help you?"
    }
  ]);
  const [aiLoading, setAiLoading] = useState(false);
  const [authMode, setAuthMode] = useState("login");
  const [authName, setAuthName] = useState("");
  const [authEmail, setAuthEmail] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [authError, setAuthError] = useState("");
  const [authSuccess, setAuthSuccess] = useState("");
  const [authLoading, setAuthLoading] = useState(false);
    // Scheduled Blog Publishing
  const [postTitle, setPostTitle] = useState("");
  const [postContent, setPostContent] = useState("");
  const [publishingOption, setPublishingOption] = useState("publish_now");
  const [scheduledAt, setScheduledAt] = useState("");
  const [postImage, setPostImage] = useState(null);
  const [postImage2, setPostImage2] = useState(null);
  const [postLoading, setPostLoading] = useState(false);
  const [postMessage, setPostMessage] = useState("");
  const [postError, setPostError] = useState("");

  // Automatically load the dashboard after a successful Auth0 login.
  useEffect(() => {
    if (!isAuthenticated || isLoading) {
      return;
    }

    let cancelled = false;

    async function loadAuth0Session() {
      try {
        setError("");

        const accessToken = await getAccessTokenSilently({
          authorizationParams: {
            audience: "http://127.0.0.1:8000",
          },
        });

        if (cancelled) {
          return;
        }

        setToken(accessToken);
        await loadDashboardWithToken(accessToken);
      } catch (err) {
        if (!cancelled) {
          setError(
            err.message ||
              "Auth0 login succeeded, but the dashboard could not be loaded."
          );
        }
      }
    }

    loadAuth0Session();

    return () => {
      cancelled = true;
    };
  }, [isAuthenticated, isLoading, getAccessTokenSilently]);
  if (isLoading) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "18px"
        }}
      >
        Loading authentication...
      </div>
    );
  }
  const unreadCount = notifications.filter(
    (notification) => !notification.is_read
  ).length;

  if (auth0Error) {
    console.error("Auth0 error:", auth0Error);
  }
  async function handleNormalAuth() {
    setAuthError("");
    setAuthSuccess("");

    if (!authEmail.trim() || !authPassword.trim()) {
      setAuthError("Please enter your email and password.");
      return;
    }

    if (authMode === "signup" && !authName.trim()) {
      setAuthError("Please enter your name.");
      return;
    }

    setAuthLoading(true);

    try {
      if (authMode === "signup") {
        const response = await fetch(`${API_URL}/auth/register`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          body: JSON.stringify({
            username: authName.trim(),
            email: authEmail.trim(),
            password: authPassword
          }),
        });
        const data = await response.json();

        if (!response.ok) {
          const detail = Array.isArray(data.detail)
            ? data.detail
                .map((item) => item.msg || "Invalid input")
                .join(", ")
            : data.detail;

          throw new Error(detail || "Signup failed.");
        }

        setAuthSuccess("Signup successful. Please login.");
        setAuthMode("login");
        setAuthPassword("");
      } else {
        const loginBody = new URLSearchParams();
        loginBody.append("username", authEmail.trim());
        loginBody.append("password", authPassword);

        const response = await fetch(`${API_URL}/auth/login`, {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            Accept: "application/json",
          },
          body: loginBody.toString(),
        });

        const data = await response.json();

        if (!response.ok) {
          const detail = Array.isArray(data.detail)
            ? data.detail
                .map((item) => item.msg || "Invalid input")
                .join(", ")
            : data.detail;

          throw new Error(detail || "Login failed.");
        }

        if (!data.access_token) {
          throw new Error("Login succeeded but no access token was returned.");
        }

        setToken(data.access_token);
        setAuthSuccess("Login successful.");
        setAuthPassword("");

        await loadDashboardWithToken(data.access_token);
      }
    } catch (err) {
      setAuthError(err.message || "Authentication failed.");
    } finally {
      setAuthLoading(false);
    }
  }
  // Create a blog post with Publish Now, Draft, or Schedule
  async function createBlogPost() {
    setPostError("");
    setPostMessage("");

    if (!postTitle.trim()) {
      setPostError("Please enter a blog title.");
      return;
    }

    if (!postContent.trim()) {
      setPostError("Please enter blog content.");
      return;
    }

    if (!token) {
      setPostError("Please login first.");
      return;
    }

    if (publishingOption === "schedule" && !scheduledAt) {
      setPostError("Please select a future date and time.");
      return;
    }

    let scheduledDate = null;

    if (publishingOption === "schedule") {
      scheduledDate = new Date(scheduledAt);

      if (Number.isNaN(scheduledDate.getTime())) {
        setPostError("Invalid scheduled date and time.");
        return;
      }

      if (scheduledDate <= new Date()) {
        setPostError("Scheduled date and time must be in the future.");
        return;
      }
    }

    setPostLoading(true);

    try {
      const formData = new FormData();

      formData.append("title", postTitle.trim());
      formData.append("content", postContent.trim());
      formData.append("publishing_option", publishingOption);

      if (publishingOption === "schedule") {
        formData.append(
          "scheduled_at",
          scheduledDate.toISOString()
        );
      }

      if (postImage instanceof File) {
        formData.append("image1", postImage);
      }

      if (postImage2 instanceof File) {
        formData.append("image2", postImage2);
      }

      const response = await fetch(`${API_URL}/posts/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: "application/json",
        },
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail
              .map((item) => item.msg || "Invalid input")
              .join(", ")
          : data.detail;

        throw new Error(detail || "Unable to create blog post.");
      }

      if (publishingOption === "draft") {
        setPostMessage("Blog saved as draft successfully.");
      } else if (publishingOption === "schedule") {
        setPostMessage(
          `Blog scheduled successfully for ${new Date(
            data.scheduled_at
          ).toLocaleString()}.`
        );
      } else {
        setPostMessage("Blog published successfully.");
      }

      // Clear form
      setPostTitle("");
      setPostContent("");
      setPublishingOption("publish_now");
      setScheduledAt("");
      setPostImage(null);
      setPostImage2("null");

      // Refresh dashboard statistics
      await loadDashboardWithToken(token);
    } catch (err) {
      setPostError(
        err.message || "Unable to create blog post."
      );
    } finally {
      setPostLoading(false);
    }
  }
async function loadDashboardWithToken(accessToken) {
  setLoading(true);
  setError("");

  try {
    const response = await fetch(DASHBOARD_URL, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        Accept: "application/json",
      },
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Unable to load dashboard.");
    }

    setDashboard(data);
    setToken(accessToken);
    await loadNotifications(accessToken);
  } catch (err) {
    setError(err.message || "Could not load dashboard.");
  } finally {
    setLoading(false);
  }
}
  async function sendAIMessage() {
    if (!aiMessage.trim()) {
      return;
    }

    let accessToken = token;

    if (!accessToken && isAuthenticated) {
      try {
        accessToken = await getAccessTokenSilently({
          authorizationParams: {
            audience: "http://127.0.0.1:8000",
          },
        });
        setToken(accessToken);
      } catch (err) {
        setAiMessages((previous) => [
          ...previous,
          {
            sender: "ai",
            text: "Please login again before using AI Support.",
          },
        ]);
        return;
      }
    }

    if (!accessToken) {
      setAiMessages((previous) => [
        ...previous,
        {
          sender: "ai",
          text: "Please login first to use AI Support.",
        },
      ]);
      return;
    }

    const userMessage = aiMessage.trim();

    setAiMessages((previous) => [
      ...previous,
      {
        sender: "user",
        text: userMessage
      }
    ]);

    setAiMessage("");
    setAiLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/api/ai-support/?message=${encodeURIComponent(
          userMessage
        )}`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${accessToken}`,
            Accept: "application/json"
          }
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to contact AI Support."
        );
      }

      setAiMessages((previous) => [
        ...previous,
        {
          sender: "ai",
          text: data.response
        }
      ]);
    } catch (error) {
      setAiMessages((previous) => [
        ...previous,
        {
          sender: "ai",
          text: "Sorry, I couldn't process your request right now."
        }
      ]);
    } finally {
      setAiLoading(false);
    }
  }
  async function loadNotifications(providedToken = "") {
    setNotificationLoading(true);
    setNotificationError("");

    try {
      let accessToken = providedToken || token;

      if (!accessToken && isAuthenticated) {
        accessToken = await getAccessTokenSilently({
          authorizationParams: {
            audience: "http://127.0.0.1:8000",
          },
        });
      }

      if (!accessToken) {
        throw new Error("Please login first.");
      }

      setToken(accessToken);

      const response = await fetch(NOTIFICATIONS_URL, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${accessToken}`,
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
        <div className="auth0-login-section">
          {!isAuthenticated ? (
            <>
              <p className="auth0-login-title">
                {dashboard
                  ? "Logged in with Email"
                  : "Login with your account"}
              </p>

              {!dashboard && (
                <div className="normal-auth-section">
                  <p className="auth0-login-title">
                    {authMode === "login"
                      ? "Login with Email"
                      : "Create Account"}
                  </p>

                  {authMode === "signup" && (
                    <input
                      type="text"
                      placeholder="Name"
                      value={authName}
                      onChange={(event) =>
                        setAuthName(event.target.value)
                      }
                    />
                  )}

                  <input
                    type="email"
                    placeholder="Email"
                    value={authEmail}
                    onChange={(event) =>
                      setAuthEmail(event.target.value)
                    }
                  />

                  <input
                    type="password"
                    placeholder="Password"
                    value={authPassword}
                    onChange={(event) =>
                      setAuthPassword(event.target.value)
                    }
                  />

                  <button
                    onClick={handleNormalAuth}
                    disabled={authLoading}
                  >
                    {authLoading
                      ? "Please wait..."
                      : authMode === "login"
                        ? "Login"
                        : "Sign Up"}
                  </button>

                  {authError && (
                    <p
                      style={{
                        color: "#dc2626",
                        margin: "8px 0",
                      }}
                    >
                      {authError}
                    </p>
                  )}

                  {authSuccess && (
                    <p
                      style={{
                        color: "#16a34a",
                        margin: "8px 0",
                      }}
                    >
                      {authSuccess}
                    </p>
                  )}

                  <button
                    type="button"
                    onClick={() => {
                      setAuthMode(
                        authMode === "login"
                          ? "signup"
                          : "login"
                      );
                      setAuthError("");
                      setAuthSuccess("");
                    }}
                  >
                    {authMode === "login"
                      ? "Create a new account"
                      : "Already have an account? Login"}
                  </button>
                </div>
              )}

              {!dashboard && (
                <button
                  className="social-login-button google-login"
                  onClick={() =>
                    loginWithRedirect({
                      authorizationParams: {
                        connection: "google-oauth2",
                        audience: "http://127.0.0.1:8000",
                      },
                    })
                  }
                >
                  Continue with Google
                </button>
              )}
                <button
                  className="facebook-login-button"
                  onClick={() =>
                    loginWithRedirect({
                      authorizationParams: {
                        connection: "facebook"
                      },
                    })
                  }
                >
                  Continue with Facebook
                </button>
              {dashboard && (
                <button
                  className="social-login-button"
                  onClick={() => {
                    setToken("");
                    setDashboard(null);
                    setNotifications([]);
                    setAuthEmail("");
                    setAuthPassword("");
                    setAuthSuccess("");
                    setError("");
                  }}
                >
                  Logout
                </button>
              )}
            </>
          ) : (
            <div>
              <p className="auth0-login-title">
                Logged in as {user?.email || user?.name}
              </p>

              <button
                className="social-login-button"
                onClick={() =>
                  logout({
                    logoutParams: {
                      returnTo: window.location.origin,
                    },
                  })
                }
              >
                Logout
              </button>
            </div>
          )}
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
                    

          {/* Create Blog Post */}
          <section
            style={{
              background: "#ffffff",
              borderRadius: "16px",
              padding: "24px",
              marginBottom: "24px",
              boxShadow: "0 4px 18px rgba(0, 0, 0, 0.08)",
            }}
          >
            <div style={{ marginBottom: "20px" }}>
              <p className="eyebrow">BLOG MANAGEMENT</p>
              <h2 style={{ margin: "4px 0" }}>
                Create Blog Post
              </h2>
              <p style={{ margin: 0, color: "#6b7280" }}>
                Create, save as draft, publish immediately, or
                schedule your blog for later.
              </p>
            </div>

            <div
              style={{
                display: "grid",
                gap: "16px",
              }}
            >
              {/* Title */}
              <div>
                <label
                  style={{
                    display: "block",
                    fontWeight: "600",
                    marginBottom: "6px",
                  }}
                >
                  Title
                </label>

                <input
                  type="text"
                  value={postTitle}
                  onChange={(event) =>
                    setPostTitle(event.target.value)
                  }
                  placeholder="Enter blog title"
                  style={{
                    width: "100%",
                    padding: "12px",
                    border: "1px solid #d1d5db",
                    borderRadius: "8px",
                    boxSizing: "border-box",
                  }}
                />
              </div>

              {/* Content */}
              <div>
                <label
                  style={{
                    display: "block",
                    fontWeight: "600",
                    marginBottom: "6px",
                  }}
                >
                  Content
                </label>

                <textarea
                  value={postContent}
                  onChange={(event) =>
                    setPostContent(event.target.value)
                  }
                  placeholder="Write your blog content"
                  rows="6"
                  style={{
                    width: "100%",
                    padding: "12px",
                    border: "1px solid #d1d5db",
                    borderRadius: "8px",
                    resize: "vertical",
                    boxSizing: "border-box",
                  }}
                />
              </div>

              {/* Images */}
              <div className="blog-image-row">
                <div className="blog-image-upload">
                  <label>
                    Image 1
                  </label>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(event) =>
                      setPostImage(
                        event.target.files?.[0] || null
                      )
                    }
                  
                  />
                </div>

                <div className="blog-image-upload">
                  <label>
                    Image 2
                  </label>

                  <input
                    type="file"
                    accept="image/*"
                    onChange={(event) =>
                      setPostImage2(
                        event.target.files?.[0] || null
                      )
                    }
                  />
                </div>
              </div>

              {/* Publishing Options */}
              <div className="blog-publishing">
                <div className="blog-publishing-title">
                  Publishing Option
                </div>

                <div className="blog-publishing-options">

                  <div className="blog-publishing-option">
                    <input
                      type="radio"
                      id="publish-now"
                      name="publishing-option"
                      value="publish_now"
                      checked={publishingOption === "publish_now"}
                      onChange={(e) => setPublishingOption(e.target.value)}
                    />
                    <label htmlFor="publish-now">
                      Publish Now
                    </label>
                  </div>

                  <div className="blog-publishing-option">
                    <input
                      type="radio"
                      id="save-draft"
                      name="publishing-option"
                      value="draft"
                      checked={publishingOption === "draft"}
                      onChange={(e) => setPublishingOption(e.target.value)}
                    />
                    <label htmlFor="save-draft">
                      Save as Draft
                    </label>
                  </div>

                  <div className="blog-publishing-option">
                    <input
                      type="radio"
                      id="schedule-post"
                      name="publishing-option"
                      value="schedule"
                      checked={publishingOption === "schedule"}
                      onChange={(e) => setPublishingOption(e.target.value)}
                    />
                    <label htmlFor="schedule-post">
                      Schedule Post
                    </label>
                  </div>

                </div>
              </div>
            

              {/* Scheduled Date & Time */}
              {publishingOption === "schedule" && (
                <div>
                  <label
                    style={{
                      display: "block",
                      fontWeight: "600",
                      marginBottom: "6px",
                    }}
                  >
                    Scheduled Date & Time
                  </label>

                  <input
                    type="datetime-local"
                    value={scheduledAt}
                    min={new Date()
                      .toISOString()
                      .slice(0, 16)}
                    onChange={(event) =>
                      setScheduledAt(event.target.value)
                    }
                    style={{
                      padding: "12px",
                      border: "1px solid #d1d5db",
                      borderRadius: "8px",
                    }}
                  />
                </div>
              )}

              {/* Messages */}
              {postError && (
                <p
                  style={{
                    color: "#dc2626",
                    margin: 0,
                    fontWeight: "600",
                  }}
                >
                  {postError}
                </p>
              )}

              {postMessage && (
                <p
                  style={{
                    color: "#16a34a",
                    margin: 0,
                    fontWeight: "600",
                  }}
                >
                  {postMessage}
                </p>
              )}

              {/* Submit */}
              <button
                className="blog-submit-button"
                onClick={createBlogPost}
                disabled={postLoading}
              >
                {postLoading
                  ? "Saving..."
                  : publishingOption === "draft"
                  ? "Save Draft"
                  : publishingOption === "schedule"
                  ? "Schedule Post"
                  : "Publish Now"}
              </button>
            </div>
          </section>

          <section className="stats-grid"></section>
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
      {/* AI Support Chat */}
      <div className="ai-support-container">

        {showAIChat && (
          <div className="ai-chat-window">

            <div className="ai-chat-header">
              <div>
                <strong>AI Support</strong>
                <span>Online</span>
              </div>

              <button
                onClick={() => setShowAIChat(false)}
                className="ai-close-button"
              >
                ×
              </button>
            </div>

            <div className="ai-chat-messages">
              {aiMessages.map((message, index) => (
                <div
                  key={index}
                  className={`ai-message ${
                    message.sender === "user"
                      ? "ai-user-message"
                      : "ai-bot-message"
                  }`}
                >
                  {message.text}
                </div>
              ))}

              {aiLoading && (
                <div className="ai-message ai-bot-message">
                  Typing...
                </div>
              )}
            </div>

            <div className="ai-chat-input-area">
              <input
                type="text"
                placeholder="Ask something..."
                value={aiMessage}
                onChange={(event) =>
                  setAiMessage(event.target.value)
                }
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    sendAIMessage();
                  }
                }}
              />

              <button onClick={sendAIMessage}>
                ➤
              </button>
            </div>
          </div>
        )}
            

        <button
          className="ai-support-button"
          onClick={() =>
            setShowAIChat((previous) => !previous)
          }
        >
          💬
        </button>

      </div>
    </main>
  );
}

export default App;
