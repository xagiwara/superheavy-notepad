import { defineStore } from 'pinia';
import { ref } from 'vue';

export interface Toast {
  symbol?: string;
  text: string;
  duration?: number;
  type?: 'info' | 'success' | 'warning' | 'error';
}

export interface ToastData {
  id: number;
  symbol: string;
  text: string;
  start: number;
  end: number;
  type?: 'info' | 'success' | 'warning' | 'error';
}

export const useToast = defineStore('toast', () => {
  const nextId = ref(0);
  const items = ref<ToastData[]>([]);
  const show = (toast: Toast) => {
    toast = Object.assign({ duration: 3 }, toast);
    const data: ToastData = {
      symbol: toast.symbol ?? 'check_circle',
      id: nextId.value++,
      text: toast.text,
      start: performance.now(),
      end: performance.now() + toast.duration! * 1000,
      type: toast.type,
    };
    items.value.push(data);
    setTimeout(() => {
      items.value = items.value.filter(item => item.id !== data.id);
    }, toast.duration! * 1000);
  };

  return {
    nextId,
    items,
    show,
  };
});

export interface Toast {
  symbol?: string;
  text: string;
  duration?: number;
  type?: 'info' | 'success' | 'warning' | 'error';
}

export interface ToastData {
  id: number;
  symbol: string;
  text: string;
  start: number;
  end: number;
  type?: 'info' | 'success' | 'warning' | 'error';
}
