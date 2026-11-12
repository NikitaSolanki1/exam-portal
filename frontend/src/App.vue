<template>
  <nav class="navbar navbar-expand navbar-dark app-navbar">
    <div class="container flex-wrap">
      <router-link class="navbar-brand fw-bold" to="/"><i class="bi bi-mortarboard-fill"></i> Exam Portal</router-link>

      <div class="navbar-nav flex-wrap">
        <template v-if="user && user.role === 'admin'">
          <router-link class="nav-link" to="/admin">Dashboard</router-link>
          <router-link class="nav-link" to="/admin/courses">Courses</router-link>
          <router-link class="nav-link" to="/admin/exams">Exams</router-link>
          <router-link class="nav-link" to="/admin/examiners">Examiners</router-link>
          <router-link class="nav-link" to="/admin/students">Students</router-link>
          <router-link class="nav-link" to="/admin/slots">Slots</router-link>
          <router-link class="nav-link" to="/admin/bookings">Bookings</router-link>
        </template>

        <template v-if="user && user.role === 'examiner'">
          <router-link class="nav-link" to="/examiner">Dashboard</router-link>
          <router-link class="nav-link" to="/profile">Profile</router-link>
        </template>

        <template v-if="user && user.role === 'student'">
          <router-link class="nav-link" to="/student">Dashboard</router-link>
          <router-link class="nav-link" to="/student/exams">Exams</router-link>
          <router-link class="nav-link" to="/student/bookings">My Bookings</router-link>
          <router-link class="nav-link" to="/student/results">Results</router-link>
          <router-link class="nav-link" to="/profile">Profile</router-link>
        </template>

        <a v-if="user" class="nav-link" href="#" @click.prevent="logout">
          <i class="bi bi-box-arrow-right"></i> Logout ({{ user.name }})
        </a>
        <template v-else>
          <router-link class="nav-link" to="/login">Login</router-link>
          <router-link class="nav-link" to="/register">Register</router-link>
        </template>
      </div>
    </div>
  </nav>

  <!-- Success and error messages -->
  <div v-if="message" class="alert flash-message" :class="'alert-' + messageType">{{ message }}</div>

  <main class="container py-4">
    <router-view />
  </main>
</template>

<script>
import api from "./api";

export default {
  data() {
    return {
      user: JSON.parse(localStorage.getItem("user")), // the logged-in user, or null
      message: "",
      messageType: "success",
    };
  },

  created() {
    // If any request to Flask fails, show the error message that Flask sent.
    // 401 means the user is not logged in (or was deactivated), so log them out.
    api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (!error.response) {
          this.showMessage("Cannot reach the server. Is Flask running?", "danger");
        } else {
          if (error.response.status === 401) {
            this.logout();
          }
          this.showMessage(error.response.data.message || error.response.data.msg, "danger");
        }
        return Promise.reject(error);
      }
    );
  },

  methods: {
    // Pages call this.$root.showMessage("...") to show a message for 4 seconds
    showMessage(text, type = "success") {
      this.message = text;
      this.messageType = type;
      clearTimeout(this.timer);
      this.timer = setTimeout(() => (this.message = ""), 4000);
    },

    logout() {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      this.user = null;
      this.$router.push("/login");
      this.showMessage("You have been logged out.", "info");
    },
  },
};
</script>
