<template>
  <div class="sidebar-logo-container" :class="{'collapse':collapse}">
    <transition name="sidebarLogoFade">
      <!--
        删除了 v-if="collapse" 和 v-else 的判断，
        因为无论是否折叠，我们都只显示标题。
      -->
      <router-link v-if="collapse" key="collapse" class="sidebar-logo-link" to="/">
        <!-- 折叠时只显示标题的第一个字或缩写 -->
        <h1 class="sidebar-title">{{ title.charAt(0) }} </h1>
      </router-link>
      <router-link v-else key="expand" class="sidebar-logo-link" to="/">
        <!-- 展开时显示完整标题 -->
        <h1 class="sidebar-title">{{ title }} </h1>
      </router-link>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'SidebarLogo',
  props: {
    collapse: {
      type: Boolean,
      required: true
    }
  },
  data() {
    return {
      title: '基于提示词工程的教辅系统'
      // logo 属性已完全删除
    }
  }
}
</script>

<style lang="scss" scoped>
/* 样式部分保持不变，删除了不再需要的 .sidebar-logo 样式 */
.sidebarLogoFade-enter-active {
  transition: opacity 1.5s;
}

.sidebarLogoFade-enter,
.sidebarLogoFade-leave-to {
  opacity: 0;
}

.sidebar-logo-container {
  position: relative;
  width: 100%;
  height: 50px;
  line-height: 50px;
  background: #2b2f3a;
  text-align: center;
  overflow: hidden;

  & .sidebar-logo-link {
    height: 100%;
    width: 100%;

    & .sidebar-title {
      display: inline-block;
      margin: 0;
      color: #fff;
      font-weight: 600;
      line-height: 50px;
      font-size: 14px;
      font-family: Avenir, Helvetica Neue, Arial, Helvetica, sans-serif;
      vertical-align: middle;
    }
  }

  /* 折叠时，标题居中 */
  &.collapse {
    .sidebar-title {
      margin: 0;
    }
  }
}
</style>
