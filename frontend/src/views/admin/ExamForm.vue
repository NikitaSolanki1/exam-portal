<!-- The same page is used to add a new exam and to edit an old one -->
<template>
  <div class="card mx-auto" style="max-width: 820px"><div class="card-body p-4">
    <h4 class="fw-bold mb-3">{{ examId ? "Edit examination" : "Add an examination" }}</h4>

    <div v-if="loaded && (courses.length === 0 || examiners.length === 0)" class="alert alert-warning">
      You need at least one course and one approved examiner before adding an exam.
    </div>

    <form @submit.prevent="save">
      <div class="row g-3">
        <div class="col-md-6">
          <label class="form-label">Course</label>
          <select v-model="form.course_id" class="form-select" required>
            <option v-for="course in courses" :key="course.id" :value="course.id">{{ course.code }} – {{ course.name }}</option>
          </select>
        </div>
        <div class="col-md-6">
          <label class="form-label">Examination name</label>
          <input v-model="form.name" class="form-control" placeholder="Viva 1" required />
        </div>
        <div class="col-md-4">
          <label class="form-label">Type</label>
          <select v-model="form.exam_type" class="form-select">
            <option v-for="type in exam_types" :key="type">{{ type }}</option>
          </select>
        </div>
        <div class="col-md-4">
          <label class="form-label">Duration (minutes)</label>
          <input type="number" v-model="form.duration" min="1" class="form-control" required />
        </div>
        <div class="col-md-4">
          <label class="form-label">Maximum marks</label>
          <input type="number" v-model="form.max_marks" min="1" class="form-control" required />
        </div>
        <div class="col-12">
          <label class="form-label">Assigned examiner</label>
          <select v-model="form.examiner_id" class="form-select" required>
            <option v-for="user in examiners" :key="user.id" :value="user.id">{{ user.name }} ({{ user.department || "No department" }})</option>
          </select>
          <div v-if="examId" class="form-text">Changing the examiner also moves this exam's slots to the new examiner.</div>
        </div>

        <div class="col-md-6">
          <div class="border rounded-3 p-3">
            <div class="fw-semibold mb-2"><i class="bi bi-calendar-plus"></i> Slot creation period (examiner)</div>
            <div class="row g-2">
              <div class="col"><label class="form-label small">Start</label><input type="date" v-model="form.slot_start" class="form-control" required /></div>
              <div class="col"><label class="form-label small">End</label><input type="date" v-model="form.slot_end" class="form-control" required /></div>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="border rounded-3 p-3">
            <div class="fw-semibold mb-2"><i class="bi bi-calendar-check"></i> Slot booking period (student)</div>
            <div class="row g-2">
              <div class="col"><label class="form-label small">Start</label><input type="date" v-model="form.booking_start" class="form-control" required /></div>
              <div class="col"><label class="form-label small">End (deadline)</label><input type="date" v-model="form.booking_end" class="form-control" required /></div>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-4">
        <button class="btn btn-primary">Save examination</button>
        <router-link :to="examId ? `/admin/exams/${examId}` : '/admin/exams'" class="btn btn-link">Cancel</router-link>
      </div>
    </form>
  </div></div>
</template>

<script>
import api from "../../api";

export default {
  data() {
    return {
      examId: this.$route.params.id, // empty when adding a new exam
      loaded: false,
      courses: [],
      examiners: [],
      exam_types: [],
      form: {
        course_id: "", examiner_id: "", name: "", exam_type: "Viva", duration: 20, max_marks: 20,
        slot_start: "", slot_end: "", booking_start: "", booking_end: "",
      },
    };
  },

  created() {
    // The lists for the drop-downs
    api.get("/admin/exam-form").then((res) => {
      this.courses = res.data.courses;
      this.examiners = res.data.examiners;
      this.exam_types = res.data.exam_types;
      this.loaded = true;
    });
    // When editing, fill the form with the exam's current values
    if (this.examId) {
      api.get(`/admin/exams/${this.examId}`).then((res) => {
        this.form = res.data.exam;
      });
    }
  },

  methods: {
    save() {
      let request;
      if (this.examId) {
        request = api.put(`/admin/exams/${this.examId}`, this.form);
      } else {
        request = api.post("/admin/exams", this.form);
      }
      request.then((res) => {
        this.$root.showMessage(res.data.message);
        this.$router.push(`/admin/exams/${res.data.id}`);
      });
    },
  },
};
</script>
