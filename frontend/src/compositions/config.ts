import { defineStore } from 'pinia';
import { computed, ref, watch } from 'vue';

interface Config {
  theme: 'system' | 'light' | 'dark';
}

export const useConfig = defineStore('config', () => {
  const loadedData = (() => {
    try {
      return JSON.parse(localStorage.getItem('config') ?? '{}');
    } catch {
      return {};
    }
  })();
  console.debug(loadedData);
  const data = ref<Config>(Object.assign({ theme: 'system' }, loadedData));

  watch(data, value => {
    localStorage.setItem('config', JSON.stringify(value));
  }, { deep: true, immediate: true });

  const theme = computed({
    get: () => data.value.theme,
    set: (value: Config['theme']) => {
      data.value.theme = value;
    },
  });

  watch(theme, value => {
    document.body.classList.remove('theme-system', 'theme-light', 'theme-dark');
    document.body.classList.add(`theme-${value}`);
  }, { immediate: true });

  return {
    theme,
  };
});
