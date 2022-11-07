<template>
  <v-container
      class="text-primary mt-5"
      style="width: 100%; max-width: 100%; padding: 5px 25px;"
  >
    <v-row>
      <p style="margin-right: 8px;font-size: 17px;margin-top: 4px; color: #007960;">
        Condition
      </p>
      <v-select
          v-model="condition_value"
          :items="condition_items"
          style="margin-right: 8px; margin-top:0; padding-top:0;"
          no-data-text="No conditions available"
          @change="condition_select_on_change"
      >
      </v-select>
    </v-row>

  </v-container>
</template>

