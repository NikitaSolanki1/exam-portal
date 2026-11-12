<template>
  <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
    <h3 class="page-title mb-0">Examinations</h3>
    <div class="d-flex gap-2">
      <form class="d-flex gap-2" @submit.prevent="load">
        <input v-model="q" class="form-control" placeholder="Search by name, course or ID" />
        <button class="btn btn-outline-primary">Search</button>
      </form>
      <router-link to="/admin/exams/new" class="btn btn-primary text-nowrap"><i class="bi bi-plus-lg"></i> Add exam</router-link>
    </div>
  </div>

  <div class="card"><div class="card-body">
    <div v-if="exams.length" class="table-responsive">
      <table class="table mb-0">
        <thead>
          <tr><th>ID</th><th>Exam</th><th>Course</th><th>Type</th><th>Examiner</th><th>Booking period</th><th>Slots</th><th>Status</th><th></th></tr>
        </thead>
        <tbody>
          <tr v-for="exam in exams" :key="exam.id">
            <td>{{ exam.id }}</td>
            <td class="fw-semibold">{{ exam.name }}</td>
            <td>{{ exam.course_code }}</td>
            <td>{{ exam.exam_type }}</td>
            <td>{{ exam.examiner_name }}</td>
            <td class="small">{{ exam.booking_start }} to {{ exam.booking_end }}</td>
            <td>{{ exam.slot_count }}</td>
            <td><StatusBadge :text="exam.status" /></td>
            <td class="text-end"><router-link :to="`/admin/exams/${exam.id}`" class="btn btn-sm btn-primary">Manage</router-link></td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else class="text-muted mb-0">No examinations found.</p>
  </div></div>
</template>

<script>
import api from "../../api";

export default {
  data() {
    return {
      q: "", // search text
      exams: [],
    };
  },

  created() {
    this.load();
  },

  methods: {
    load() {
      api.get("/admin/exams", { params: { q: this.q } }).then((res) => {
        this.exams = res.data.exams;
      });
    },
  },
};
</script>
