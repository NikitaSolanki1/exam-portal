<template>
  <h3 class="page-title mb-4">Admin Dashboard</h3>

  <div class="row g-3 mb-4">
    <div v-for="count in counts" :key="count.label" class="col-6 col-md-4 col-xl-2">
      <div class="card stat-card h-100"><div class="card-body">
        <div class="icon mb-2"><i class="bi" :class="count.icon"></i></div>
        <div class="value">{{ count.value }}</div>
        <div class="text-muted small">{{ count.label }}</div>
      </div></div>
    </div>
  </div>

  <div class="row g-3">
    <div class="col-lg-5">
      <div class="card h-100"><div class="card-body">
        <h5 class="card-title mb-3">Examiners waiting for approval</h5>
        <div v-for="user in pending" :key="user.id" class="d-flex justify-content-between align-items-center border-bottom py-2">
          <div>
            <div class="fw-semibold">{{ user.name }}</div>
            <div class="small text-muted">{{ user.email }} · {{ user.department || "No department" }}</div>
          </div>
          <button class="btn btn-sm btn-success" @click="approve(user.id)">Approve</button>
        </div>
        <p v-if="pending.length === 0" class="text-muted mb-0">No pending requests.</p>
      </div></div>
    </div>

    <div class="col-lg-7">
      <div class="card h-100"><div class="card-body">
        <h5 class="card-title mb-3">Latest bookings</h5>
        <div v-if="recent_bookings.length" class="table-responsive">
          <table class="table mb-0">
            <thead><tr><th>Student</th><th>Exam</th><th>Slot</th><th>Status</th></tr></thead>
            <tbody>
              <tr v-for="b in recent_bookings" :key="b.id">
                <td>{{ b.student_name }}</td>
                <td>{{ b.exam_name }}</td>
                <td>{{ b.slot_date }}, {{ b.start_time }}</td>
                <td><StatusBadge :text="b.status" /></td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="text-muted mb-0">No bookings yet.</p>
      </div></div>
    </div>
  </div>
</template>

<script>
import api from "../../api";

export default {
  data() {
    return {
      counts: [],
      pending: [],
      recent_bookings: [],
    };
  },

  created() {
    this.load();
  },

  methods: {
    load() {
      api.get("/admin/dashboard").then((res) => {
        this.counts = res.data.counts;
        this.pending = res.data.pending;
        this.recent_bookings = res.data.recent_bookings;
      });
    },

    approve(userId) {
      api.put(`/admin/examiners/${userId}/approve`).then((res) => {
        this.$root.showMessage(res.data.message);
        this.load();
      });
    },
  },
};
</script>
