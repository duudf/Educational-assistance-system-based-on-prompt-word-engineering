<template>
  <div class="createPost-container">
    <el-form ref="postForm" :model="postForm" :rules="rules" class="form-container">
      <sticky :z-index="10" :class-name="'sub-navbar '+postForm.status">
        <el-button v-loading="loading" style="margin-left: 10px;" type="success" @click="submitForm">
          {{ isEdit ? '更新' : '发布' }}
        </el-button>
        <el-button v-if="!isEdit" v-loading="loading" type="warning" @click="draftForm">
          存为草稿
        </el-button>
      </sticky>

      <div class="createPost-main-container">
        <el-row>
          <el-col :span="24">
            <el-form-item style="margin-bottom: 40px;" prop="title">
              <MDinput v-model="postForm.title" :maxlength="100" name="name" required>
                作业标题
              </MDinput>
            </el-form-item>
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

        <el-form-item prop="content" style="margin-bottom: 30px;" label="作业内容:">
          <Tinymce ref="editor" v-model="postForm.content" :height="400" />
        </el-form-item>
      </div>
    </el-form>
  </div>
</template>

<script>
import Tinymce from '@/components/Tinymce'
import MDinput from '@/components/MDinput'
import Sticky from '@/components/Sticky'
import { fetchAssignment, createAssignment, updateAssignment } from '@/api/assignment'
import { fetchCourseOptions } from '@/api/course'

const defaultForm = {
  status: 'draft',
  title: '',
  content: '',
  display_time: undefined,
  id: undefined,
  course_id: undefined
}

export default {
  name: 'AssignmentDetail',
  components: { Tinymce, MDinput, Sticky },
  props: {
    isEdit: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      postForm: Object.assign({}, defaultForm),
      loading: false,
      courseListOptions: [],
      rules: {
        title: [{ required: true, message: '标题不能为空', trigger: 'blur' }],
        content: [{ required: true, message: '内容不能为空', trigger: 'blur' }],
        course_id: [{ required: true, message: '必须选择一个课程', trigger: 'change' }]
      },
      tempRoute: {}
    }
  },
  created() {
    if (this.isEdit) {
      const id = this.$route.params.id
      this.fetchData(id)
    }
    this.getCourseList()
    this.tempRoute = Object.assign({}, this.$route)
  },
  methods: {
    getCourseList() {
      fetchCourseOptions().then(response => {
        this.courseListOptions = response.data.items
      })
    },
    fetchData(id) {
      this.loading = true
      fetchAssignment(id).then(response => {
        this.postForm = response.data
        this.setTagsViewTitle()
        this.setPageTitle()
        this.loading = false
      }).catch(err => {
        console.log(err)
        this.loading = false
      })
    },
    setTagsViewTitle() {
      const title = '编辑作业'
      const route = Object.assign({}, this.tempRoute, { title: `${title}-${this.postForm.id}` })
      this.$store.dispatch('tagsView/updateVisitedView', route)
    },
    setPageTitle() {
      const title = '编辑作业'
      document.title = `${title} - ${this.postForm.id}`
    },
    submitForm() {
      this.$refs.postForm.validate(valid => {
        if (valid) {
          this.loading = true
          const action = this.isEdit ? updateAssignment(this.postForm.id, this.postForm) : createAssignment(this.postForm)

          action.then(() => {
            this.$notify({
              title: '成功',
              message: this.isEdit ? '作业更新成功' : '作业发布成功',
              type: 'success',
              duration: 2000
            })
            this.postForm.status = 'published'
            this.loading = false
            this.$router.push('/course/list') // 假设你的课程/作业列表页路由是这个
          }).catch(() => {
            this.loading = false
          })
        }
      })
    },
    draftForm() {
      // 简化，草稿也直接提交
      this.submitForm()
    }
  }
}
</script>

<style lang="scss" scoped>
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
