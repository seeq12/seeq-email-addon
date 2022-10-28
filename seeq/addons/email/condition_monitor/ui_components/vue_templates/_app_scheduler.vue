<template>
  <v-app
      id="notification-scheduler"
      class="pa-1"
  >
    <v-app-bar
        color="#007960"
        dark
        dense
    >
      <v-toolbar-title class="ml-4">Email Notification Scheduler</v-toolbar-title>

    </v-app-bar>

    <!-- Sizes your content based upon application components -->
    <v-main>
      <!-- Provides the application the proper gutter -->
      <condition></condition>
      <v-divider></v-divider>
      <tabs @buttonDisabled="onTabsContentChange"></tabs>
      <footie></footie>
      <snackbar></snackbar>

    </v-main>

  </v-app>
</template>

<style>

.container {
  width: 100% !important;
}

/*#header #header-container {*/
/*  display: none !important;*/
/*}*/

div.output_subarea {
  max-width: 100% !important;
}

.mdi-checkbox-marked, .mdi-minus-box {
  color: #007960 !important;
}

.v-toolbar__content {
  padding: 0 !important
}

.v-snack {
  position: absolute !important;
  top: -300px;
  right: 0 !important;
  left: unset !important;
}

div.output_scroll {
  height: unset;
  width: unset;
  overflow: unset;
  border-radius: unset;
  box-shadow: unset;
  display: unset;
}

.background_box {
  background-color: #007960 !important;
}

.vuetify-styles .v-text-field.v-text-field--enclosed .v-text-field__details {
  margin-bottom: 0 !important;
}

.vuetify-styles .v-text-field__details {
  min-height: 0 !important;
}

.v-messages {
  min-height: 0 !important;
}

.vuetify-styles .v-label {
  font-size: 14px;
}

.vuetify-styles .v-application {
  font-family: "Source Sans Pro", "Helvetica Neue", Helvetica, Arial, sans-serif;
}
</style>

<script>

export default {

  data() {
    return {
      form_validated: true, // This value is set to the value emitted by the child
    }
  },
  name: 'tabs',

  methods: {
    // Triggered when `buttonDisabled` event in _tabs.vue is emitted by the child.
    onTabsContentChange(tab, value) {
      this.form_validated = value;
    }
  }
}
</script>
