<template>
  <div>
    <v-expansion-panels class="mt-5">
      <v-expansion-panel>
        <v-expansion-panel-header style="font-size: 16px">
          Instructions
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <jupyter-widget :widget="templating_explanation"/>
        </v-expansion-panel-content>

      </v-expansion-panel>
    </v-expansion-panels>

    <v-form
        ref="templating_form"
        v-model="templating_form_valid"
        lazy-validation
        @input="templateEmitToTabs"
    >

      <v-textarea
          v-model="subject"
          label="Subject Template"
          rows=1
          auto-grow
          :rules="[v => !!v || 'Subject is required']"

      >
      </v-textarea>

      <v-textarea
          v-model="html"
          label="HTML Template"
          rows=1
          auto-grow
          :rules="[v => !!v || 'HTML Template is required']"
      >
      </v-textarea>

      <v-toolbar style="box-shadow: none;">
        <v-spacer></v-spacer>
        <v-btn
            class="mx-2"
            :disabled="reset_button_disabled"
            @click="template_reset_on_click"
        >
          Reset
        </v-btn>
      </v-toolbar>
    </v-form>

  </div>
</template>

<script>
export default {
  mounted() {
    this.$refs.templating_form.validate()
  },
  name: 'Templating',
  methods: {
    templateEmitToTabs(event) {
      this.$emit('templatingToTabs', 'templating', this.$refs.templating_form.validate())
    }
  }
}
</script>

