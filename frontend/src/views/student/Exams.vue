<!-- All exams, with search and filters -->
<template>
  <h3 class="page-title mb-3">Examinations</h3>

  <div class="card mb-3"><div class="card-body">
    <form class="row g-2" @submit.prevent="load">
      <div class="col-md-5"><input v-model="q" class="form-control" placeholder="Search by exam or course name" /></div>
      <div class="col-md-3">
        <select v-model="course" class="form-select">
          <option value="">All courses</option>
          <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.code }} – {{ c.name }}</option>
        </select>
      </div>
      <div class="col-md-2">
        <select v-model="type" class="form-select">
          <option value="">All types</option>
          <option v-for="t in exam_types" :key="t">{{ t }}</option>
        </select>
      </div>
      <div class="col-md-2 d-grid"><button class="btn btn-primary">Search</button></div>
    </form>
  </div></div>

  <div class="row g-3">
    <div v-for="exam in exams" :key="exam.id" class="col-md-6 col-xl-4">
      <div class="card h-100"><div class="card-body d-flex flex-column">
        <div class="d-flex justify-content-between align-items-start mb-2">
          <span class="small text-muted">{{ exam.course_code }} · {{ exam.exam_type }}</span>
          <StatusBadge :text="exam.status" />
        </div>
        <h5 class="card-title">{{ exam.name }}</h5>
        <p class="small text-muted mb-3">
          {{ exam.duration }} min · {{ exam.max_marks }} marks · Examiner: {{ exam.examiner_name }}<br />
          Booking: {{ exam.booking_start }} to {{ exam.booking_end }}
        </p>
        <div class="mt-auto d-flex justify-content-between align-items-center">
          <span v-if="booked_ids.includes(exam.id)" class="badge status-booked"><i class="bi bi-check2"></i> You booked this</span>
          <span v-else></span>
          <router-link :to="`/student/exams/${exam.id}`" class="btn btn-sm btn-primary">View slots</router-link>
        </div>
      </div></div>
    </div>

    <div v-if="exams.length === 0" class="col-12">
      <div class="card"><div class="card-body text-muted">No examinations match your search.</div></div>
    </div>
  </div>
</template>

<script>
import api from "../../api";

export default {
  data() {
    return {
      q: "", // search text
      course: "", // course filter
      type: "", // exam type filter
      exams: [],
      courses: [],
      exam_types: [],
      booked_ids: [], // ids of exams this student has already booked
    };
  },

  created() {
    this.load();
  },

  methods: {
    load() {
      api.get("/student/exams", { params: { q: this.q, course: this.course, type: this.type } }).then((res) => {
        this.exams = res.data.exams;
        this.courses = res.data.courses;
        this.exam_types = res.data.exam_types;
        this.booked_ids = res.data.booked_ids;
      });
    },
  },
};
</script>
