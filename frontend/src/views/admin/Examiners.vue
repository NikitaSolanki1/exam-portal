<template>
  <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
    <h3 class="page-title mb-0">Examiners</h3>
    <form class="d-flex gap-2" @submit.prevent="load">
      <input v-model="q" class="form-control" placeholder="Search by name, email, department or ID" />
      <button class="btn btn-outline-primary">Search</button>
    </form>
  </div>

  <div class="row g-3">
    <div class="col-lg-8">
      <div class="card"><div class="card-body">
        <div v-if="examiners.length" class="table-responsive">
          <table class="table mb-0">
            <thead><tr><th>ID</th><th>Name</th><th>Contact</th><th>Department</th><th>Exams</th><th>Status</th><th></th></tr></thead>
            <tbody>
              <tr v-for="user in examiners" :key="user.id">
                <td>{{ user.id }}</td>
                <td class="fw-semibold">{{ user.name }}</td>
                <td class="small">{{ user.email }}<br /><span class="text-muted">{{ user.phone }}</span></td>
                <td>{{ user.department || "–" }}</td>
                <td>{{ user.exam_count }}</td>
                <td>
                  <StatusBadge v-if="!user.is_approved" text="Pending" />
                  <StatusBadge v-else-if="user.is_active" text="Active" />
                  <StatusBadge v-else text="Deactivated" />
                </td>
                <td class="text-end text-nowrap">
                  <button v-if="!user.is_approved" class="btn btn-sm btn-success me-1" @click="approve(user.id)">Approve</button>
                  <button class="btn btn-sm" :class="user.is_active ? 'btn-outline-danger' : 'btn-outline-success'" @click="toggle(user.id)">
                    {{ user.is_active ? "Deactivate" : "Activate" }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="text-muted mb-0">No examiners found.</p>
      </div></div>
    </div>

    <div class="col-lg-4">
      <div class="card"><div class="card-body">
        <h5 class="card-title">Add an examiner</h5>
        <form @submit.prevent="addExaminer">
          <div class="mb-2"><input v-model="form.name" class="form-control" placeholder="Full name" required /></div>
          <div class="mb-2"><input type="email" v-model="form.email" class="form-control" placeholder="Email" required /></div>
          <div class="mb-2"><input type="password" v-model="form.password" class="form-control" placeholder="Password" minlength="4" required /></div>
          <div class="mb-2"><input v-model="form.phone" class="form-control" placeholder="Phone" /></div>
          <div class="mb-3"><input v-model="form.department" class="form-control" placeholder="Department" /></div>
          <button class="btn btn-primary w-100">Add examiner</button>
        </form>
      </div></div>
    </div>
  </div>
</template>

<script>
import api from "../../api";

export default {
  data() {
    return {
      q: "", // search text
      examiners: [],
      form: { name: "", email: "", password: "", phone: "", department: "" },
    };
  },

  created() {
    this.load();
  },

  methods: {
    load() {
      api.get("/admin/examiners", { params: { q: this.q } }).then((res) => {
        this.examiners = res.data.examiners;
      });
    },

    addExaminer() {
      api.post("/admin/examiners", this.form).then((res) => {
        this.$root.showMessage(res.data.message);
        this.form = { name: "", email: "", password: "", phone: "", department: "" };
        this.load();
      });
    },

    approve(userId) {
      api.put(`/admin/examiners/${userId}/approve`).then((res) => {
        this.$root.showMessage(res.data.message);
        this.load();
      });
    },

    // Deactivate or activate
    toggle(userId) {
      api.put(`/admin/users/${userId}/toggle`).then((res) => {
        this.$root.showMessage(res.data.message);
        this.load();
      });
    },
  },
};
</script>
