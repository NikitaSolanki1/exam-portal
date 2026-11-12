<!-- Give marks for each rubric criterion, plus remarks -->
<template>
  <div v-if="booking" class="card mx-auto" style="max-width: 720px"><div class="card-body p-4">
    <h4 class="fw-bold mb-1">Evaluate {{ booking.student_name }}</h4>
    <p class="text-muted">
      {{ booking.exam_name }} · {{ booking.slot_date }}, {{ booking.start_time }}<br />
      {{ booking.student_email }} · {{ booking.student_department || "No department" }}
    </p>

    <div v-if="rubrics.length === 0" class="alert alert-warning">The admin has not added a rubric for this exam yet.</div>

    <form v-else @submit.prevent="submit">
      <table class="table">
        <thead><tr><th>Criterion</th><th>Weightage</th><th style="width: 150px">Marks</th></tr></thead>
        <tbody>
          <tr v-for="rubric in rubrics" :key="rubric.id">
            <td>
              <div class="fw-semibold">{{ rubric.criterion }}</div>
              <div class="small text-muted">{{ rubric.description }}</div>
            </td>
            <td>{{ rubric.weightage }}%</td>
            <td>
              <div class="input-group">
                <input type="number" v-model="marks[rubric.id]" class="form-control" min="0" :max="rubric.max_marks" required />
                <span class="input-group-text">/ {{ rubric.max_marks }}</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="mb-3">
        <label class="form-label">Remarks for the student</label>
        <textarea v-model="remarks" class="form-control" rows="3" required></textarea>
      </div>
      <button class="btn btn-success">Submit marks</button>
      <router-link :to="`/examiner/exams/${booking.exam_id}`" class="btn btn-link">Cancel</router-link>
    </form>
  </div></div>
</template>

<script>
import api from "../../api";

export default {
  data() {
    return {
      bookingId: this.$route.params.id,
      booking: null,
      rubrics: [],
      marks: {}, // { rubric id: marks }
      remarks: "",
    };
  },

  created() {
    api.get(`/examiner/bookings/${this.bookingId}/evaluate`).then((res) => {
      this.booking = res.data.booking;
      this.rubrics = res.data.rubrics;
      this.marks = res.data.old_marks; // marks given before, if this is a re-evaluation
      this.remarks = res.data.booking.remarks || "";
    });
  },

  methods: {
    submit() {
      api.post(`/examiner/bookings/${this.bookingId}/evaluate`, { marks: this.marks, remarks: this.remarks }).then((res) => {
        this.$root.showMessage(res.data.message);
        this.$router.push(`/examiner/exams/${this.booking.exam_id}`);
      });
    },
  },
};
</script>
