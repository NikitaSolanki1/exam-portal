<template>
  <div class="hero mb-4">
    <h1 class="fw-bold">Examination Management Portal</h1>
    <p class="lead mb-4">
      Schedule vivas, practicals and project demos. Book slots, evaluate with rubrics and publish results, all in one place.
    </p>
    <router-link to="/login" class="btn btn-light btn-lg me-2">Login</router-link>
    <router-link to="/register" class="btn btn-outline-light btn-lg">Register</router-link>
  </div>

  <div class="row g-3">
    <div class="col-md-4">
      <div class="card h-100"><div class="card-body">
        <div class="fs-2 text-primary"><i class="bi bi-shield-lock"></i></div>
        <h5 class="card-title">Admin</h5>
        <p class="text-muted mb-0">Creates courses, exams and rubrics, approves examiners, opens slot creation and booking, and publishes results.</p>
      </div></div>
    </div>
    <div class="col-md-4">
      <div class="card h-100"><div class="card-body">
        <div class="fs-2 text-primary"><i class="bi bi-person-badge"></i></div>
        <h5 class="card-title">Examiner</h5>
        <p class="text-muted mb-0">Creates exam slots, sees the students booked into them, and gives marks and remarks using the rubric.</p>
      </div></div>
    </div>
    <div class="col-md-4">
      <div class="card h-100"><div class="card-body">
        <div class="fs-2 text-primary"><i class="bi bi-mortarboard"></i></div>
        <h5 class="card-title">Student</h5>
        <p class="text-muted mb-0">Finds exams, books or cancels a slot, sees the exam schedule, and views published results and feedback.</p>
      </div></div>
    </div>
  </div>
</template>

<script>
export default {
  created() {
    // A logged-in user goes straight to their own dashboard
    if (this.$root.user) {
      this.$router.replace("/" + this.$root.user.role);
    }
  },
};
</script>
