import { createApp } from 'vue'
import App from './App.vue'

import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

// import Vue3Toastify from 'vue3-toastify';


const vuetify = createVuetify({
  components,
  directives,
});

const app = createApp(App);
app.use(vuetify);

// app.use(Vue3Toastify,{
//   autoClose: 3000,
// });

app.mount('#app');