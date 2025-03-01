<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue';
import MainEditor from './components/MainEditor.vue';
import LoadingPage from './components/LoadingPage.vue';
import { useCurrentFile } from './compositions/file';
import { useToast } from './compositions/toast';
import ConfigPage from './components/ConfigPage.vue';
import { useConfig } from './compositions/config';

const loaded = ref(false);
const data = useCurrentFile();
const toast = useToast();
const config = ref(false);
useConfig();

const keydown = async (ev: KeyboardEvent) => {
  if (!loaded.value) {
    return;
  }

  if (ev.code === 'KeyS' && (ev.ctrlKey || ev.metaKey) && !ev.shiftKey && !ev.altKey) {
    ev.preventDefault();
    data.save();
  }
  if (ev.code === 'KeyS' && (ev.ctrlKey || ev.metaKey) && ev.shiftKey && !ev.altKey) {
    ev.preventDefault();
    data.saveAs();
  }
};

onMounted(() => {
  window.addEventListener('keydown', keydown);
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', keydown);
});
</script>

<template>
  <div class="wrapper">
    <div class="header">
      <div class="header-menu">
        <template v-if="loaded && !config">
          <div class="buttons">
            <button type="button" @click="data.newFile">新規</button>
            <button type="button" @click="data.open">開く</button>
            <button type="button" :disabled="!data.fileHandle" @click="data.save">保存</button>
            <button type="button" @click="data.saveAs">名前を付けて保存</button>
          </div>
          <div class="filename" :title="data.fileHandle?.name">{{ data.fileHandle?.name }}</div>
        </template>
      </div>
      <div class="settings-button-wrapper">
        <button type="button" @click="config = !config">
          <span class="material-symbols-outlined">manufacturing</span>
        </button>
      </div>
    </div>
    <div class="content">
      <ConfigPage v-if="config" @close="config = false" />
      <MainEditor v-else-if="loaded" />
      <LoadingPage v-else @loaded="loaded = true" />
    </div>
    <div class="status">
      <template v-if="toast.items.length > 0">
        <span class="material-symbols-outlined">{{ toast.items.slice(-1)[0].symbol }}</span>{{ toast.items.slice(-1)[0].text }}
      </template>
      <template v-else>
        <span class="material-symbols-outlined">check_circle</span>
        <span v-if="loaded">準備完了</span>
        <span v-else>準備中……</span>
      </template>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.wrapper {
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: auto 1fr auto;
  overflow: hidden;

  .header {
    display: grid;
    grid-template-columns: 1fr auto;

    .header-menu {
      display: grid;
      grid-template-columns: auto 1fr;
      align-items: center;

      .buttons {
        display: flex;
      }
      .filename {
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
        padding: 0 0.5em;

      }
    }
  }

  .content {
    width: 100%;
    height: 100%;
    overflow: hidden;
  }

  .status {
    background: light-dark(#F5F5F5, #424242);
    font-size: 12px;
    padding: 0.25em 0.5em;
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 0.5em;

    .material-symbols-outlined {
      font-size: 16px;
    }
  }
}
</style>
