import { createApp } from "vue";
import { Alert, Button, Form, Input, Select, Space, Statistic, Tag } from "@arco-design/web-vue";
import "@arco-design/web-vue/dist/arco.css";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import "leaflet/dist/leaflet.css";
import "./styles.css";
import { createArcoTheme } from "./theme/arco";
import { MotionPlugin } from "./theme/motion";

const app = createApp(App);
const arcoTheme = createArcoTheme();
const arcoComponents = [Alert, Button, Form, Input, Select, Space, Statistic, Tag];

app.use(createPinia());
app.use(router);
arcoComponents.forEach((component) => {
  app.use(component, arcoTheme);
});
app.use(MotionPlugin);
app.mount("#app");
