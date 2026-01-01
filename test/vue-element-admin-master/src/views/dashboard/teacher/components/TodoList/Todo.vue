<template>
  <!--
    li 元素的 class 会根据 todo.done 和 editing 的状态动态变化
    - 'completed': 任务已完成时添加
    - 'editing': 正在编辑任务时添加
  -->
  <li :class="{ completed: todo.done, editing: editing }" class="todo">
    <div class="view">
      <!-- 复选框，用于切换任务的完成状态 -->
      <input
        :checked="todo.done"
        class="toggle"
        type="checkbox"
        @change="toggleTodo( todo)"
      >
      <!-- 任务文本标签。双击时，将 editing 状态设为 true，进入编辑模式 -->
      <label @dblclick="editing = true" v-text="todo.text" />
      <!-- 删除按钮 -->
      <button class="destroy" @click="deleteTodo( todo )" />
    </div>
    <!--
      编辑任务的输入框。
      - v-show="editing": 仅在 editing 为 true 时显示
      - v-focus="editing": 自定义指令，在显示时自动获取焦点
      - @keyup.enter: 按回车键完成编辑
      - @keyup.esc: 按 Esc 键取消编辑
      - @blur: 失去焦点时完成编辑
    -->
    <input
      v-show="editing"
      v-focus="editing"
      :value="todo.text"
      class="edit"
      @keyup.enter="doneEdit"
      @keyup.esc="cancelEdit"
      @blur="doneEdit"
    >
  </li>
</template>

<script>
export default {
  name: 'Todo',
  // 自定义指令
  directives: {
    // 'focus' 指令：当绑定的值（value）为真时，让元素自动获得焦点
    focus(el, { value }, { context }) {
      if (value) {
        context.$nextTick(() => {
          el.focus()
        })
      }
    }
  },
  // 从父组件接收的属性
  props: {
    todo: {
      type: Object,
      default: function() {
        return {}
      }
    }
  },
  // 组件的内部状态
  data() {
    return {
      editing: false // 是否处于编辑模式，默认为 false
    }
  },
  methods: {
    // 触发 'deleteTodo' 事件，通知父组件删除此任务
    deleteTodo(todo) {
      this.$emit('deleteTodo', todo)
    },
    // 触发 'editTodo' 事件，通知父组件修改此任务
    editTodo({ todo, value }) {
      this.$emit('editTodo', { todo, value })
    },
    // 触发 'toggleTodo' 事件，通知父组件切换此任务的完成状态
    toggleTodo(todo) {
      this.$emit('toggleTodo', todo)
    },
    // 完成编辑
    doneEdit(e) {
      const value = e.target.value.trim() // 获取输入框的值并去除首尾空格
      const { todo } = this
      if (!value) {
        // 如果值为空，则直接删除该任务
        this.deleteTodo({
          todo
        })
      } else if (this.editing) {
        // 如果值不为空且处于编辑状态，则提交编辑
        this.editTodo({
          todo,
          value
        })
        this.editing = false // 退出编辑模式
      }
    },
    // 取消编辑
    cancelEdit(e) {
      e.target.value = this.todo.text // 将输入框的值恢复为原始值
      this.editing = false // 退出编辑模式
    }
  }
}
</script>
