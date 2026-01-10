<template>
  <div class="createPost-container">
    <!-- 表单主体 -->
    <el-form ref="postForm" :model="postForm" :rules="rules" class="form-container">
      <!-- 顶部固定的操作栏 -->
      <sticky :z-index="10" :class-name="'sub-navbar '+postForm.status">
        <el-button v-loading="loading" style="margin-left: 10px;" type="success" @click="submitForm">
          {{ isEdit ? '更新' : '发布' }}
        </el-button>
        <el-button v-if="!isEdit" v-loading="loading" type="warning" @click="draftForm">
          存为草稿
        </el-button>
      </sticky>

      <!-- 表单内容区域 -->
      <div class="createPost-main-container">
        <el-row>
          <el-col :span="24">
            <!-- 作业标题输入框 -->
            <el-form-item style="margin-bottom: 40px;" prop="title">
              <MDinput v-model="postForm.title" :maxlength="100" name="name" required>
                作业标题
              </MDinput>
            </el-form-item>

            <!-- 课程和时间选择区域 -->
            <div class="postInfo-container">
              <el-row>
                <el-col :span="8">
                  <el-form-item label-width="90px" label="所属课程:" class="postInfo-container-item" prop="course_id">
                    <el-select v-model="postForm.course_id" filterable placeholder="请选择课程">
                      <el-option v-for="item in courseListOptions" :key="item.id" :label="item.name" :value="item.id" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="10">
                  <el-form-item label-width="120px" label="截止时间:" class="postInfo-container-item">
                    <el-date-picker v-model="postForm.display_time" type="datetime" format="yyyy-MM-dd HH:mm:ss" placeholder="选择日期和时间" />
                  </el-form-item>
                </el-col>
              </el-row>
            </div>
          </el-col>
        </el-row>

        <!-- 富文本编辑器 -->
        <el-form-item prop="content" style="margin-bottom: 30px;" label="作业内容:">
          <Tinymce ref="editor" v-model="postForm.content" :height="400" />
        </el-form-item>
      </div>
    </el-form>
  </div>
</template>

<script>
// 引入所需组件和API
import Tinymce from '@/components/Tinymce'
import MDinput from '@/components/MDinput'
import Sticky from '@/components/Sticky'
import { fetchAssignment, createAssignment, updateAssignment } from '@/api/assignment'
import { fetchCourseOptions } from '@/api/course'

// 默认表单数据结构
const defaultForm = {
  status: 'draft', // 状态, 'draft' 为草稿, 'published' 为已发布
  title: '', // 标题
  content: '', // 内容
  display_time: undefined, // 截止时间
  id: undefined, // 作业ID
  course_id: undefined // 课程ID
}

export default {
  name: 'AssignmentDetail',
  components: { Tinymce, MDinput, Sticky },
  props: {
    // 判断当前是 "编辑" 模式还是 "创建" 模式
    isEdit: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      postForm: Object.assign({}, defaultForm), // 表单数据
      loading: false, // 加载状态
      courseListOptions: [], // 课程下拉列表选项
      // 表单验证规则
      rules: {
        title: [{required: true, message: '标题不能为空', trigger: 'blur'}],
        content: [{required: true, message: '内容不能为空', trigger: 'blur'}],
        course_id: [{required: true, message: '必须选择一个课程', trigger: 'change'}]
      },
      tempRoute: {} // 用于存储路由信息，以更新tagsView
    }
  },
  // 组件创建时的生命周期钩子
  created() {
    // 如果是编辑模式，则根据路由中的id获取作业数据
    if (this.isEdit) {
      const id = this.$route.params.id
      this.fetchData(id)
    }
    // 获取所有课程的列表，用于下拉选择
    this.getCourseList()
    // 备份当前路由信息
    this.tempRoute = Object.assign({}, this.$route)
  },
  methods: {
    // 获取课程列表
    getCourseList() {
      fetchCourseOptions().then(response => {
        this.courseListOptions = response.data.items
      })
    },
    // 根据ID获取作业详情（仅编辑模式下调用）
    fetchData(id) {
      this.loading = true
      fetchAssignment(id).then(response => {
        this.postForm = response.data
        // 设置顶部标签页的标题
        this.setTagsViewTitle()
        // 设置浏览器窗口的标题
        this.setPageTitle()
        this.loading = false
      }).catch(err => {
        console.log(err)
        this.loading = false
      })
    },
    // 设置TagsView的标题
    setTagsViewTitle() {
      const title = '编辑作业'
      const route = Object.assign({}, this.tempRoute, {title: `${title}-${this.postForm.id}`})
      this.$store.dispatch('tagsView/updateVisitedView', route)
    },
    // 设置页面标题
    setPageTitle() {
      const title = '编辑作业'
      document.title = `${title} - ${this.postForm.id}`
    },
    // 提交表单（发布/更新）
    submitForm() {
      this.$refs.postForm.validate(valid => {
        if (valid) {
          this.loading = true
          // 根据 isEdit 标志决定是调用更新接口还是创建接口
          const action = this.isEdit ? updateAssignment(this.postForm.id, this.postForm) : createAssignment(this.postForm)

          action.then(() => {
            this.$notify({
              title: '成功',
              message: this.isEdit ? '作业更新成功' : '作业发布成功',
              type: 'success',
              duration: 2000
            })
            this.postForm.status = 'published' // 将状态标记为已发布
            this.loading = false
            // 操作成功后，跳转到作业列表页面
            this.$router.push('/assignment/list')
          }).catch(() => {
            this.loading = false
          })
        }
      })
    },
    // 存为草稿
    draftForm() {
      // 存为草稿时，状态就是默认的 'draft'，直接调用提交即可
      this.submitForm()
    }
  }
}
</script>

<style lang="scss" scoped>
// 样式部分保持不变，因为它们不包含面向用户的文本
@import "~@/styles/mixin.scss";

.createPost-container {
  position: relative;

  .createPost-main-container {
    padding: 40px 45px 20px 50px;

    .postInfo-container {
      position: relative;
      @include clearfix;
      margin-bottom: 10px;

      .postInfo-container-item {
        float: left;
      }
    }
  }

  .word-counter {
    width: 40px;
    position: absolute;
    right: 10px;
    top: 0px;
  }
}

.article-textarea ::v-deep {
  textarea {
    padding-right: 40px;
    resize: none;
    border: none;
    border-radius: 0px;
    border-bottom: 1px solid #bfcbd9;
  }
}
</style>
