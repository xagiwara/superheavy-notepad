<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue';
import Title from '@/components/Title';
import { useCurrentFile } from '@/compositions/file';

const data = useCurrentFile();

const textarea = ref<HTMLTextAreaElement | null>(null);
const overlayElement = ref<HTMLDivElement | null>(null);
const caretPosition = ref(Number.NaN);
const inputTimeout = ref<number | null>(null);
const currentFile = shallowRef<FileSystemFileHandle>();

const currentFetching = ref<Promise<{
    candidates: string[];
    data: string;
    pos: number;
}>>();

const candidatesRef = ref<string[]>([]);

const autocomplete = computed(() => {
  if (candidatesRef.value.length > 0) {
    const lines = candidatesRef.value[0].split('\n');
    const filtered = lines.map((x, i) => [x, i] as const).filter(([x, i]) => x);
    console.debug('filtered', lines, filtered);
    if (filtered.length === 0) {
      return undefined;
    }
    let text = lines.slice(0, filtered[0][1] + 1).join('\n');
    if (lines.length > filtered[0][1] + 1) {
      text += '\n';
    }
    return text;
  } else {
    return undefined;
  }
});

watch(autocomplete, value => value != null && console.debug(value), { immediate: true });

const inputCompleted = async () => {
  candidatesRef.value = [];
  if (inputTimeout.value !== null) {
    clearTimeout(inputTimeout.value);
  }
  if (Number.isFinite(caretPosition.value) && data.text !== '') {
    const d = data.text;
    const pos = caretPosition.value;
    await Promise.all([
      currentFetching.value,
      new Promise(resolve => setTimeout(resolve, 500)),
    ]);
    if (d === data.text && pos === caretPosition.value) {
      const before = d.slice(0, pos);
      const after = d.slice(pos);
      // TODO: 挿入
      if (after.trim() === '') {
        currentFetching.value = (async () => {
          const res = await fetch('/api/infer/text', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: before, tags: [] }),
          });
          const { candidates } = await res.json() as { candidates: string[] };
          return {
            candidates,
            data: d,
            pos,
          };
        })();
        const { candidates } = await currentFetching.value;
        if (d === data.text && pos === caretPosition.value) {
          console.debug(candidates);
          candidatesRef.value = candidates;
        }
      } else if(after[0] === '\n') {
        currentFetching.value = (async () => {
          const res = await fetch('/api/infer/insert', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ before, after, tags: [] }),
          });
          const { candidates } = await res.json() as { candidates: string[] };
          return {
            candidates,
            data: d,
            pos,
          };
        })();
        const { candidates } = await currentFetching.value;
        if (d === data.text && pos === caretPosition.value) {
          console.debug(candidates);
          candidatesRef.value = candidates;
        }
      }
      console.debug(d, pos, `"${d.slice(0, pos)}"`, `"${d.slice(pos)}"`);
    }
  }
};

const input = (ev: Event) => {
  candidatesRef.value = [];
  if (ev instanceof InputEvent) {
    if (ev.inputType === 'insertCompositionText') {
      return;
    }
    // inputCompleted();
  }
};

const composition = ref(false);

const compositionstart = (ev: CompositionEvent) => {
  composition.value = true;
};

const compositionend = (ev: CompositionEvent) => {
  composition.value = false;
};

const selectionchange = (ev: Event) => {
  if (!composition.value && ev.target === textarea.value && textarea.value) {
    const newPosition = textarea.value.selectionStart === textarea.value.selectionEnd ? textarea.value.selectionStart : Number.NaN;
    if (newPosition !== caretPosition.value) {
      caretPosition.value = newPosition;
      inputCompleted();
    }
  }
};

onMounted(() => {
  document.addEventListener('selectionchange', selectionchange);
  textarea.value?.focus();
});

onBeforeUnmount(() => {
  document.removeEventListener('selectionchange', selectionchange);
});

const keydown = async (ev: KeyboardEvent) => {
  if (ev.key === 'Tab' && !ev.altKey && !ev.metaKey && !ev.shiftKey && !ev.ctrlKey) {
    ev.preventDefault();
    const insertText = autocomplete.value;
    if (textarea.value && insertText != null && textarea.value.selectionStart === textarea.value.selectionEnd) {
      const pos = textarea.value.selectionStart;
      candidatesRef.value = [];
      data.text = data.text.slice(0, pos) + insertText + data.text.slice(pos);
      await nextTick();
      textarea.value.setSelectionRange(pos + insertText.length, pos + insertText.length);
    }
  }
};

const scroll = (ev: Event) => {
  if (overlayElement.value && textarea.value) {
    overlayElement.value.scrollTop = textarea.value.scrollTop;
    console.log(overlayElement.value.scrollTop, textarea.value.scrollTop);
  }
};

const blur = (ev: Event) => {
  textarea.value?.focus();
};
</script>

<template>
  <Title :text="(currentFile?.name ?? '新しいテキスト') + (data.modified ? ' *' : '')" />
  <div class="editbox-area">
    <textarea class="editbox" v-model="data.text" @input="input" @compositionend="compositionend" @compositionstart="compositionstart" ref="textarea" @keydown="keydown" @scroll="scroll" autofocus @blur="blur" />
    <div class="editbox-overlay" ref="overlayElement">
      <template v-for="x, i in [...data.text, undefined]">
        <span v-if="caretPosition === i && autocomplete != null" class="autocomplete">
          <template v-for="a in autocomplete">
            <span v-if="a === '\n'">&#x21b5;</span>
            <span v-else-if="a === ' '" class="space-symbol">{{ a }}</span>
            <span v-else-if="a === '\u3000'" class="wide-space-symbol">{{ a }}</span>
            <span v-else>{{ a }}</span>
          </template>
        </span>
        <template v-if="x !== undefined">
          <template v-if="x === '\n'">
            <span class="return-symbol" v-if="caretPosition !== i || autocomplete == null">&#x21b5;</span>
            <br />
          </template>
          <span v-else-if="x === ' '" class="space-symbol">{{ x }}</span>
          <span v-else-if="x === '\u3000'" class="wide-space-symbol">{{ x }}</span>
          <span v-else class="other-characters">{{ x }}</span>
        </template>
      </template>
    </div>
  </div>
  <!-- <ConfirmDiscardModal /> -->
</template>

<style lang="scss" scoped>
.editbox-area {
  position: relative;
  z-index: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.editbox, .editbox-overlay {
  resize: none;

  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  display: block;

  border: none;
  outline: none;
  font-family: 'Not Serif JP', serif;
  font-optical-sizing: auto;
  font-weight: 400;
  font-style: normal;
  font-size: 16px;
  line-height: 1.5;
  padding: 0.5em;

  overflow-y: scroll;
  overflow-x: hidden;
}

.editbox-overlay {
  z-index: 1;
  pointer-events: none;
  opacity: 0.5;
  position: relative;
  padding-bottom: 2em;
}

.return-symbol {
  position: absolute;
}

.space-symbol {
  white-space: pre;
  position: relative;
  &::after {
    content: ".";
    display: inline;
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    right: 0;
    text-align: center;
  }
}

.wide-space-symbol {
  white-space: pre;
  position: relative;
  &::after {
    content: "□";
    display: inline;
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    right: 0;
    text-align: center;
  }
}

.other-characters {
  white-space: pre;
  opacity: 0;
}

.autocomplete {
  white-space: nowrap;
  position: absolute;
  font-style: italic;
}
</style>
