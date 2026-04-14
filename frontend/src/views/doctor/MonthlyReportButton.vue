<template>
  <button @click="sendMonthlyReport">Send Monthly Report</button>
</template>

<script>
export default {
  methods: {
    async sendMonthlyReport() {
      // Replace with actual doctor ID, year, month
      const doctorId = this.$store.state.auth.user.id;
      const now = new Date();
      const year = now.getFullYear();
      const month = now.getMonth(); // JS months are 0-indexed, backend expects 1-indexed
      await fetch('/api/send-monthly-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ doctor_id: doctorId, year, month: month + 1 })
      });
      alert('Monthly report triggered!');
    }
  }
}
</script>
