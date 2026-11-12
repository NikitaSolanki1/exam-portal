<template>
  <h3 class="page-title mb-3">My results</h3>

  <div class="row g-3">
    <div v-for="b in results" :key="b.id" class="col-lg-6">
      <div class="card h-100"><div class="card-body">
        <div class="d-flex justify-content-between align-items-start mb-2">
          <div>
            <div class="small text-muted">{{ b.course_code }} · {{ b.exam_type }} · {{ b.slot_date }}</div>
            <h5 class="card-title mb-0">{{ b.exam_name }}</h5>
          </div>
          <div class="fs-3 fw-bold text-primary">{{ b.total_marks }}<span class="fs-6 text-muted"> / {{ b.max_marks }}</span></div>
        </div>

        <table class="table table-sm">
          <thead><tr><th>Criterion</th><th class="text-end">Marks</th></tr></thead>
          <tbody>
            <tr v-for="mark in b.marks" :key="mark.criterion">
              <td>{{ mark.criterion }}</td>
              <td class="text-end">{{ mark.marks }} / {{ mark.max_marks }}</td>
            </tr>
          </tbody>
        </table>
        <div class="small"><span class="fw-semibold">Examiner remarks ({{ b.examiner_name }}):</span> {{ b.remarks }}</div>
      </div></div>
    </div>

    <div v-if="results.length === 0" class="col-12">
      <div class="card"><div class="card-body text-muted">No results have been published for you yet.</div></div>
    </div>
  </div>
</template>

<script>
import api from "../../api";

export default {
  data() {
    return {
      results: [],
    };
  },

  created() {
    api.get("/student/results").then((res) => {
      this.results = res.data.results;
    });
  },
};
</script>
