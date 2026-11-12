<template>
  <h3 class="page-title mb-3">My bookings and exam history</h3>

  <div class="card"><div class="card-body">
    <div v-if="bookings.length" class="table-responsive">
      <table class="table mb-0">
        <thead><tr><th>ID</th><th>Exam</th><th>Slot</th><th>Examiner</th><th>Booked on</th><th>Status</th><th>Marks</th><th></th></tr></thead>
        <tbody>
          <tr v-for="b in bookings" :key="b.id">
            <td>{{ b.id }}</td>
            <td>
              <div class="fw-semibold">{{ b.exam_name }}</div>
              <div class="small text-muted">{{ b.course_code }} · {{ b.exam_type }}</div>
            </td>
            <td class="small">{{ b.slot_date }}<br />{{ b.start_time }} – {{ b.end_time }}</td>
            <td>{{ b.examiner_name }}</td>
            <td class="small">{{ b.booking_date }}</td>
            <td><StatusBadge :text="b.status" /></td>
            <td>
              <span v-if="b.status === 'Completed' && b.results_published">{{ b.total_marks }} / {{ b.max_marks }}</span>
              <span v-else-if="b.status === 'Completed'" class="small text-muted">Not published</span>
              <span v-else>–</span>
            </td>
            <td class="text-end">
              <button v-if="b.can_cancel" class="btn btn-sm btn-outline-danger" @click="cancelBooking(b.id)">Cancel</button>
              <span v-else-if="b.status === 'Booked'" class="small text-muted">Deadline passed</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else class="text-muted mb-0">
      You have not booked any exam yet. <router-link to="/student/exams">Browse exams</router-link>.
    </p>
  </div></div>
</template>

<script>
import api from "../../api";

export default {
  data() {
    return {
      bookings: [],
    };
  },

  created() {
    this.load();
  },

  methods: {
    load() {
      api.get("/student/bookings").then((res) => {
        this.bookings = res.data.bookings;
      });
    },

    cancelBooking(bookingId) {
      if (!confirm("Cancel this booking?")) {
        return;
      }
      api.put(`/student/bookings/${bookingId}/cancel`).then((res) => {
        this.$root.showMessage(res.data.message);
        this.load();
      });
    },
  },
};
</script>
