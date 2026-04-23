import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    host: "0.0.0.0",
    port: 5173,
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (
            id.includes("node_modules/@arco-design") ||
            id.includes("node_modules/dayjs") ||
            id.includes("node_modules/number-precision") ||
            id.includes("node_modules/b-validate") ||
            id.includes("node_modules/compute-scroll-into-view")
          ) {
            return "vendor-arco";
          }
          if (id.includes("node_modules/@vueuse")) {
            return "vendor-motion";
          }
          if (id.includes("node_modules/zrender")) {
            return "vendor-zrender";
          }
          if (id.includes("node_modules/echarts")) {
            return "vendor-echarts";
          }
          if (id.includes("node_modules/leaflet")) {
            return "vendor-leaflet";
          }
          if (id.includes("node_modules/vue") || id.includes("node_modules/pinia") || id.includes("node_modules/vue-router")) {
            return "vendor-vue";
          }
          return undefined;
        },
      },
    },
  },
});
