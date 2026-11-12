<template>
  <div class="card auth-card"><div class="card-body p-4">
    <h4 class="fw-bold mb-1">Welcome back</h4>
    <p class="text-muted">Log in as admin, examiner or student.</p>

    <form @submit.prevent="login">
      <div class="mb-3">
        <label class="form-label">Email</label>
        <input type="email" v-model="email" class="form-control" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Password</label>
        <input type="password" v-model="password" class="form-control" required />
      </div>
      <button class="btn btn-primary w-100">Login</button>
    </form>

    <p class="text-center mt-3 mb-0">New here? <router-link to="/register">Create an account</router-link></p>
  </div></div>
</template>

<script>
import api from "../api";

export default {
  data() {
    return {
      email: "",
      password: "",
    };
  },

  methods: {
    login() {
      api.post("/login", { email: this.email, password: this.password }).then((res) => {
        // Save the token and the user, so we stay logged in after a page refresh
        localStorage.setItem("token", res.data.token);
        localStorage.setItem("user", JSON.stringify(res.data.user));
        this.$root.user = res.data.user;
        this.$router.push("/" + res.data.user.role); // e.g. /admin, /examiner or /student
      });
    },
  },
};
</script>
