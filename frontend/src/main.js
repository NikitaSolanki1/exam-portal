import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import StatusBadge from "./components/StatusBadge.vue";
import "./style.css";

const app = createApp(App);
app.use(router);
app.component("StatusBadge", StatusBadge); // <StatusBadge> can now be used on every page
app.mount("#app");
