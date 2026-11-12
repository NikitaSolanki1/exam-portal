<template>
  <div class="card auth-card"><div class="card-body p-4">
    <h4 class="fw-bold mb-3">My profile</h4>

    <form @submit.prevent="save">
      <div class="mb-3">
        <label class="form-label">Email</label>
        <input class="form-control" :value="form.email" disabled />
      </div>
      <div class="mb-3">
        <label class="form-label">Full name</label>
        <input v-model="form.name" class="form-control" required />
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
      <div class="mb-3">
        <label class="form-label">New password <span class="text-muted small">(leave empty to keep the old one)</span></label>
        <input type="password" v-model="form.password" class="form-control" minlength="4" />
      </div>
      <button class="btn btn-primary w-100">Save profile</button>
    </form>
  </div></div>
</template>

<script>
import api from "../api";

export default {
  data() {
    return {
      form: { email: "", name: "", phone: "", department: "", password: "" },
    };
  },

  created() {
    api.get("/profile").then((res) => {
      this.form = res.data.user;
      this.form.password = "";
    });
  },

  methods: {
    save() {
      api.put("/profile", this.form).then((res) => {
        // Update the name shown in the navbar
        localStorage.setItem("user", JSON.stringify(res.data.user));
        this.$root.user = res.data.user;
        this.form.password = "";
        this.$root.showMessage(res.data.message);
      });
    },
  },
};
</script>
