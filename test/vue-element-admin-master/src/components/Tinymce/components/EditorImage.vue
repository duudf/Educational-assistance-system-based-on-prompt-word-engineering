<template>
  <div class="upload-container">
    <!-- 点击此按钮会弹出上传对话框 -->
    <el-button :style="{background:color,borderColor:color}" icon="el-icon-upload" size="mini" type="primary" @click=" dialogVisible=true">
      上传图片
    </el-button>

    <!-- 图片上传对话框 -->
    <el-dialog :visible.sync="dialogVisible">
      <el-upload
        :multiple="true"
        :file-list="fileList"
        :show-file-list="true"
        :on-remove="handleRemove"
        :on-success="handleSuccess"
        :before-upload="beforeUpload"
        class="editor-slide-upload"
        action="https://httpbin.org/post"
        list-type="picture-card"
      >
        <el-button size="small" type="primary">
          点击上传
        </el-button>
      </el-upload>
      <el-button @click="dialogVisible = false">
        取 消
      </el-button>
      <el-button type="primary" @click="handleSubmit">
        确 定
      </el-button>
    </el-dialog>
  </div>
</template>

<script>
// 这是一个用于编辑器（如 Tinymce）的图片上传组件

export default {
  name: 'EditorSlideUpload',
  props: {
    color: {
      type: String,
      default: '#1890ff'
    }
  },
  data() {
    return {
      dialogVisible: false, // 控制上传对话框的显示与隐藏
      listObj: {}, // 存储所有待上传或已上传文件的对象，键为文件 UID
      fileList: [] // el-upload 组件需要的文件列表，用于在界面上展示
    }
  },

  methods: {
    // 检查 listObj 中的所有文件是否都已上传成功
    checkAllSuccess() {
      // 使用 every 方法遍历 listObj 的所有键，并检查每个对象的 hasSuccess 属性是否为 true
      return Object.keys(this.listObj).every(item => this.listObj[item].hasSuccess)
    },
    // 处理“确定”按钮点击事件
    handleSubmit() {
      // 将 listObj 对象的值转换为数组
      const arr = Object.keys(this.listObj).map(v => this.listObj[v])
      // 检查是否所有图片都已成功上传
      if (!this.checkAllSuccess()) {
        this.$message('请等待所有图片上传成功！如果出现网络问题，请刷新页面重新上传。')
        return
      }
      // 触发父组件的 successCBK 事件，并传递已上传成功的图片信息数组
      this.$emit('successCBK', arr)
      // 操作完成后，清空数据
      this.listObj = {}
      this.fileList = []
      // 关闭对话框
      this.dialogVisible = false
    },
    // 文件上传成功后的回调函数
    handleSuccess(response, file) {
      const uid = file.uid // 获取文件的唯一标识 uid
      const objKeyArr = Object.keys(this.listObj)
      // 遍历 listObj 查找与上传成功文件 uid 相同的文件对象
      for (let i = 0, len = objKeyArr.length; i < len; i++) {
        if (this.listObj[objKeyArr[i]].uid === uid) {
          // 找到后，更新其 url 和 hasSuccess 状态
          // 注意：response.files.file 是由 action="https://httpbin.org/post" 的返回决定的，
          // 在实际项目中，你需要根据你的后端接口返回的数据结构来获取 url
          this.listObj[objKeyArr[i]].url = response.files.file
          this.listObj[objKeyArr[i]].hasSuccess = true
          return
        }
      }
    },
    // 文件列表移除时的钩子
    handleRemove(file) {
      const uid = file.uid
      const objKeyArr = Object.keys(this.listObj)
      // 同样通过 uid 找到 listObj 中的对应文件并删除
      for (let i = 0, len = objKeyArr.length; i < len; i++) {
        if (this.listObj[objKeyArr[i]].uid === uid) {
          delete this.listObj[objKeyArr[i]]
          return
        }
      }
    },
    // 上传文件之前的钩子，用于处理文件信息
    beforeUpload(file) {
      const _self = this
      const _URL = window.URL || window.webkitURL
      const fileName = file.uid
      // 在 listObj 中为即将上传的文件创建一个占位符
      this.listObj[fileName] = {}
      // 使用 Promise 来处理异步获取图片尺寸的操作
      return new Promise((resolve, reject) => {
        const img = new Image()
        img.src = _URL.createObjectURL(file)
        // 图片加载完成后，可以获取其真实的宽度和高度
        img.onload = function() {
          _self.listObj[fileName] = { hasSuccess: false, uid: file.uid, width: this.width, height: this.height }
        }
        // resolve(true) 表示校验通过，Element UI 会继续执行上传操作
        resolve(true)
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.editor-slide-upload {
  margin-bottom: 20px;
  ::v-deep .el-upload--picture-card {
    width: 100%;
  }
}
</style>
