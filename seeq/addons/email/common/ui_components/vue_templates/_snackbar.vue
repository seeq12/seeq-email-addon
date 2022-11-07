<template>
  <v-snackbar
      v-model="value"
      app
      shaped
      :color="color"
      :timeout="timeout"
  >
    {{ message }}

    <v-btn
        color="white"
        icon
        @click="value = false"
    >
      <v-icon>
        mdi-window-close
      </v-icon>
    </v-btn>
  </v-snackbar>
</template>
