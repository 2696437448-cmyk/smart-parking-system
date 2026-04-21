import { createApp } from "vue";
import ArcoVue from "@arco-design/web-vue";
import "@arco-design/web-vue/dist/arco.css";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import "leaflet/dist/leaflet.css";
import "./styles.css";
import { createArcoTheme } from "./theme/arco";
import { MotionPlugin } from "./theme/motion";

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.use(ArcoVue, createArcoTheme());
app.use(MotionPlugin);
app.mount("#app");
