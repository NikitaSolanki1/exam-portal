import { createRouter, createWebHistory } from "vue-router";

// meta.role says who can open a page. "any" means any logged-in user.
const routes = [
  { path: "/", component: () => import("./views/Home.vue") },
  { path: "/login", component: () => import("./views/Login.vue") },
  { path: "/register", component: () => import("./views/Register.vue") },
  { path: "/profile", component: () => import("./views/Profile.vue"), meta: { role: "any" } },

  // Admin pages
  { path: "/admin", component: () => import("./views/admin/Dashboard.vue"), meta: { role: "admin" } },
  { path: "/admin/courses", component: () => import("./views/admin/Courses.vue"), meta: { role: "admin" } },
  { path: "/admin/courses/new", component: () => import("./views/admin/CourseForm.vue"), meta: { role: "admin" } },
  { path: "/admin/courses/:id/edit", component: () => import("./views/admin/CourseForm.vue"), meta: { role: "admin" } },
  { path: "/admin/exams", component: () => import("./views/admin/Exams.vue"), meta: { role: "admin" } },
  { path: "/admin/exams/new", component: () => import("./views/admin/ExamForm.vue"), meta: { role: "admin" } },
  { path: "/admin/exams/:id", component: () => import("./views/admin/ExamDetail.vue"), meta: { role: "admin" } },
  { path: "/admin/exams/:id/edit", component: () => import("./views/admin/ExamForm.vue"), meta: { role: "admin" } },
  { path: "/admin/examiners", component: () => import("./views/admin/Examiners.vue"), meta: { role: "admin" } },
  { path: "/admin/students", component: () => import("./views/admin/Students.vue"), meta: { role: "admin" } },
  { path: "/admin/slots", component: () => import("./views/admin/Slots.vue"), meta: { role: "admin" } },
  { path: "/admin/bookings", component: () => import("./views/admin/Bookings.vue"), meta: { role: "admin" } },
  { path: "/admin/bookings/:id/reschedule", component: () => import("./views/admin/Reschedule.vue"), meta: { role: "admin" } },

  // Examiner pages
  { path: "/examiner", component: () => import("./views/examiner/Dashboard.vue"), meta: { role: "examiner" } },
  { path: "/examiner/exams/:id", component: () => import("./views/examiner/ExamPage.vue"), meta: { role: "examiner" } },
  { path: "/examiner/slots/:id/edit", component: () => import("./views/examiner/SlotForm.vue"), meta: { role: "examiner" } },
  { path: "/examiner/bookings/:id/evaluate", component: () => import("./views/examiner/Evaluate.vue"), meta: { role: "examiner" } },

  // Student pages
  { path: "/student", component: () => import("./views/student/Dashboard.vue"), meta: { role: "student" } },
  { path: "/student/exams", component: () => import("./views/student/Exams.vue"), meta: { role: "student" } },
  { path: "/student/exams/:id", component: () => import("./views/student/ExamSlots.vue"), meta: { role: "student" } },
  { path: "/student/bookings", component: () => import("./views/student/Bookings.vue"), meta: { role: "student" } },
  { path: "/student/results", component: () => import("./views/student/Results.vue"), meta: { role: "student" } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Before opening a page, check that the user is allowed to see it
router.beforeEach((to) => {
  const user = JSON.parse(localStorage.getItem("user"));
  if (to.meta.role && !user) {
    return "/login";
  }
  if (to.meta.role && to.meta.role !== "any" && to.meta.role !== user.role) {
    return "/login";
  }
});

export default router;
