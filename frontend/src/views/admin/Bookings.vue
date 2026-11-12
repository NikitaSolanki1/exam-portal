<template>
  <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
    <h3 class="page-title mb-0">All bookings</h3>
    <form class="d-flex gap-2" @submit.prevent="load">
      <input v-model="q" class="form-control" placeholder="Search by student, exam or booking ID" />
      <button class="btn btn-outline-primary">Search</button>
    </form>
  </div>

  <div class="card"><div class="card-body">
    <div v-if="bookings.length" class="table-responsive">
      <table class="table mb-0">
        <thead><tr><th>ID</th><th>Student</th><th>Exam</th><th>Slot</th><th>Examiner</th><th>Booked on</th><th>Status</th><th>Marks</th><th></th></tr></thead>
        <tbody>
          <tr v-for="b in bookings" :key="b.id">
            <td>{{ b.id }}</td>
            <td>{{ b.student_name }}<br /><span class="small text-muted">{{ b.student_email }}</span></td>
            <td><router-link :to="`/admin/exams/${b.exam_id}`">{{ b.exam_name }}</router-link></td>
            <td class="small">{{ b.slot_date }}<br />{{ b.start_time }} – {{ b.end_time }}</td>
            <td>{{ b.examiner_name }}</td>
            <td class="small">{{ b.booking_date }}</td>
            <td><StatusBadge :text="b.status" /></td>
            <td>{{ b.total_marks ?? "–" }}</td>
            <td class="text-end text-nowrap">
              <template v-if="b.status === 'Booked'">
                <router-link :to="`/admin/bookings/${b.id}/reschedule`" class="btn btn-sm btn-outline-primary me-1">Reschedule</router-link>
                <button class="btn btn-sm btn-outline-danger" @click="cancelBooking(b.id)">Cancel</button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else class="text-muted mb-0">No bookings found.</p>
  </div></div>
</template>

<script>
import api from "../../api";

export default {
  data() {
    return {
      q: this.$route.query.q || "", // the Students page links here with ?q=email
      bookings: [],
    };
  },

  created() {
    this.load();
  },

  methods: {
    load() {
      api.get("/admin/bookings", { params: { q: this.q } }).then((res) => {
        this.bookings = res.data.bookings;
      });
    },

    cancelBooking(bookingId) {
      if (!confirm("Cancel this booking?")) {
        return;
      }
      api.put(`/admin/bookings/${bookingId}/cancel`).then((res) => {
        this.$root.showMessage(res.data.message);
        this.load();
      });
    },
  },
};
</script>
