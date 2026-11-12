<template>
  <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
    <h3 class="page-title mb-0">Students</h3>
    <form class="d-flex gap-2" @submit.prevent="load">
      <input v-model="q" class="form-control" placeholder="Search by name, email, department or ID" />
      <button class="btn btn-outline-primary">Search</button>
    </form>
  </div>

  <div class="card"><div class="card-body">
    <div v-if="students.length" class="table-responsive">
      <table class="table mb-0">
        <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th><th>Department</th><th>Bookings</th><th>Status</th><th></th></tr></thead>
        <tbody>
          <tr v-for="user in students" :key="user.id">
            <td>{{ user.id }}</td>
            <td class="fw-semibold">{{ user.name }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.phone || "–" }}</td>
            <td>{{ user.department || "–" }}</td>
            <td><router-link :to="{ path: '/admin/bookings', query: { q: user.email } }">{{ user.booking_count }}</router-link></td>
            <td><StatusBadge :text="user.is_active ? 'Active' : 'Deactivated'" /></td>
            <td class="text-end">
              <button class="btn btn-sm" :class="user.is_active ? 'btn-outline-danger' : 'btn-outline-success'" @click="toggle(user.id)">
                {{ user.is_active ? "Deactivate" : "Activate" }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else class="text-muted mb-0">No students found.</p>
  </div></div>
</template>

<script>
import api from "../../api";

export default {
  data() {
    return {
      q: "", // search text
      students: [],
    };
  },

  created() {
    this.load();
  },

  methods: {
    load() {
      api.get("/admin/students", { params: { q: this.q } }).then((res) => {
        this.students = res.data.students;
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
