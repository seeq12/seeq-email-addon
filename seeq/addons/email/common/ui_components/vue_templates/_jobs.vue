<template>
  <v-data-table
      :headers="data_table_headers"
      :items="data_table_items"
      v-model="data_table_values"
      item-key="Codition Name"
      class="elevation-1"
      no-data-text="No notifications scheduled"
  >
  </v-data-table>
</template>

