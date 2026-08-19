import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const apiProxyTarget = env.VITE_API_PROXY_TARGET || "http://127.0.0.1:4901";

  return {
    plugins: [react()],
    server: {
      host: true,
      port: 5203,
      allowedHosts: [".manus.computer"],
      proxy: {
        "/api": apiProxyTarget,
        "/metrics": apiProxyTarget,
        "/health": apiProxyTarget
      }
    }
  };
});
