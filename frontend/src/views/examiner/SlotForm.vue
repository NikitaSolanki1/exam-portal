<template>
  <div class="card auth-card"><div class="card-body p-4">
    <h4 class="fw-bold mb-1">Edit slot</h4>
    <p class="text-muted">{{ form.exam_name }}</p>

    <form @submit.prevent="save">
      <div class="mb-3">
        <label class="form-label">Date</label>
        <input type="date" v-model="form.date" class="form-control" required />
      </div>
      <div class="row g-2 mb-3">
        <div class="col"><label class="form-label">Start time</label><input type="time" v-model="form.start_time" class="form-control" required /></div>
        <div class="col"><label class="form-label">End time</label><input type="time" v-model="form.end_time" class="form-control" required /></div>
      </div>
      <div class="mb-3">
        <label class="form-label">Maximum students</label>
        <input type="number" v-model="form.capacity" min="1" class="form-control" required />
      </div>
      <button class="btn btn-primary">Save slot</button>
      <router-link :to="`/examiner/exams/${form.exam_id}`" class="btn btn-link">Cancel</router-link>
    </form>
  </div></div>
</template>

<script>
import api from "../../api";

export default {
  data() {
    return {
      slotId: this.$route.params.id,
      form: { exam_id: "", exam_name: "", date: "", start_time: "", end_time: "", capacity: 1 },
    };
  },

  created() {
    api.get(`/examiner/slots/${this.slotId}`).then((res) => {
      this.form = res.data.slot;
    });
  },

  methods: {
    save() {
      api.put(`/examiner/slots/${this.slotId}`, this.form).then((res) => {
        this.$root.showMessage(res.data.message);
        this.$router.push(`/examiner/exams/${this.form.exam_id}`);
      });
    },
  },
};
</script>
