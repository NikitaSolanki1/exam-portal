<template>
  <h3 class="page-title mb-4">Welcome, {{ $root.user.name }}</h3>

  <div class="row g-3 mb-4">
    <div class="col-6 col-md-3"><div class="card stat-card h-100"><div class="card-body">
      <div class="icon mb-2"><i class="bi bi-clipboard-check"></i></div>
      <div class="value">{{ exams.length }}</div><div class="text-muted small">Assigned exams</div>
    </div></div></div>
    <div class="col-6 col-md-3"><div class="card stat-card h-100"><div class="card-body">
      <div class="icon mb-2"><i class="bi bi-calendar-week"></i></div>
      <div class="value">{{ slot_count }}</div><div class="text-muted small">Slots created</div>
    </div></div></div>
    <div class="col-6 col-md-3"><div class="card stat-card h-100"><div class="card-body">
      <div class="icon mb-2"><i class="bi bi-people"></i></div>
      <div class="value">{{ booked_count }}</div><div class="text-muted small">Students booked</div>
    </div></div></div>
    <div class="col-6 col-md-3"><div class="card stat-card h-100"><div class="card-body">
      <div class="icon mb-2"><i class="bi bi-hourglass-split"></i></div>
      <div class="value">{{ pending.length }}</div><div class="text-muted small">Pending evaluations</div>
    </div></div></div>
  </div>

  <div class="row g-3">
    <div class="col-lg-7">
      <div class="card h-100"><div class="card-body">
        <h5 class="card-title mb-3">My assigned exams</h5>
        <div v-if="exams.length" class="table-responsive">
          <table class="table mb-0">
            <thead><tr><th>Exam</th><th>Slot creation</th><th>Slots</th><th>Status</th><th></th></tr></thead>
            <tbody>
              <tr v-for="exam in exams" :key="exam.id">
                <td>
                  <div class="fw-semibold">{{ exam.name }}</div>
                  <div class="small text-muted">{{ exam.course_code }} · {{ exam.exam_type }}</div>
                </td>
                <td class="small">{{ exam.slot_start }} to {{ exam.slot_end }}</td>
                <td>{{ exam.slot_count }}</td>
                <td><StatusBadge :text="exam.status" /></td>
                <td class="text-end"><router-link :to="`/examiner/exams/${exam.id}`" class="btn btn-sm btn-primary">Open</router-link></td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="text-muted mb-0">The admin has not assigned any exams to you yet.</p>
      </div></div>
    </div>

    <div class="col-lg-5">
      <div class="card h-100"><div class="card-body">
        <h5 class="card-title mb-3">Pending evaluations</h5>
        <div v-for="b in pending" :key="b.id" class="d-flex justify-content-between align-items-center border-bottom py-2">
          <div>
            <div class="fw-semibold">{{ b.student_name }}</div>
            <div class="small text-muted">{{ b.exam_name }} · {{ b.slot_date }}, {{ b.start_time }}</div>
          </div>
          <router-link :to="`/examiner/bookings/${b.id}/evaluate`" class="btn btn-sm btn-success">Evaluate</router-link>
        </div>
        <p v-if="pending.length === 0" class="text-muted mb-0">Nothing to evaluate right now.</p>
      </div></div>
    </div>
  </div>
</template>

<script>
import api from "../../api";

export default {
  data() {
    return {
      exams: [],
      slot_count: 0,
      booked_count: 0,
      pending: [], // booked students who are not evaluated yet
    };
  },

  created() {
    api.get("/examiner/dashboard").then((res) => {
      this.exams = res.data.exams;
      this.slot_count = res.data.slot_count;
      this.booked_count = res.data.booked_count;
      this.pending = res.data.pending;
    });
  },
};
</script>
