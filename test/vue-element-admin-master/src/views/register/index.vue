<template>
  <div class="login-container">
    <el-form ref="registerForm" :model="registerForm" :rules="registerRules" class="login-form" autocomplete="on" label-position="left">

      <div class="title-container">
        <h3 class="title">系统注册</h3>
      </div>

      <el-form-item prop="username">
        <span class="svg-container">
          <svg-icon icon-class="user" />
        </span>
        <el-input
          ref="username"
          v-model="registerForm.username"
          placeholder="请输入用户名"
          name="username"
          type="text"
          tabindex="1"
          autocomplete="on"
        />
      </el-form-item>

      <el-form-item prop="password">
        <span class="svg-container">
          <svg-icon icon-class="password" />
        </span>
        <el-input
          ref="password"
          v-model="registerForm.password"
          :type="'password'"
          placeholder="请输入密码"
          name="password"
          tabindex="2"
          autocomplete="on"
        />
      </el-form-item>

      <el-form-item prop="role" class="role-selector">
        <el-radio-group v-model="registerForm.role">
          <el-radio label="student">我是学生</el-radio>
          <el-radio label="teacher">我是教师</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-button :loading="loading" type="primary" style="width:100%;margin-bottom:30px;" @click.prevent="handleRegister">注 册</el-button>

      <div style="text-align:right;">
        <router-link to="/login" class="link-to-login">
          已有账户？立即登录
        </router-link>
      </div>
    </el-form>
  </div>
</template>

<script>
import { register } from '@/api/user'

export default {
  name: 'Register',
  data() {
    const validatePassword = (rule, value, callback) => {
      if (value.length < 6) {
        callback(new Error('密码不能少于6位'))
      } else {
        callback()
      }
    }
    return {
      registerForm: {
        username: '',
        password: '',
        role: 'student'
      },
      registerRules: {
        username: [{ required: true, trigger: 'blur', message: '用户名是必填项' }],
        password: [{ required: true, trigger: 'blur', validator: validatePassword }],
        role: [{ required: true, message: '请选择您的角色', trigger: 'change' }]
      },
      loading: false
    }
  },
  methods: {
    handleRegister() {
      this.$refs.registerForm.validate(valid => {
        if (valid) {
          this.loading = true
          register(this.registerForm).then(() => {
            this.$message({
              message: '注册成功！',
              type: 'success'
            })
            this.loading = false
            this.$router.push({ path: '/login' })
          }).catch(error => {
            console.log(error)
            this.loading = false
          })
        } else {
          console.log('表单验证失败!!')
          return false
        }
      })
    }
  }
}
</script>

<!-- --- ↓↓↓ 从这里开始是正确的样式代码 ↓↓↓ --- -->

<style lang="scss">
/* 修复input 背景不协调 和光标变色 */
$bg:#283443;
$light_gray:#fff;
$cursor: #fff;

@supports (-webkit-mask: none) and (not (cater-color: $cursor)) {
  .login-container .el-input input {
    color: $cursor;
  }
}

/* 重置 element-ui css */
.login-container {
  .el-input {
    display: inline-block;
    height: 47px;
    width: 85%;

    input {
      background: transparent;
      border: 0px;
      -webkit-appearance: none;
      border-radius: 0px;
      padding: 12px 5px 12px 15px;
      color: $light_gray;
      height: 47px;
      caret-color: $cursor;

      &:-webkit-autofill {
        box-shadow: 0 0 0px 1000px $bg inset !important;
        -webkit-text-fill-color: $cursor !important;
      }
    }
  }

  .el-form-item {
    border: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(0, 0, 0, 0.1);
    border-radius: 5px;
    color: #454545;
  }
}
</style>

<style lang="scss" scoped>
$bg:#2d3a4b;
$dark_gray:#889aa4;
$light_gray:#eee;

.login-container {
  min-height: 100%;
  width: 100%;
  background-color: $bg;
  overflow: hidden;

  .login-form {
    position: relative;
    width: 520px;
    max-width: 100%;
    padding: 160px 35px 0;
    margin: 0 auto;
    overflow: hidden;
  }

  .svg-container {
    padding: 6px 5px 6px 15px;
    color: $dark_gray;
    vertical-align: middle;
    width: 30px;
    display: inline-block;
  }

  .title-container {
    position: relative;

    .title {
      font-size: 26px;
      color: $light_gray;
      margin: 0px auto 40px auto;
      text-align: center;
      font-weight: bold;
    }
  }

  .link-to-login {
    font-size: 14px;
    color: #fff;
    text-decoration: underline;
    cursor: pointer;
  }

  // 针对角色选择器的特殊样式
  .role-selector {
    border: none;
    background: none;
    margin-left: 10px; // 稍微调整一下位置
    ::v-deep .el-radio__label {
      color: #fff;
    }
  }
}
</style>
