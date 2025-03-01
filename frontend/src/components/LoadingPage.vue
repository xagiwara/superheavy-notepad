<template>
  <div class="loading">
    <div>
      <p>
        読込中……
      </p>
      <p>
        起動には数分かかる場合があります。
      </p>
      <p>
        <div v-if="status === 'loading_base_model'">ベースモデルを読み込んでいます……</div>
        <div v-if="status === 'loading_peft_model'">PEFTモデルを読み込んでいます……</div>
        <div v-if="status === 'loading_tokenizer'">トークナイザを読み込んでいます……</div>
        <div v-if="status === 'warming_up'">モデルをウォームアップしています……</div>
      </p>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue';

const emit = defineEmits<{
  (e: 'loaded'): void;
}>();

const status = ref<'loading_base_model' | 'loading_peft_model' | 'loading_tokenizer' | 'warming_up' | 'done'>();

onMounted(async () => {
  while (true) {
    const abort = new AbortController();
    const response = await Promise.race([
      fetch('/api/ready', {
        signal: abort.signal,
      }),
      new Promise<undefined>(resolve => setTimeout(() => {
        abort.abort();
        resolve(undefined);
      }, 1000)),
    ]);
    if (response) {
      const data: {
        done: boolean;
        status: 'loading_base_model' | 'loading_peft_model' | 'loading_tokenizer' | 'warming_up' | 'done';
      } = await response.json();
      status.value = data.status;
      if (data.done) {
        break;
      }
    }
    await new Promise<void>(resolve => setTimeout(resolve, 1000));
  }
  emit('loaded');
});
</script>

<style lang="scss" scoped>
.loading {
  display: flex;
  flex-direction: column;
  padding: 1em;
  justify-content: center;
  align-items: center;
}
</style>
