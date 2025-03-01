import { nextTick, ref, shallowRef, watch } from 'vue';
import { defineStore } from 'pinia';
import { useToast } from './toast';

export const useCurrentFile = defineStore('currentFile', () => {
  const text = ref('');
  const fileHandle = shallowRef<FileSystemFileHandle>();
  const modified = ref(false);

  const toast = useToast();

  watch(text, () => modified.value = true);

  const onbeforeunload = (e: BeforeUnloadEvent) => {
    e.preventDefault();
  };

  watch(modified, v => {
    if (v) {
      window.addEventListener('beforeunload', onbeforeunload);
    } else {
      window.removeEventListener('beforeunload', onbeforeunload);
    }
  }, { immediate: true });

  const newFile = async () => {
    if (modified.value && !confirm('編集中の内容が破棄されます。よろしいですか？')) {
      return;
    }
    text.value = '';
    await nextTick();
    modified.value = false;
  };

  const open = async () => {
    if (modified.value && !confirm('編集中の内容が破棄されます。よろしいですか？')) {
      return;
    }
    const [openFileHandle] = await window.showOpenFilePicker({ types: [{ accept: { 'text/plain': ['.txt'] } }] });
    const file = await openFileHandle.getFile();
    text.value = (await file.text()).replace(/\r\n/g, '\n');
    fileHandle.value = openFileHandle;
    await nextTick();
    modified.value = false;
  };

  const saveAs = async () => {
    try {
      const saveFileHandle = await window.showSaveFilePicker({ types: [{ accept: { 'text/plain': ['.txt'] } }] });
      const writable = await saveFileHandle.createWritable();
      await writable.write(text.value);
      await writable.close();
      fileHandle.value = saveFileHandle;
      await nextTick();
      modified.value = false;
      toast.show({ symbol: 'check_circle', text: '保存しました' });
    } catch (e) {
      console.error(e);
      toast.show({ symbol: 'error', text: '保存に失敗しました' });
    }
  };

  const save = async () => {
    if (fileHandle.value) {
      try {
        const writable = await fileHandle.value.createWritable();
        await writable.write(text.value);
        await writable.close();
        await nextTick();
        modified.value = false;
        toast.show({ symbol: 'check_circle', text: '保存しました' });
      } catch (e) {
        if (e instanceof DOMException && e.name === 'NoModificationAllowedError') {
          await saveAs();
          console.error('Permission denied');
        } else {
          console.error(e);
          toast.show({ symbol: 'error', text: '保存に失敗しました' });
        }
      }
    } else {
      await saveAs();
    }
  };

  return {
    text,
    fileHandle,
    modified,
    open,
    save,
    saveAs,
    newFile,
  };
});
