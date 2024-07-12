const { createApp } = Vue
const { createVuetify } = Vuetify

const vuetify = createVuetify({
    theme: {
      defaultTheme: 'dark',
    },
})

createApp({
    data() {
        return {
            message: 'Hello Vue 3 with Vuetify!',
            buttonText: 'Click me', 
            drawer: false
        }
    }
})
.use(vuetify)
.mount('#app')