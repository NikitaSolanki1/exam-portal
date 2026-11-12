<template>
  <h3 class="page-title mb-4">Hi, {{ $root.user.name }}</h3>

  <div class="row g-3 mb-4">
    <div class="col-6 col-md-3"><div class="card stat-card h-100"><div class="card-body">
      <div class="icon mb-2"><i class="bi bi-clipboard-check"></i></div>
      <div class="value">{{ open_exams.length }}</div><div class="text-muted small">Exams open for booking</div>
    </div></div></div>
    <div class="col-6 col-md-3"><div class="card stat-card h-100"><div class="card-body">
      <div class="icon mb-2"><i class="bi bi-calendar-week"></i></div>
      <div class="value">{{ free_slots }}</div><div class="text-muted small">Available slots</div>
    </div></div></div>
    <div class="col-6 col-md-3"><div class="card stat-card h-100"><div class="card-body">
      <div class="icon mb-2"><i class="bi bi-bookmark-check"></i></div>
      <div class="value">{{ booked_count }}</div><div class="text-muted small">Booked slots</div>
    </div></div></div>
    <div class="col-6 col-md-3"><div class="card stat-card h-100"><div class="card-body">
      <div class="icon mb-2"><i class="bi bi-award"></i></div>
      <div class="value">{{ results.length }}</div><div class="text-muted small">Published results</div>
    </div></div></div>
  </div>

  <div class="row g-3">
    <div class="col-lg-6">
      <div class="card mb-3"><div class="card-body">
        <h5 class="card-title mb-3">Upcoming exams</h5>
        <div v-for="b in upcoming" :key="b.id" class="d-flex justify-content-between align-items-center border-bottom py-2">
          <div>
            <div class="fw-semibold">{{ b.exam_name }} <span class="small text-muted">({{ b.course_code }})</span></div>
            <div class="small text-muted">{{ b.slot_date }} · {{ b.start_time }} – {{ b.end_time }} · {{ b.examiner_name }}</div>
          </div>
          <StatusBadge text="Booked" />
        </div>
        <p v-if="upcoming.length === 0" class="text-muted mb-0">
          No upcoming exams. <router-link to="/student/exams">Book a slot</router-link>.
        </p>
      </div></div>

      <div class="card"><div class="card-body">
        <h5 class="card-title mb-3">Published results</h5>
        <div v-for="b in results" :key="b.id" class="d-flex justify-content-between align-items-center border-bottom py-2">
          <div class="fw-semibold">{{ b.exam_name }}</div>
          <span class="fw-bold">{{ b.total_marks }} / {{ b.max_marks }}</span>
        </div>
        <p v-if="results.length === 0" class="text-muted mb-0">No results published yet.</p>
        <router-link v-else to="/student/results" class="btn btn-sm btn-outline-primary mt-3">See marks and feedback</router-link>
      </div></div>
    </div>

    <div class="col-lg-6">
      <div class="card h-100"><div class="card-body">
        <h5 class="card-title mb-3">Exams open for booking</h5>
        <div v-for="exam in open_exams" :key="exam.id" class="d-flex justify-content-between align-items-center border-bottom py-2">
          <div>
            <div class="fw-semibold">{{ exam.name }} <span class="small text-muted">({{ exam.course_code }})</span></div>
            <div class="small text-muted">{{ exam.exam_type }} · book before {{ exam.booking_end }}</div>
          </div>
          <router-link :to="`/student/exams/${exam.id}`" class="btn btn-sm btn-primary">View slots</router-link>
        </div>
        <p v-if="open_exams.length === 0" class="text-muted mb-0">No exams are open for booking right now.</p>
      </div></div>
    </div>
  </div>
</template>

<script>
import api from "../../api";

export default {
  data() {
    return {
      upcoming: [],
      results: [],
      open_exams: [],
      free_slots: 0,
      booked_count: 0,
    };
  },

  created() {
    api.get("/student/dashboard").then((res) => {
      this.upcoming = res.data.upcoming;
      this.results = res.data.results;
      this.open_exams = res.data.open_exams;
      this.free_slots = res.data.free_slots;
      this.booked_count = res.data.booked_count;
    });
  },
};
</script>
