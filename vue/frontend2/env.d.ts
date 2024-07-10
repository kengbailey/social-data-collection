/// <reference types="vite/client" />

// need this to make typescript happy w/ new component
// TODO: fully figure out why this is necessary
declare module '*/YTDL.vue' {
    import Vue from 'vue';
    export default Vue;
}
  