import { defineComponent, watch, type PropType } from 'vue';

export default defineComponent((props) => {
  watch(() => props.text, text => {
    document.title = text;
  }, { immediate: true });

  return () => undefined;
}, {
  props: {
    text: String as PropType<string>,
  },
});
