<template>
  <v-app
      id="unsubscriber"
  >
    <v-app-bar
        color="white"
        dense
        elevation="1"
    >
      <v-toolbar-title class="mx-3">Unsubscribe from Notification</v-toolbar-title>

    </v-app-bar>

    <!-- Sizes your content based upon application components -->
    <v-main>
      <!-- Provides the application the proper gutter -->
      <v-form
          ref="unsubscribe_form"
          v-model="valid_emails"
          lazy-validation
      >
        <v-textarea
            v-model="email_addresses"
            :rules="[v => !!v || 'At least one email address is required', v => (v && /^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5}){1,25}(,[ ]{0,1}([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5}){1,25})*$/.test(v.toLowerCase())) || 'Invalid email address or wrong address delimiter']"
            label="Email Address(es)"
            hint="Separate email addresses with commas"
            rows=1,
            auto_grow
            class="mx-3"
        >
        </v-textarea>
      </v-form>

      <!--      Footer  -->
      <v-toolbar elevation="1">
        <snackbar></snackbar>
        <v-spacer></v-spacer>
        <v-btn
            color="success"
            class="mx-3"
            :disabled="!valid_emails"
            :loading="unsubscribe_button_loading"
            @click="unsubscribe_click"
        >
          Unsubscribe
        </v-btn>
      </v-toolbar>

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
  top: -220px;
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
  mounted() {
    this.$refs.unsubscribe_form.validate()
  }

}
</script>
