import React from "react";
import { createRoot } from "react-dom/client";

import { App } from "@/app/app";
import { AppProviders } from "@/app/providers";
import "@/app/global.css";

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AppProviders>
      <App />
    </AppProviders>
  </React.StrictMode>,
);
