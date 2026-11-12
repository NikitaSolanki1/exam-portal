<template>
  <div class="card auth-card"><div class="card-body p-4">
    <h4 class="fw-bold mb-1">Create an account</h4>
    <p class="text-muted">Examiner accounts need admin approval before login.</p>

    <form @submit.prevent="register">
      <div class="mb-3">
        <label class="form-label">I am a</label>
        <select v-model="form.role" class="form-select" required>
          <option value="student">Student</option>
          <option value="examiner">Examiner</option>
        </select>
      </div>
      <div class="mb-3">
        <label class="form-label">Full name</label>
        <input v-model="form.name" class="form-control" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Email</label>
        <input type="email" v-model="form.email" class="form-control" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Password</label>
        <input type="password" v-model="form.password" class="form-control" minlength="4" required />
      </div>
      <div class="row g-2 mb-3">
        <div class="col">
          <label class="form-label">Phone</label>
          <input v-model="form.phone" class="form-control" />
        </div>
        <div class="col">
          <label class="form-label">Department</label>
          <input v-model="form.department" class="form-control" />
        </div>
      </div>
      <button class="btn btn-primary w-100">Register</button>
    </form>

    <p class="text-center mt-3 mb-0">Already registered? <router-link to="/login">Login</router-link></p>
  </div></div>
</template>

<script>
import api from "../api";

export default {
  data() {
    return {
      form: { role: "student", name: "", email: "", password: "", phone: "", department: "" },
    };
  },

  methods: {
    register() {
      api.post("/register", this.form).then((res) => {
        this.$root.showMessage(res.data.message);
        this.$router.push("/login");
      });
    },
  },
};
</script>
