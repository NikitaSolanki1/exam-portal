<!-- One exam and its slots. The student books one slot here. -->
<template>
  <div v-if="exam">
    <div class="mb-3">
      <div class="text-muted small">{{ exam.course_code }} · {{ exam.course_name }}</div>
      <h3 class="page-title mb-1">{{ exam.name }}</h3>
      <span class="text-muted small">
        {{ exam.exam_type }} · {{ exam.duration }} min · {{ exam.max_marks }} marks · Examiner: {{ exam.examiner_name }}
      </span>
    </div>

    <div v-if="my_booking" class="alert alert-success">
      <i class="bi bi-check-circle"></i> You have booked
      <b>{{ my_booking.slot_date }}, {{ my_booking.start_time }} – {{ my_booking.end_time }}</b>.
      Only one booking per exam is allowed. <router-link to="/student/bookings">Manage my bookings</router-link>
    </div>
    <div v-else-if="!booking_open" class="alert alert-secondary">
      Booking is not open for this exam right now. Booking period: {{ exam.booking_start }} to {{ exam.booking_end }}.
    </div>
    <div v-else class="alert alert-info">
      Booking is open until <b>{{ exam.booking_end }}</b>. Pick one slot below.
    </div>

    <div class="card"><div class="card-body">
      <h5 class="card-title mb-3">Slots</h5>
      <div v-if="slots.length" class="table-responsive">
        <table class="table mb-0">
          <thead><tr><th>Date</th><th>Time</th><th>Seats left</th><th>Status</th><th></th></tr></thead>
          <tbody>
            <tr v-for="slot in slots" :key="slot.id">
              <td>{{ slot.date }}</td>
              <td>{{ slot.start_time }} – {{ slot.end_time }}</td>
              <td>{{ slot.available_seats }} / {{ slot.capacity }}</td>
              <td><StatusBadge :text="slot.status" /></td>
              <td class="text-end">
                <button v-if="booking_open && !my_booking && slot.status === 'Available' && slot.date >= today"
                        class="btn btn-sm btn-success" @click="book(slot.id)">Book this slot</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="text-muted mb-0">The examiner has not created slots for this exam yet.</p>
    </div></div>
  </div>
</template>

<script>
import api from "../../api";

export default {
  data() {
    return {
      examId: this.$route.params.id,
      exam: null,
      slots: [],
      my_booking: null, // this student's booking for this exam, if any
      booking_open: false,
      today: "",
    };
  },

  created() {
    this.load();
  },

  methods: {
    load() {
      api.get(`/student/exams/${this.examId}`).then((res) => {
        this.exam = res.data.exam;
        this.slots = res.data.slots;
        this.my_booking = res.data.my_booking;
        this.booking_open = res.data.booking_open;
        this.today = res.data.today;
      });
    },

    book(slotId) {
      api.post(`/student/slots/${slotId}/book`).then((res) => {
        this.$root.showMessage(res.data.message);
        this.load();
      });
    },
  },
};
</script>
