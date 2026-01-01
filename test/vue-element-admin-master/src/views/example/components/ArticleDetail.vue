<template>
  <div class="form-container">
    <el-form ref="courseForm" :model="courseForm" :rules="rules" label-width="100px" class="course-form">
      <sticky :z-index="10" :class-name="'sub-navbar ' + (isEdit ? 'edit' : 'draft')">
        <el-button v-loading="loading" style="margin-left: 10px;" type="success" @click="submitForm">
          {{ isEdit ? '更新课程' : '立即创建' }}
        </el-button>
        <el-button v-if="!isEdit" type="info" @click="resetForm">
          重置表单
        </el-button>
      </sticky>

      <div class="createPost-main-container">
        <el-form-item label="课程名称" prop="name" >
          <el-input v-model="courseForm.name" placeholder="请输入课程名称" />
        </el-form-item>

        <el-form-item label="课程描述" prop="description">
          <el-input
            v-model="courseForm.description"
            type="textarea"
            :rows="8"
            placeholder="请输入课程的详细描述，例如课程目标、教学大纲等"
          />
        </el-form-item>
      </div>
    </el-form>
  </div>
</template>

<script>
import Sticky from '@/components/Sticky' // 引入粘性头部组件
// 引入课程相关的 API
import { fetchCourseDetail, createCourse, updateCourse } from '@/api/course'

// 定义表单的默认数据结构
const defaultForm = {
  id: undefined,
  name: '',
  description: ''
}

export default {
  name: 'CourseDetail',
  components: { Sticky },
  props: {
    isEdit: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      courseForm: Object.assign({}, defaultForm),
      loading: false,
      rules: {
        name: [{ required: true, message: '课程名称是必填项', trigger: 'blur' }],
        description: [{ required: true, message: '课程描述是必填项', trigger: 'blur' }]
      },
      tempRoute: {}
    }
  },
  created() {
    if (this.isEdit) {
      const id = this.$route.params.id
      this.fetchData(id)
    }
    this.tempRoute = Object.assign({}, this.$route)
  },
  methods: {
    fetchData(id) {
      this.loading = true
      fetchCourseDetail(id).then(response => {
        this.courseForm = response.data
        this.setTagsViewTitle()
        this.setPageTitle()
        this.loading = false
      }).catch(err => {
        console.error('获取课程详情失败:', err)
        this.loading = false
      })
    },
    setTagsViewTitle() {
      const title = '编辑课程'
      const route = Object.assign({}, this.tempRoute, { title: `${title}-${this.courseForm.id}` })
      this.$store.dispatch('tagsView/updateVisitedView', route)
    },
    setPageTitle() {
      const title = '编辑课程'
      document.title = `${title} - ${this.courseForm.id}`
    },
    submitForm() {
      this.$refs.courseForm.validate(valid => {
        if (valid) {
          this.loading = true
          const action = this.isEdit
            ? updateCourse(this.courseForm.id, this.courseForm)
            : createCourse(this.courseForm)

          action.then(() => {
            this.$notify({
              title: '成功',
              message: this.isEdit ? '课程更新成功' : '课程创建成功',
              type: 'success',
              duration: 2000
            })
            this.loading = false
            this.$router.push('/course/list') // 操作成功后跳转到课程列表页
          }).catch(() => {
            this.loading = false
          })
        }
      })
    },
    resetForm() {
      this.courseForm = Object.assign({}, defaultForm)
    }
  }
}
</script>

<style lang="scss" scoped>
@import "~@/styles/mixin.scss";
.createPost-main-container {
  /*
    这个容器现在是表单的一部分，我们可以给它一些内边距，
    比如上下 40px，左右 20px。
    或者，如果你觉得不需要这一层，可以直接移除它。
  */
  padding: 40px 20px;
  background-color: #fff; /* 给表单部分一个白色背景 */
  border-radius: 4px;
}
.createPost-container {
  position: relative;


}
</style>
