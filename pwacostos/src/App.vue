<template>
  <router-view v-slot="{ Component, route }">
    <Transition :name="route.meta.guest ? 'page-auth' : 'page'" mode="out-in">
      <component :is="Component" :key="route.path" />
    </Transition>
  </router-view>
</template>

<script setup lang="ts">
</script>
