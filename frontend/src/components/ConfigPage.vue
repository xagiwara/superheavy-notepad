<template>
  <div class="config">
    <h2>設定</h2>
    <h3>配色</h3>
    <div>
      <label><input type="radio" v-model="config.theme" value="system"/>システム</label>
      <label><input type="radio" v-model="config.theme" value="light" />ライト</label>
      <label><input type="radio" v-model="config.theme" value="dark" />ダーク</label>
    </div>
    <div><button type="button" @click="emit('close')">閉じる</button></div>

    <template v-if="status">
      <h2>システム情報</h2>
      <div class="system-info">
        <div>
          <h3>PyTorch</h3>
          <p>{{ status.torch }}</p>
        </div>
        <div>
          <h3>CUDA</h3>
          <p>{{ status.cuda?.version ?? 'N/A' }}<span v-if="status.cuda?.device_name">&nbsp;/&nbsp;{{ status.cuda.device_name }}</span></p>
        </div>
      </div>
      <div><button type="button" @click="emit('close')">閉じる</button></div>
    </template>
  </div>
</template>

<script lang="ts" setup>
import { useConfig } from '@/compositions/config';
import { onMounted, ref } from 'vue';

const emit = defineEmits<{
  (e: 'close'): void;
}>();

const config = useConfig();
const status = ref<{
  torch: string;
  cuda?: {
    version: string;
    device_name?: string;
  }
}>();

onMounted(async () => {
  status.value = await fetch('/api/status').then(res => res.json());
})
</script>

<style lang="scss" scoped>
h2 {
  margin: 0;
  font-size: 1.5em;
}

h3 {
  margin: 0;
  font-size: 1em;
}

.config {
  padding: 1em;
  display: grid;
  grid-template-columns: 1fr;
  grid-gap: 1em;
}

.system-info {
  display: grid;
  grid-template-columns: auto 1fr;
  grid-gap: 1em;
  align-items: center;

  > div {
    display: contents;
  }

  p {
    margin: 0;
  }
}
</style>
