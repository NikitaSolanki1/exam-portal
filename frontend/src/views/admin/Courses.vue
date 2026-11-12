<template>
  <div class="d-flex justify-content-between align-items-center mb-3">
    <h3 class="page-title mb-0">Courses</h3>
    <router-link to="/admin/courses/new" class="btn btn-primary"><i class="bi bi-plus-lg"></i> Add course</router-link>
  </div>

  <div class="card"><div class="card-body">
    <div v-if="courses.length" class="table-responsive">
      <table class="table mb-0">
        <thead><tr><th>ID</th><th>Code</th><th>Name</th><th>Description</th><th>Exams</th><th>Status</th><th></th></tr></thead>
        <tbody>
          <tr v-for="course in courses" :key="course.id">
            <td>{{ course.id }}</td>
            <td class="fw-semibold">{{ course.code }}</td>
            <td>{{ course.name }}</td>
            <td class="text-muted small">{{ course.description }}</td>
            <td>{{ course.exam_count }}</td>
            <td><StatusBadge :text="course.status" /></td>
            <td class="text-end text-nowrap">
              <router-link :to="`/admin/courses/${course.id}/edit`" class="btn btn-sm btn-outline-primary me-1">Edit</router-link>
              <button class="btn btn-sm btn-outline-danger" @click="deleteCourse(course)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else class="text-muted mb-0">No courses yet. Add the first one.</p>
  </div></div>
</template>

<script>
import api from "../../api";

export default {
  data() {
    return {
      courses: [],
    };
  },

  created() {
    this.load();
  },

  methods: {
    load() {
      api.get("/admin/courses").then((res) => {
        this.courses = res.data.courses;
      });
    },

    deleteCourse(course) {
      if (!confirm(`Delete ${course.code}? Its exams, slots and bookings will be deleted too.`)) {
        return;
      }
      api.delete(`/admin/courses/${course.id}`).then((res) => {
        this.$root.showMessage(res.data.message);
        this.load();
      });
    },
  },
};
</script>
