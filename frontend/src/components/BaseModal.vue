<template>
  <Teleport to="body">
    <div 
      class="modal fade" 
      :class="{ show: show }" 
      :style="{ display: show ? 'block' : 'none' }" 
      tabindex="-1" 
      @click.self="close"
    >
      <div 
        class="modal-dialog modal-dialog-centered modal-dialog-scrollable"
        :class="size"
      >
        <div class="modal-content border-0 shadow rounded-4">
          <div class="modal-header border-bottom px-4 py-3">
            <h5 class="modal-title fw-bold text-primary">
              <slot name="title">{{ title }}</slot>
            </h5>
            <button type="button" class="btn-close" @click="close"></button>
          </div>
          <div class="modal-body p-4">
            <slot></slot>
          </div>
          <div class="modal-footer border-top px-4 py-3" v-if="$slots.footer">
            <slot name="footer"></slot>
          </div>
        </div>
      </div>
    </div>
    <div v-if="show" class="modal-backdrop fade show backdrop-blur"></div>
  </Teleport>
</template>

<script>
export default {
  name: 'BaseModal',
  props: {
    show: {
      type: Boolean,
      required: true
    },
    title: {
      type: String,
      default: ''
    },
    size: {
      type: String,
      default: 'modal-lg'
    }
  },
  emits: ['close'],
  methods: {
    close() {
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
.backdrop-blur {
  backdrop-filter: blur(5px);
  background-color: rgba(0, 0, 0, 0.5);
}
.modal.fade .modal-dialog {
  transition: transform 0.3s ease-out;
  transform: scale(0.95);
}
.modal.show .modal-dialog {
  transform: scale(1);
}
</style>
