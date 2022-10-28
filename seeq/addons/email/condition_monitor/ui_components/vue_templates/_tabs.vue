<template>
  <v-tabs>
    <v-tab>
      Scheduling
    </v-tab>
    <v-tab-item style="padding: 15px;">
      <scheduling-content @schedulingToTabs="onSchedulingChange"></scheduling-content>
    </v-tab-item>

    <v-tab>
      Templates
    </v-tab>
    <v-tab-item style="padding: 15px;">
      <templating-content @templatingToTabs="onSchedulingChange"></templating-content>
    </v-tab-item>

    <v-tab>
      Jobs
    </v-tab>
    <v-tab-item class="pa-4">
      <jobs-content></jobs-content>
    </v-tab-item>

    <!--    <v-btn-->
    <!--        class="mx-2"-->
    <!--        color="Success"-->
    <!--        :disabled="buttonDisabled"-->
    <!--    >-->
    <!--      Schedule-->
    <!--    </v-btn>-->

  </v-tabs>

</template>

<script>

export default {
  data() {
    return {
      scheduling_valid: false,
      templating_valid: false,
      // buttonDisabled: true, // This value is set to the value emitted by the child
    }
  },
  name: 'tabs',
  methods: {
    // Triggered when `schedulingToTabs` event is emitted by the child.
    onSchedulingChange(tab, value) {
      if (tab === 'scheduling') {
        this.scheduling_valid = value
      }
      if (tab === 'templating') {
        this.templating_valid = value
      }

      this.$emit('buttonDisabled', 'tabs', this.scheduling_valid && this.templating_valid)
      // this.buttonDisabled = !(this.scheduling_valid && this.templating_valid);
    }
  }
}
</script>

