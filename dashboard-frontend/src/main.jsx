import React from "react";
import ReactDOM from "react-dom/client";
import { Auth0Provider } from "@auth0/auth0-react";

import App from "./App";
import "./index.css";

const domain = "dev-pdv15uboe1vee85h.us.auth0.com";
const clientId = "1OSq3Tje20kfjqYB2suVs2gQ9GJUYqP9";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <Auth0Provider
      domain={domain}
      clientId={clientId}
      authorizationParams={{
        redirect_uri: window.location.origin,
        audience: "http://127.0.0.1:8000",
        scope: "openid profile email",
      }}
      onRedirectCallback={() => {
        window.history.replaceState(
          {},
          document.title,
          window.location.pathname
        );
      }}
    >
      <App />
    </Auth0Provider>
  </React.StrictMode>
);