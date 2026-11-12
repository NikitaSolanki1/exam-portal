<template>
  <h3 class="page-title mb-3">All examination slots</h3>

  <div class="card"><div class="card-body">
    <div v-if="slots.length" class="table-responsive">
      <table class="table mb-0">
        <thead><tr><th>ID</th><th>Exam</th><th>Course</th><th>Examiner</th><th>Date</th><th>Time</th><th>Seats left</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="slot in slots" :key="slot.id">
            <td>{{ slot.id }}</td>
            <td><router-link :to="`/admin/exams/${slot.exam_id}`">{{ slot.exam_name }}</router-link></td>
            <td>{{ slot.course_code }}</td>
            <td>{{ slot.examiner_name }}</td>
            <td>{{ slot.date }}</td>
            <td>{{ slot.start_time }} – {{ slot.end_time }}</td>
            <td>{{ slot.available_seats }} / {{ slot.capacity }}</td>
            <td><StatusBadge :text="slot.status" /></td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else class="text-muted mb-0">No slots have been created yet.</p>
  </div></div>
</template>

<script>
import api from "../../api";

export default {
  data() {
    return {
      slots: [],
    };
  },

  created() {
    api.get("/admin/slots").then((res) => {
      this.slots = res.data.slots;
    });
  },
};
</script>
