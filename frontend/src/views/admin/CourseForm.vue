<!-- The same page is used to add a new course and to edit an old one -->
<template>
  <div class="card mx-auto" style="max-width: 640px"><div class="card-body p-4">
    <h4 class="fw-bold mb-3">{{ courseId ? "Edit course" : "Add a course" }}</h4>

    <form @submit.prevent="save">
      <div class="row g-3">
        <div class="col-md-4">
          <label class="form-label">Course code</label>
          <input v-model="form.code" class="form-control" placeholder="MAD1" required />
        </div>
        <div class="col-md-8">
          <label class="form-label">Course name</label>
          <input v-model="form.name" class="form-control" required />
        </div>
        <div class="col-12">
          <label class="form-label">Description</label>
          <textarea v-model="form.description" class="form-control" rows="3"></textarea>
        </div>
        <div class="col-md-4">
          <label class="form-label">Status</label>
          <select v-model="form.status" class="form-select">
            <option>Active</option>
            <option>Inactive</option>
          </select>
        </div>
      </div>
      <div class="mt-4">
        <button class="btn btn-primary">Save course</button>
        <router-link to="/admin/courses" class="btn btn-link">Cancel</router-link>
      </div>
    </form>
  </div></div>
</template>

<script>
import api from "../../api";

export default {
  data() {
    return {
      courseId: this.$route.params.id, // empty when adding a new course
      form: { code: "", name: "", description: "", status: "Active" },
    };
  },

  created() {
    if (this.courseId) {
      api.get(`/admin/courses/${this.courseId}`).then((res) => {
        this.form = res.data.course;
      });
    }
  },

  methods: {
    save() {
      let request;
      if (this.courseId) {
        request = api.put(`/admin/courses/${this.courseId}`, this.form);
      } else {
        request = api.post("/admin/courses", this.form);
      }
      request.then((res) => {
        this.$root.showMessage(res.data.message);
        this.$router.push("/admin/courses");
      });
    },
  },
};
</script>
