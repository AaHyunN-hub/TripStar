<template>
  <div class="auth-page">
    <div class="auth-card">
      <!-- Logo -->
      <div class="auth-header">
        <h1 class="auth-logo">TRIPSTAR</h1>
        <p class="auth-subtitle">{{ isLogin ? t('auth.loginTitle') : t('auth.registerTitle') }}</p>
      </div>

      <!-- 登录/注册表单 -->
      <a-form
        :model="formState"
        layout="vertical"
        @finish="handleSubmit"
        autocomplete="off"
      >
        <a-form-item
          :label="t('auth.username')"
          name="username"
          :rules="[{ required: true, message: t('auth.usernameRequired'), min: 2, max: 32 }]"
        >
          <a-input
            v-model:value="formState.username"
            :placeholder="t('auth.usernamePlaceholder')"
            size="large"
          >
            <template #prefix>
              <UserOutlined />
            </template>
          </a-input>
        </a-form-item>

        <a-form-item
          :label="t('auth.password')"
          name="password"
          :rules="[
            { required: true, message: t('auth.passwordRequired') },
            { min: 6, message: t('auth.passwordMin') }
          ]"
        >
          <a-input-password
            v-model:value="formState.password"
            :placeholder="t('auth.passwordPlaceholder')"
            size="large"
          >
            <template #prefix>
              <LockOutlined />
            </template>
          </a-input-password>
        </a-form-item>

        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            :loading="submitting"
            block
            size="large"
            class="auth-btn"
          >
            {{ isLogin ? t('auth.loginBtn') : t('auth.registerBtn') }}
          </a-button>
        </a-form-item>
      </a-form>

      <!-- 切换登录/注册 -->
      <div class="auth-footer">
        <span>{{ isLogin ? t('auth.noAccount') : t('auth.hasAccount') }}</span>
        <a-button type="link" @click="toggleMode">
          {{ isLogin ? t('auth.goRegister') : t('auth.goLogin') }}
        </a-button>
      </div>

      <!-- 错误提示 -->
      <a-alert
        v-if="errorMsg"
        :message="errorMsg"
        type="error"
        show-icon
        closable
        :after-close="() => errorMsg = ''"
        class="auth-error"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { login, register } from '@/services/api'

const router = useRouter()
const { t } = useI18n()

const isLogin = ref(true)
const submitting = ref(false)
const errorMsg = ref('')

const formState = reactive({
  username: '',
  password: '',
})

function toggleMode() {
  isLogin.value = !isLogin.value
  errorMsg.value = ''
  formState.username = ''
  formState.password = ''
}

async function handleSubmit() {
  submitting.value = true
  errorMsg.value = ''

  try {
    let result
    if (isLogin.value) {
      result = await login(formState.username, formState.password)
    } else {
      result = await register(formState.username, formState.password)
    }

    if (result.success && result.token) {
      // 保存 token 到 localStorage
      localStorage.setItem('tripstar.auth.token', result.token)
      localStorage.setItem('tripstar.auth.user', JSON.stringify(result.user))
      message.success(result.message)
      router.push('/')
    } else {
      errorMsg.value = result.message || t('auth.unknownError')
    }
  } catch (err: any) {
    errorMsg.value = err.response?.data?.detail || err.message || t('auth.unknownError')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3e 50%, #0d0d2b 100%);
  padding: 20px;
}

.auth-card {
  width: 400px;
  max-width: 100%;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 40px;
  position: relative;
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.auth-logo {
  font-family: 'Outfit', sans-serif;
  font-size: 32px;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 4px;
  margin: 0;
}

.auth-subtitle {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  margin-top: 8px;
}

.auth-btn {
  height: 44px;
  font-size: 16px;
  border-radius: 8px;
  margin-top: 8px;
}

.auth-footer {
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
}

.auth-error {
  margin-top: 16px;
  border-radius: 8px;
}

:deep(.ant-input-affix-wrapper) {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
}

:deep(.ant-input-affix-wrapper:hover) {
  border-color: #667eea;
}

:deep(.ant-input) {
  background: transparent;
  color: #fff;
}

:deep(.ant-input-prefix) {
  color: rgba(255, 255, 255, 0.4);
}

:deep(.ant-form-item-label > label) {
  color: rgba(255, 255, 255, 0.7);
}
</style>
