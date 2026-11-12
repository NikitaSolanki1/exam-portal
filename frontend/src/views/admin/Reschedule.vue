<template>
  <div v-if="booking" class="card mx-auto" style="max-width: 640px"><div class="card-body p-4">
    <h4 class="fw-bold mb-1">Reschedule booking #{{ booking.id }}</h4>
    <p class="text-muted">
      {{ booking.student_name }} · {{ booking.exam_name }}<br />
      Current slot: {{ booking.slot_date }}, {{ booking.start_time }} – {{ booking.end_time }}
    </p>

    <form v-if="free_slots.length" @submit.prevent="move">
      <div class="list-group mb-3">
        <label v-for="slot in free_slots" :key="slot.id" class="list-group-item d-flex gap-2">
          <input class="form-check-input" type="radio" v-model="slotId" :value="slot.id" required />
          <span>
            {{ slot.date }}, {{ slot.start_time }} – {{ slot.end_time }}
            <span class="text-muted small">({{ slot.available_seats }} seats left)</span>
          </span>
        </label>
      </div>
      <button class="btn btn-primary">Move booking</button>
      <router-link to="/admin/bookings" class="btn btn-link">Back</router-link>
    </form>

    <div v-else>
      <div class="alert alert-warning">
        There are no free slots for this exam right now. A slot becomes free when another student cancels,
        or when the examiner adds a new slot.
      </div>
      <router-link to="/admin/bookings" class="btn btn-outline-primary">Back to bookings</router-link>
    </div>
  </div></div>
</template>

<script>
import api from "../../api";

export default {
  data() {
    return {
      bookingId: this.$route.params.id,
      booking: null,
      free_slots: [],
      slotId: null, // the slot the admin picks
    };
  },

  created() {
    api.get(`/admin/bookings/${this.bookingId}/reschedule`).then((res) => {
      this.booking = res.data.booking;
      this.free_slots = res.data.free_slots;
    });
  },

  methods: {
    move() {
      api.put(`/admin/bookings/${this.bookingId}/reschedule`, { slot_id: this.slotId }).then((res) => {
        this.$root.showMessage(res.data.message);
        this.$router.push("/admin/bookings");
      });
    },
  },
};
</script>
