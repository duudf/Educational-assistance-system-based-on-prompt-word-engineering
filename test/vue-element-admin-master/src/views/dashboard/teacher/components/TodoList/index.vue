<template>
  <section class="todoapp">
    <!-- header: 输入框 -->
    <header class="header">
      <input class="new-todo" autocomplete="off" placeholder="添加待办事项" @keyup.enter="addTodo">
    </header>
    <!-- main section: 待办事项列表 -->
    <section v-show="todos.length" class="main">
      <input id="toggle-all" :checked="allChecked" class="toggle-all" type="checkbox" @change="toggleAll({ done: !allChecked })">
      <label for="toggle-all" />
      <ul class="todo-list">
        <todo
          v-for="(todo, index) in filteredTodos"
          :key="index"
          :todo="todo"
          @toggleTodo="toggleTodo"
          @editTodo="editTodo"
          @deleteTodo="deleteTodo"
        />
      </ul>
    </section>
    <!-- footer: 底部信息和过滤器 -->
    <footer v-show="todos.length" class="footer">
      <span class="todo-count">
        <strong>{{ remaining }}</strong> 项剩余
      </span>
      <ul class="filters">
        <li v-for="(val, key) in filters" :key="key">
          <a :class="{ selected: visibility === key }" @click.prevent="visibility = key">{{
            key | visibilityFilter
          }}</a>
        </li>
      </ul>
      <!--
      <button class="clear-completed" v-show="todos.length > remaining" @click="clearCompleted">
        清除已完成
      </button>
      -->
    </footer>
  </section>
</template>

<script>
import Todo from './Todo.vue'

const STORAGE_KEY = 'todos'
// 过滤器逻辑
const filters = {
  all: todos => todos, // 全部
  active: todos => todos.filter(todo => !todo.done), // 未完成
  completed: todos => todos.filter(todo => todo.done) // 已完成
}
// 默认的待办事项列表
const defalutList = [
  { text: '给这个仓库点赞', done: false },
  { text: 'Fork 此仓库', done: false },
  { text: '关注作者', done: false },
  { text: '学习 vue-element-admin', done: true },
  { text: '学习 vue', done: true },
  { text: '学习 element-ui', done: true },
  { text: '学习 axios', done: true },
  { text: '学习 webpack', done: true }
]
export default {
  components: { Todo },
  filters: {
    // 这个过滤器在中文环境下不再需要，因为“项”没有单复数之分
    pluralize: (n, w) => n === 1 ? w : w + 's',
    // 这个过滤器也被下面的 visibilityFilter 替代了
    capitalize: s => s.charAt(0).toUpperCase() + s.slice(1),
    // 新增过滤器：将 'all', 'active', 'completed' 翻译成中文
    visibilityFilter(key) {
      const map = {
        all: '全部',
        active: '未完成',
        completed: '已完成'
      }
      return map[key]
    }
  },
  data() {
    return {
      visibility: 'all', // 当前的可见性状态
      filters,
      // 从 localStorage 加载 todos，如果不存在则使用默认列表
      // todos: JSON.parse(window.localStorage.getItem(STORAGE_KEY)) || defalutList
      todos: defalutList
    }
  },
  computed: {
    // 是否所有任务都已完成
    allChecked() {
      return this.todos.every(todo => todo.done)
    },
    // 根据当前 visibility 过滤后的任务列表
    filteredTodos() {
      return filters[this.visibility](this.todos)
    },
    // 剩余未完成任务的数量
    remaining() {
      return this.todos.filter(todo => !todo.done).length
    }
  },
  methods: {
    // 将当前 todos 存入 localStorage
    setLocalStorage() {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(this.todos))
    },
    // 添加新的待办事项
    addTodo(e) {
      const text = e.target.value
      if (text.trim()) {
        this.todos.push({
          text,
          done: false
        })
        // this.setLocalStorage() // 如果需要持久化，取消此行注释
      }
      e.target.value = ''
    },
    // 切换单个任务的完成状态
    toggleTodo(val) {
      val.done = !val.done
      // this.setLocalStorage()
    },
    // 删除一个任务
    deleteTodo(todo) {
      this.todos.splice(this.todos.indexOf(todo), 1)
      // this.setLocalStorage()
    },
    // 编辑一个任务
    editTodo({ todo, value }) {
      todo.text = value
      // this.setLocalStorage()
    },
    // 清除所有已完成的任务
    clearCompleted() {
      this.todos = this.todos.filter(todo => !todo.done)
      // this.setLocalStorage()
    },
    // 切换所有任务的完成状态
    toggleAll({ done }) {
      this.todos.forEach(todo => {
        todo.done = done
        // this.setLocalStorage()
      })
    }
  }
}
</script>

<style lang="scss">
@import './index.scss';
</style>
