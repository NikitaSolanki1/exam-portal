<!-- A coloured label for a status. "Booking Open" gets the CSS class "status-booking-open" (see style.css) -->
<template>
  <span class="badge" :class="'status-' + text.toLowerCase().replaceAll(' ', '-')">{{ text }}</span>
</template>

<script>
export default {
  props: ["text"],
};
</script>
