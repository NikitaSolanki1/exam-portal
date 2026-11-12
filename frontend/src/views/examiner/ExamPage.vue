<!-- One exam: create slots and see the students booked into them -->
<template>
  <div v-if="exam">
    <div class="mb-3">
      <div class="text-muted small">{{ exam.course_code }} · {{ exam.course_name }}</div>
      <h3 class="page-title mb-1">{{ exam.name }}</h3>
      <StatusBadge :text="exam.status" />
      <span class="text-muted small ms-2">{{ exam.exam_type }} · {{ exam.duration }} min · {{ exam.max_marks }} marks</span>
    </div>

    <div class="row g-3">
      <div class="col-lg-4">
        <div class="card"><div class="card-body">
          <h5 class="card-title">Create a slot</h5>
          <p class="small text-muted">Slot creation period: {{ exam.slot_start }} to {{ exam.slot_end }}</p>

          <form v-if="can_create" @submit.prevent="createSlot">
            <div class="mb-2">
              <label class="form-label small">Date</label>
              <input type="date" v-model="form.date" class="form-control" :min="today" required />
            </div>
            <div class="row g-2 mb-2">
              <div class="col"><label class="form-label small">Start time</label><input type="time" v-model="form.start_time" class="form-control" required /></div>
              <div class="col"><label class="form-label small">End time</label><input type="time" v-model="form.end_time" class="form-control" required /></div>
            </div>
            <div class="mb-3">
              <label class="form-label small">Maximum students</label>
              <input type="number" v-model="form.capacity" min="1" class="form-control" required />
            </div>
            <button class="btn btn-primary w-100">Create slot</button>
          </form>

          <div v-else class="alert alert-secondary small mb-0">
            Slot creation is closed. You can add slots only after the admin opens slot creation, and before {{ exam.slot_end }}.
          </div>
        </div></div>
      </div>

      <div class="col-lg-8">
        <div class="card"><div class="card-body">
          <h5 class="card-title mb-3">My slots and booked students</h5>

          <div v-for="slot in slots" :key="slot.id" class="border rounded-3 p-3 mb-3">
            <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
              <div>
                <span class="fw-semibold">{{ slot.date }}</span>
                <span class="text-muted"> · {{ slot.start_time }} – {{ slot.end_time }}</span>
                <StatusBadge :text="slot.status" class="ms-1" />
                <span class="small text-muted ms-1">{{ slot.available_seats }} of {{ slot.capacity }} seats free</span>
              </div>
              <!-- A slot can be changed only before booking opens, and only if nobody booked it -->
              <div v-if="['Draft', 'Slot Creation'].includes(exam.status) && !slot.has_bookings" class="d-flex gap-1">
                <router-link :to="`/examiner/slots/${slot.id}/edit`" class="btn btn-sm btn-outline-primary">Edit</router-link>
                <button class="btn btn-sm btn-outline-danger" @click="deleteSlot(slot.id)">Remove</button>
              </div>
            </div>

            <div v-for="b in slot.bookings" :key="b.id" class="d-flex justify-content-between align-items-center border-top mt-2 pt-2">
              <div>
                <i class="bi bi-person"></i> {{ b.student_name }} <span class="small text-muted">{{ b.student_email }}</span>
                <StatusBadge :text="b.status" class="ms-1" />
                <span v-if="b.total_marks !== null" class="small ms-1">{{ b.total_marks }} / {{ exam.max_marks }}</span>
              </div>
              <router-link :to="`/examiner/bookings/${b.id}/evaluate`" class="btn btn-sm" :class="b.status === 'Completed' ? 'btn-outline-success' : 'btn-success'">
                {{ b.status === "Completed" ? "Edit marks" : "Evaluate" }}
              </router-link>
            </div>
            <div v-if="slot.bookings.length === 0" class="small text-muted mt-2">No students booked yet.</div>
          </div>

          <p v-if="slots.length === 0" class="text-muted mb-0">You have not created any slots for this exam yet.</p>
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
      slots: [],
      can_create: false,
      today: "",
      form: { date: "", start_time: "", end_time: "", capacity: 1 },
    };
  },

  created() {
    this.load();
  },

  methods: {
    load() {
      api.get(`/examiner/exams/${this.examId}`).then((res) => {
        this.exam = res.data.exam;
        this.slots = res.data.slots;
        this.can_create = res.data.can_create;
        this.today = res.data.today;
      });
    },

    createSlot() {
      api.post(`/examiner/exams/${this.examId}/slots`, this.form).then((res) => {
        this.$root.showMessage(res.data.message);
        this.form = { date: "", start_time: "", end_time: "", capacity: 1 };
        this.load();
      });
    },

    deleteSlot(slotId) {
      if (!confirm("Remove this slot?")) {
        return;
      }
      api.delete(`/examiner/slots/${slotId}`).then((res) => {
        this.$root.showMessage(res.data.message);
        this.load();
      });
    },
  },
};
</script>
