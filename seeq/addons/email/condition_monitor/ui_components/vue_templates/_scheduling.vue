<template>
  <div>

    <v-form
        ref="scheduling_form"
        v-model="scheduling_form_valid"
        lazy-validation
        @input="scheduleEmitToTabs"
    >
      <v-textarea
          v-model="to"
          :rules="[v => !!v || 'At least one email address is required', v => (v && /^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5}){1,25}(,[ ]{0,1}([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5}){1,25})*$/.test(v.toLowerCase())) || 'Invalid email address or wrong address delimiter']"
          label="To"
          hint="Separate email addresses with commas"
          rows=1
          auto-grow
      >
      </v-textarea>
      <v-text-field
          v-model="schedule"
          label="Schedule"
          :rules="[v => !!v || 'A schedule frequency is required',
        v => (v && !!/^every \d+ \w+$/.test(schedule.toLowerCase())) ||
        'Provide a valid Cron expression, i.e. `every 15 minutes`']"
      >
      </v-text-field>
      <v-textarea
          v-model="topic_url"
          label="Topic Document URL (optional)"
          rows=1
          auto-grow
      >
      </v-textarea>
      <v-expansion-panels class="mt-5">
        <v-expansion-panel>
          <v-expansion-panel-header>
            Advanced
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            <v-select
                v-model="time_zone_value"
                :items="time_zone_items"
                label="Time Zone"
            >
            </v-select>
            <v-text-field
                v-model="lookback_period"
                label="Check for new capsule starts within the last N days:"
                :rules="[v  => {
      if (!v.trim()) return true;
      if (!isNaN(parseFloat(v)) && v > 0) return true;
      return 'Value must be a number greater than 0';
    }]"
            >
            </v-text-field>
            <v-textarea
                v-model="cc"
                label="Cc"
                hint="Separate email addresses with commas"
                rows=1
                auto-grow
            >
            </v-textarea>
            <v-textarea
                v-model="bcc"
                label="Bcc"
                hint="Separate email addresses with commas"
                rows=1
                auto-grow
            >
            </v-textarea>
          </v-expansion-panel-content>

        </v-expansion-panel>
      </v-expansion-panels>
    </v-form>
  </div>
</template>

<script>
export default {
  mounted() {
    this.$refs.scheduling_form.validate()
  },

  data() {
    return {
      scheduling_form_valid: false
    }
  },
  name: 'Scheduling',
  methods: {
    scheduleEmitToTabs(event) {
      this.$emit('schedulingToTabs', 'scheduling', this.$refs.scheduling_form.validate())
    }
  }
}
</script>

