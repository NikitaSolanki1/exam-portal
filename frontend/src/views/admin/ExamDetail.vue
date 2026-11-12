<template>
  <div v-if="exam">
    <div class="d-flex justify-content-between align-items-start mb-3 flex-wrap gap-2">
      <div>
        <div class="text-muted small">{{ exam.course_code }} · {{ exam.course_name }}</div>
        <h3 class="page-title mb-1">{{ exam.name }}</h3>
        <StatusBadge :text="exam.status" />
        <span v-if="exam.results_published" class="badge status-published ms-1">Results published</span>
      </div>
      <div class="d-flex gap-2">
        <router-link :to="`/admin/exams/${exam.id}/edit`" class="btn btn-outline-primary"><i class="bi bi-pencil"></i> Edit</router-link>
        <button class="btn btn-outline-danger" @click="deleteExam"><i class="bi bi-trash"></i> Delete</button>
      </div>
    </div>

    <div class="row g-3">
      <!-- Left: details and controls -->
      <div class="col-lg-4">
        <div class="card mb-3"><div class="card-body">
          <h5 class="card-title">Details</h5>
          <dl class="row mb-0 small">
            <dt class="col-6 text-muted">Type</dt><dd class="col-6">{{ exam.exam_type }}</dd>
            <dt class="col-6 text-muted">Duration</dt><dd class="col-6">{{ exam.duration }} min</dd>
            <dt class="col-6 text-muted">Maximum marks</dt><dd class="col-6">{{ exam.max_marks }}</dd>
            <dt class="col-6 text-muted">Examiner</dt><dd class="col-6">{{ exam.examiner_name }}</dd>
            <dt class="col-6 text-muted">Slot creation</dt><dd class="col-6">{{ exam.slot_start }} to {{ exam.slot_end }}</dd>
            <dt class="col-6 text-muted">Booking</dt><dd class="col-6 mb-0">{{ exam.booking_start }} to {{ exam.booking_end }}</dd>
          </dl>
        </div></div>

        <div class="card"><div class="card-body">
          <h5 class="card-title">Exam controls</h5>
          <p class="small text-muted">Draft → Slot Creation → Booking Open → Closed → Completed</p>
          <div class="d-grid gap-2">
            <button v-if="exam.status === 'Draft'" class="btn btn-warning" @click="changeStatus('Slot Creation')">Open slot creation for examiner</button>
            <button v-if="exam.status === 'Slot Creation'" class="btn btn-outline-secondary" @click="changeStatus('Draft')">Close slot creation</button>
            <button v-if="['Draft', 'Slot Creation', 'Closed'].includes(exam.status)" class="btn btn-success" @click="changeStatus('Booking Open')">Open booking for students</button>
            <button v-if="exam.status === 'Booking Open'" class="btn btn-danger" @click="changeStatus('Closed')">Close student booking</button>
            <button v-if="exam.status === 'Closed'" class="btn btn-primary" @click="changeStatus('Completed')">Mark exam completed</button>
            <button v-if="['Closed', 'Completed'].includes(exam.status)" class="btn" :class="exam.results_published ? 'btn-outline-secondary' : 'btn-primary'" @click="togglePublish">
              {{ exam.results_published ? "Hide results" : "Publish results to students" }}
            </button>
          </div>
        </div></div>
      </div>

      <!-- Right: rubric, slots and bookings -->
      <div class="col-lg-8">
        <div class="card mb-3"><div class="card-body">
          <h5 class="card-title">Rubric</h5>
          <table class="table">
            <thead><tr><th>Criterion</th><th>Description</th><th>Max marks</th><th>Weightage</th><th></th></tr></thead>
            <tbody>
              <tr v-for="rubric in rubrics" :key="rubric.id">
                <td class="fw-semibold">{{ rubric.criterion }}</td>
                <td class="small text-muted">{{ rubric.description }}</td>
                <td>{{ rubric.max_marks }}</td>
                <td>{{ rubric.weightage }}%</td>
                <td class="text-end">
                  <button class="btn btn-sm btn-outline-danger" @click="deleteRubric(rubric.id)"><i class="bi bi-trash"></i></button>
                </td>
              </tr>
              <tr v-if="rubrics.length === 0">
                <td colspan="5" class="text-muted">No criteria yet. Examiners need a rubric to give marks.</td>
              </tr>
            </tbody>
          </table>
          <form class="row g-2" @submit.prevent="addRubric">
            <div class="col-md-4"><input v-model="rubricForm.criterion" class="form-control" placeholder="Criterion, e.g. Concepts" required /></div>
            <div class="col-md-2"><input type="number" v-model="rubricForm.max_marks" min="1" class="form-control" placeholder="Marks" required /></div>
            <div class="col-md-4"><input v-model="rubricForm.description" class="form-control" placeholder="Description" /></div>
            <div class="col-md-2 d-grid"><button class="btn btn-primary">Add</button></div>
          </form>
        </div></div>

        <div class="card mb-3"><div class="card-body">
          <h5 class="card-title">Slots created by the examiner</h5>
          <div v-if="slots.length" class="table-responsive">
            <table class="table mb-0">
              <thead><tr><th>Date</th><th>Time</th><th>Capacity</th><th>Seats left</th><th>Status</th></tr></thead>
              <tbody>
                <tr v-for="slot in slots" :key="slot.id">
                  <td>{{ slot.date }}</td>
                  <td>{{ slot.start_time }} – {{ slot.end_time }}</td>
                  <td>{{ slot.capacity }}</td>
                  <td>{{ slot.available_seats }}</td>
                  <td><StatusBadge :text="slot.status" /></td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="text-muted mb-0">No slots yet. Open slot creation so the examiner can add them.</p>
        </div></div>

        <div class="card"><div class="card-body">
          <h5 class="card-title">Bookings</h5>
          <div v-if="bookings.length" class="table-responsive">
            <table class="table mb-0">
              <thead><tr><th>ID</th><th>Student</th><th>Slot</th><th>Status</th><th>Marks</th><th></th></tr></thead>
              <tbody>
                <tr v-for="b in bookings" :key="b.id">
                  <td>{{ b.id }}</td>
                  <td>{{ b.student_name }}</td>
                  <td class="small">{{ b.slot_date }}, {{ b.start_time }}</td>
                  <td><StatusBadge :text="b.status" /></td>
                  <td>{{ b.total_marks ?? "–" }} / {{ exam.max_marks }}</td>
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
          <p v-else class="text-muted mb-0">No bookings yet.</p>
        </div></div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../../api";

export default {
  data() {
    return {
      examId: this.$route.params.id,
      exam: null,
      rubrics: [],
      slots: [],
      bookings: [],
      rubricForm: { criterion: "", max_marks: "", description: "" },
    };
  },

  created() {
    this.load();
  },

  methods: {
    load() {
      api.get(`/admin/exams/${this.examId}`).then((res) => {
        this.exam = res.data.exam;
        this.rubrics = res.data.rubrics;
        this.slots = res.data.slots;
        this.bookings = res.data.bookings;
      });
    },

    changeStatus(status) {
      api.put(`/admin/exams/${this.examId}/status`, { status: status }).then((res) => {
        this.$root.showMessage(res.data.message);
        this.load();
      });
    },

    togglePublish() {
      api.put(`/admin/exams/${this.examId}/publish`).then((res) => {
        this.$root.showMessage(res.data.message);
        this.load();
      });
    },

    deleteExam() {
      if (!confirm("Delete this exam? Its rubric, slots and bookings will be deleted too.")) {
        return;
      }
      api.delete(`/admin/exams/${this.examId}`).then((res) => {
        this.$root.showMessage(res.data.message);
        this.$router.push("/admin/exams");
      });
    },

    addRubric() {
      api.post(`/admin/exams/${this.examId}/rubrics`, this.rubricForm).then((res) => {
        this.$root.showMessage(res.data.message);
        this.rubricForm = { criterion: "", max_marks: "", description: "" };
        this.load();
      });
    },

    deleteRubric(rubricId) {
      api.delete(`/admin/rubrics/${rubricId}`).then((res) => {
        this.$root.showMessage(res.data.message);
        this.load();
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
