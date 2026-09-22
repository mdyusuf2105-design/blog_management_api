
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

const API_URL = "http://127.0.0.1:8000/user/dashboard/";

function App() {
  const [token, setToken] = useState("");
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadDashboard() {
    if (!token.trim()) {
      setError("Please enter your JWT access token.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(API_URL, {
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
    } catch (err) {
      setError(
        err.message ||
          "Could not connect to the FastAPI server."
      );
    } finally {
      setLoading(false);
    }
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

        <div className="user-badge">
          <span>●</span> Personal Analytics
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
          request your authenticated dashboard.
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

          {/* Overall activity chart */}
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

          {/* Per-post engagement chart */}
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