<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <v-app>
    <v-main>
      <v-container>
        <v-text-field
          v-model="videoUrl"
          label="YouTube URL"
          @keyup.enter="downloadAudio"
        ></v-text-field>
        <v-btn @click="downloadAudio" color="primary">Download Audio</v-btn>
        <v-alert v-if="message" :type="alertType" class="mt-4">
          {{ message }}
        </v-alert>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      videoUrl: '',
      message: '',
      alertType: 'info',
    };
  },
  methods: {
    async downloadAudio() {
      try {
        const response = await axios.post('http://localhost:8000/download', { url: this.videoUrl });
        this.message = response.data.message;
        this.alertType = 'info';
        this.listenForCompletion();
      } catch (error) {
        console.error('Error:', error);
        this.message = 'Error starting download';
        this.alertType = 'error';
      }
    },
    listenForCompletion() {
      const eventSource = new EventSource('http://localhost:8000/status');
      
      eventSource.onmessage = (event) => {
        this.message = event.data;
        this.alertType = 'success';
        eventSource.close();
      };

      eventSource.onerror = (error) => {
        console.error('EventSource failed:', error);
        this.message = 'Error listening for updates';
        this.alertType = 'error';
        eventSource.close();
      };

      // Close the connection after a timeout (e.g., 5 minutes)
      setTimeout(() => {
        if (eventSource.readyState !== EventSource.CLOSED) {
          console.log('Closing EventSource after timeout');
          eventSource.close();
        }
      }, 300000); // 5 minutes
    },
  },
};
</script>