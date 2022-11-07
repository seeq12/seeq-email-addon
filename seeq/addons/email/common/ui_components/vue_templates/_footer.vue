<template>
  <v-toolbar style="box-shadow: none;">

    <v-spacer></v-spacer>

    <v-subheader>{{ stopped_job_warning }}</v-subheader>

    <v-btn
        class="mx-2"
        :disabled="unschedule_button_disabled"
        :loading="unschedule_button_loading"
        @click="unschedule_button_on_click"
    >
      Unschedule
    </v-btn>

    <v-btn
        class="mx-2"
        color="success"
        :disabled="schedule_button_disabled"
        :loading="schedule_button_loading"
        @click="schedule_button_on_click"
    >
      Schedule
    </v-btn>

  </v-toolbar>
</template>

