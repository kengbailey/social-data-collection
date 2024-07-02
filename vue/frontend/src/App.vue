<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <v-app>
    <v-main>
      <v-container>

        <!-- Download a Video -->
        <v-text-field
          v-model="videoUrl"
          label="YouTube URL"
          @keyup.enter="downloadAudio"
        ></v-text-field>
        
        <!-- <v-row justify="center">
          <v-col cols="auto">
            <v-btn @click="downloadAudio" color="primary">Download</v-btn>
          </v-col>
        </v-row> -->
        
                
        

        <!-- Downloaded Videos -->
        <h2 class="mt-12 custom-header">Downloaded</h2>
        <v-data-table
          :headers="headers"
          :items="items"
          :items-per-page="5"
          class="elevation-1 mt-4"
          hide-default-footer
          hide-default-header
        ></v-data-table>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import axios from 'axios';
import { toast } from "vue3-toastify";
import "vue3-toastify/dist/index.css";

export default {
  data() {
    return {
      videoUrl: '',
      message: '',
      alertType: 'info',
      isDownloading: false,
      items: [],
      headers: [
        { text: 'File Name', value: 'name' },
        { text: 'Last Modified', value: 'last_modified' },
      ],
    };
  },
  methods: {
    async downloadAudio() {
      this.isDownloading = true;
      try {
        const response = await axios.post('http://localhost:8000/download', { url: this.videoUrl });
        toast(response.data.message, {
          "theme": "auto",
          "type": "success",
          "position": "bottom-left",
          "transition": "slide",
          "dangerouslyHTMLString": true
        })
        
      } catch (error) {
        console.error('Error:', error);
        this.message = 'Error starting download';
        this.alertType = 'error';
      } finally {
        this.isDownloading = false;
      }
    },
    async getLatestItems() {
      try {
        const response = await axios.get('http://localhost:8000/get_latest');
        console.log(response)
        this.items = response.data.items.map((item, index) => ({
          name: item,
          last_modified: new Date(response.data.items_last_modified[index]).toLocaleString(), // Convert to JavaScript Date and then format
        }));
      } catch (error) {
        console.error('Error getting latest items:', error);
      }
    },
  },
  created() {
    this.getLatestItems();
    setInterval(this.getLatestItems, 5000);
  }
};
</script>

<style scoped>
.custom-header {
  font-weight: normal;
  font-size: large;
  text-decoration: underline; /* to add underlining */
}
</style>
